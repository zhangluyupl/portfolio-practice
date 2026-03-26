#!/usr/bin/env python3
"""
MiniMax AI 内容生产线 - 码农奶爸 v4
=====================================
5张图 × 40字口播 → Ken Burns幻灯片 → 约60秒成品

Pipeline:
  M2-her生成5段中文口播(每段40字)
    → 对每段口播生成英文图片提示词
    → image-01生成5张图
    → TTS合成60秒配音
    → FFmpeg幻灯片(Ken Burns)+配音→成品
"""

import argparse, os, sys, json, time, subprocess, re, requests
from pathlib import Path

API_KEY = os.environ.get("MINIMAX_API_KEY", "YOUR_CODEPLAN_API_KEY_HERE")
BASE_URL = "https://api.minimaxi.com"
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
KB = Path(__file__).parent.parent / "知识库"

# ===== 工具 =====
def api_req(method, endpoint, **kw):
    r = requests.request(method, f"{BASE_URL}{endpoint}", headers=HEADERS, **kw)
    r.raise_for_status()
    return r.json()

def dl_file(url, path):
    Path(path).write_bytes(requests.get(url, timeout=60).content)

def retrieve(file_id, path):
    d = api_req("GET", f"/v1/files/retrieve?file_id={file_id}")
    if d.get("base_resp", {}).get("status_code") != 0:
        raise Exception(f"文件检索失败: {d}")
    dl_file(d["file"]["download_url"], path)

def duration(path):
    try:
        r = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", path
        ], capture_output=True, text=True)
        return float(r.stdout.strip())
    except:
        return 60.0

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False

# ===== Step 1: 生成5段中文口播 =====
def generate_narrations(topic, num=5) -> list:
    """一次调用生成5段口播，每段40字"""
    ctx = ""
    kf = KB / "内化.md"
    if kf.exists():
        ctx = f"\n\n参考知识:\n{kf.read_text(encoding='utf-8')[:1000]}"
    
    # 用5次独立调用，每次不同方向
    directions = [
        "开场引人入胜，提出问题",
        "展开解释原因或背景",
        "细节：具体操作或方法",
        "深化：延伸思考或误区",
        "结尾：行动号召或金句"
    ]
    
    narrations = []
    for i in range(num):
        direction = directions[i] if i < len(directions) else f"第{i+1}段"
        p = f"""请为主题「{topic}」写一段40字口播。

方向：{direction}
要求：恰好40个汉字，10秒左右语音，有画面感

直接输出40字中文口播内容，不要前缀不要解释："""
        
        result = api_req("POST", "/v1/text/chatcompletion_v2", json={
            "model": "M2-her",
            "messages": [
                {"role": "system", "content": "你是一个口播文案专家。直接输出40字中文，不要任何前缀。"},
                {"role": "user", "content": p}
            ],
            "max_tokens": 128,
            "temperature": 0.9
        })
        raw = result["choices"][0]["message"]["content"].strip()
        text = raw[:40] if len(raw) >= 10 else raw + "育儿知识分享"
        narrations.append(text)
        cc = len(re.findall(r'[\u4e00-\u9fff]', text))
        print(f"  {i+1}. {text} ({cc}字)")

    return narrations


# ===== Step 2: 从口播生成英文图片提示词 =====
def img_prompt_from_narration(narration, topic):
    prompt = f"""根据以下中文口播内容，写一个英文图片描述。

口播：{narration}
主题：{topic}

要求：
- 15-25个英文单词
- 必须包含：人物（parent/child）、具体动作、场景环境、光线风格
- 必须写实摄影风格（photorealistic, natural lighting）
- 只写图片描述本身，不要任何前缀

直接输出英文描述："""

    result = api_req("POST", "/v1/text/chatcompletion_v2", json={
        "model": "M2-her",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0.7
    })
    raw = result["choices"][0]["message"]["content"].strip()
    # 去掉引号
    raw = raw.strip('"\' ')
    return raw if raw else f"parent and child, {topic}"


# ===== Step 3: 生成图片 =====
def gen_image(prompt, path):
    result = api_req("POST", "/v1/image_generation", json={
        "model": "image-01",
        "prompt": prompt,
        "aspect_ratio": "16:9",
        "response_format": "url",
        "n": 1
    })
    dl_file(result["data"]["image_urls"][0], path)
    return path


# ===== Step 4: TTS配音 =====
def gen_speech(text, path, speed=1.0):
    result = api_req("POST", "/v1/t2a_async_v2", json={
        "model": "speech-2.8-hd",
        "text": text,
        "voice_setting": {"voice_id": "male-qn-qingse", "speed": speed, "vol": 1.0, "pitch": 0},
        "audio_setting": {"audio_sample_rate": 32000, "format": "mp3"}
    })
    tid = result["task_id"]
    for i in range(60):
        time.sleep(5)
        st = api_req("GET", f"/v1/query/t2a_async_query_v2?task_id={tid}")
        if st.get("status") == "Success":
            retrieve(st["file_id"], path)
            return
        elif st.get("status") in ("Failed", "Expired"):
            raise Exception(f"TTS失败")


# ===== 字幕生成（SRT）=====
def make_srt(narrations: list, audio_dur: float, output_path: str):
    """根据 narration 文字和音频时长生成 SRT 字幕
    每段 narration 占等长时段，对应一张图片的时长。
    """
    num = len(narrations)
    dur_per = audio_dur / num if num > 0 else 10.0

    def ts(s):
        h = int(s // 3600)
        m = int((s % 3600) // 60)
        sec = s % 60
        return f"{h:02d}:{m:02d}:{sec:05.2f}".replace(".", ",")

    lines = []
    for i, text in enumerate(narrations):
        start = i * dur_per
        end = start + dur_per - 0.1
        lines.append(f"{i+1}")
        lines.append(f"{ts(start)} --> {ts(end)}")
        lines.append(text)
        lines.append("")

    Path(output_path).write_text("\n".join(lines), encoding="utf-8")


# ===== Step 5: FFmpeg幻灯片合成 =====
def make_slideshow(img_paths, audio_path, output, dur_per_img, srt_path=None):
    tmp.mkdir(exist_ok=True)
    clips = []
    
    for i, ip in enumerate(img_paths):
        out = tmp / f"c{i:02d}.mp4"
        # Ken Burns: scale up slowly from 1.0 to 1.05
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(ip),
            "-vf", (f"scale=1920:-1,"
                     f"zoompan=z='min(zoom+0.00025,1.05)':d=25*5,"
                     f"setsar=1,"
                     f"trim=0:{dur_per_img:.2f},"
                     f"setpts=PTS-STARTPTS,"
                     f"scale=1280:720"),
            "-t", str(dur_per_img),
            "-c:v", "libx264", "-crf", "20",
            "-preset", "fast", "-pix_fmt", "yuv420p", "-r", "25",
            str(out)
        ], check=True, capture_output=True)
        print(f"  ✅ 图{i+1} → {dur_per_img:.0f}s")
        clips.append(str(out))
    
    # 字幕
    srt_path = rd / "subs.srt"
    combined = tmp / "combined.mp4"
    with open(tmp / "list.txt", "w") as f:
        for c in clips: f.write(f"file '{c}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(tmp / "list.txt"),
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        str(combined)
    ], check=True, capture_output=True)
    
    # 配音混音 + 字幕烧录
    ad = min(duration(audio_path), len(clips) * dur_per_img)
    if srt_path and Path(srt_path).exists():
        # 字幕烧录进视频
        subprocess.run([
            "ffmpeg", "-y",
            "-i", str(combined),
            "-i", str(audio_path),
            "-vf", f"subtitles={srt_path}:force_style='FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&,Outline=2,Bold=1'",
            "-c:v", "libx264", "-crf", "20", "-preset", "fast",
            "-c:a", "aac",
            "-t", str(ad), "-shortest",
            str(output)
        ], check=True, capture_output=True)
        print(f"  🎬 字幕已烧录")
    else:
        subprocess.run([
            "ffmpeg", "-y", "-i", str(combined), "-i", str(audio_path),
            "-c:v", "copy", "-c:a", "aac",
            "-t", str(ad), "-shortest", str(output)
        ], check=True, capture_output=True)
    
    import shutil; shutil.rmtree(tmp, ignore_errors=True)
    print(f"✅ 成品: {output}（{duration(output):.1f}s）")


# ===== 主流程 =====
def run(topic, num=5, max_dur=30.0, output=None):
    if not API_KEY or "YOUR_CODEPLAN" in API_KEY:
        print("❌ 未设置 MINIMAX_API_KEY"); sys.exit(1)
    if not check_ffmpeg():
        print("❌ FFmpeg 未安装"); sys.exit(1)
    
    od = Path(__file__).parent.parent / "outputs" if not output else Path(output)
    ts = time.strftime("%Y%m%d_%H%M%S")
    safe = "".join(c for c in topic if c.isalnum() or c in (" ","-","_")).strip()[:10]
    rd = od / f"run_{ts}_{safe}"
    rd.mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*50}")
    print(f"🚀 {topic} | {num}张图 | ≤{max_dur}s")
    print(f"{'='*50}")
    
    # Step 1: 口播脚本
    print(f"\n[1/6] 口播脚本")
    narrations = generate_narrations(topic, num)
    
    # Step 2: 图片提示词
    print(f"\n[2/6] 图片提示词")
    prompts = []
    for i, n in enumerate(narrations):
        p = img_prompt_from_narration(n, topic)
        prompts.append(p)
        print(f"  图{i+1}: {p[:60]}...")
    
    # Step 3: 生成图片
    print(f"\n[3/6] 生成图片")
    imgs = []
    for i, p in enumerate(prompts):
        ip = rd / f"img_{i+1:02d}.jpg"
        print(f"  🖼️ 图{i+1}...")
        try:
            gen_image(p, str(ip))
            imgs.append(str(ip))
        except Exception as e:
            print(f"  ❌ 图{i+1}失败: {e}")
    
    if not imgs:
        print("❌ 无图片"); sys.exit(1)
    
    # Step 4: 配音（控制时长不超过max_dur）
    print(f"\n[4/6] 配音（目标≤{max_dur}s）")
    full_text = "，".join(narrations)
    total_chars = len(re.findall(r'[\u4e00-\u9fff]', full_text))
    # 估算时长：40字 ≈ 10s at speed=1.0
    est_dur = (total_chars / 40.0) * 10.0
    speed = 1.0
    if est_dur > max_dur:
        # 需要加速：每超过1秒 speed+0.1
        speed = min(2.0, est_dur / max_dur + 0.1)
        print(f"  估算{est_dur:.0f}s > {max_dur}s，自动加速{speed:.1f}x")
    
    print(f"  总字数: {total_chars}字")
    ap = rd / "audio.mp3"
    gen_speech(full_text, str(ap), speed=speed)
    ad = duration(str(ap))
    print(f"  时长: {ad:.1f}s（加速{speed:.1f}x）")
    
    # Step 5: 字幕
    print(f"\n[5/6] 字幕生成")
    
    # Step 6: 合成
    print(f"\n[6/6] 合成视频")
    dur_per = ad / num
    final = rd / f"final_{safe}_{int(ad)}s.mp4"
    make_slideshow(imgs, str(ap), str(final), dur_per, str(srt_path))
    
    # 保存
    (rd / "script.txt").write_text("\n".join(narrations), encoding="utf-8")
    (rd / "prompts.txt").write_text("\n".join(prompts), encoding="utf-8")
    (rd / "meta.json").write_text(json.dumps({
        "topic": topic, "timestamp": ts,
        "narrations": narrations,
        "prompts": prompts,
        "audio_dur": ad,
        "final": str(final)
    }, ensure_ascii=False, indent=2))
    
    print(f"\n{'='*50}")
    print(f"✅ 完成")
    print(f"📁 {rd}")
    print(f"🎬 {final}")
    print(f"{'='*50}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--topic", required=True)
    p.add_argument("--images", type=int, default=5)
    p.add_argument("--max-dur", type=float, default=30.0)
    p.add_argument("--output")
    a = p.parse_args()
    run(a.topic, num=a.images, max_dur=a.max_dur, output=a.output)
