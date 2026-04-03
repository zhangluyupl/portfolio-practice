---
name: minimax-image
description: |
  使用 MiniMax image-01 模型生成图片。用户给出一个图片主题或描述，技能负责优化提示词、调用 API、下载图片并通过微信发送给用户。

  触发场景：
  - 用户说"生成图片"、"画一张图"、"帮我生成"
  - 用户给出一个主题让我生成图片
  - 用户发送一个图片生成需求
---

# MiniMax 图片生成技能

## 核心流程

1. **接收用户需求** - 用户给出一个图片主题/描述/想法
2. **优化提示词** - 翻译成英文，增强细节和风格描述
3. **调用 API 生成** - 使用 image-01 模型
4. **下载并发送** - 通过 openclaw-weixin 发送给用户

## ⚠️ 生成前必查（后悔药机制）

**每次生成图片前，先强制检索 `~/self-improving/corrections.md`**，确认没有相关失败教训。如果有，在调用API之前先说出来或问清楚。

**检索关键词：** 当前任务的主体 + 风格 + 场景
- 例如"唱歌+国风" → 检索"图片"、"审美"、"国风"相关教训

---

## Step 1: 优化提示词

image-01 擅长真实摄影风格，中文描述需要转成英文。

**必须包含的要素：**
- 人物（如有）：动作、表情、服装
- 场景：具体环境、光线
- 风格：photorealistic, cinematic lighting 等
- 氛围：情绪、色调

**示例：**
- 用户说："妹子在唱歌"
  - 优化为：A beautiful young Chinese woman singing passionately into a microphone, emotional performance, warm stage lighting, photorealistic style
  
- 用户说："山水画"
  - 优化为：Misty mountains and flowing river, traditional Chinese ink painting style, serene landscape, soft morning light, photorealistic

## Step 2: 调用 API

**API 端点：** `POST https://api.minimaxi.com/v1/image_generation`

**请求头：**
```
Authorization: Bearer {MINIMAX_API_KEY}
Content-Type: application/json
```

**请求体：**
```json
{
  "model": "image-01",
  "prompt": "英文优化后的提示词",
  "aspect_ratio": "16:9",
  "response_format": "url",
  "n": 1
}
```

**API Key 获取：**
- 首先检查环境变量 `MINIMAX_API_KEY`
- 如果没有，检查 `~/.openclaw/workspace/skills/video-producer/.env` 文件
- 如果还没有，检查 `~/.openclaw/openclaw.json` 中的 `env.MINIMAX_API_KEY`

## Step 3: 下载图片

从响应中取 `data.image_urls[0]`，用 curl 下载到 `/tmp/img_gen/` 目录。

```bash
curl -s -o /tmp/img_gen/xxx.jpg "图片URL"
```

## Step 4: 发送微信

```bash
openclaw message send \
  --channel openclaw-weixin \
  --target "o9cq809eGr7RPqXvU6WWeqETSpKA@im.wechat" \
  --media "/tmp/img_gen/xxx.jpg" \
  --message "图片描述"
```

## 完整执行示例

```bash
# 1. 生成图片
curl -s -X POST "https://api.minimaxi.com/v1/image_generation" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "image-01",
    "prompt": "A serene mountain stream flowing through misty forest, photorealistic, natural lighting",
    "aspect_ratio": "16:9",
    "response_format": "url",
    "n": 1
  }'

# 2. 下载（假设返回URL为 https://example.com/image.jpg）
curl -s -o /tmp/img_gen/output.jpg "https://example.com/image.jpg"

# 3. 发送
openclaw message send --channel openclaw-weixin --target "o9cq809eGr7RPqXvU6WWeqETSpKA@im.wechat" --media "/tmp/img_gen/output.jpg" --message "🌄 山水意境"
```

## 注意事项

- 用户盲调 API，看不到生成结果，所以 prompt 优化很关键
- 默认 16:9 横版，如需竖版可用 "3:4"
- 如需中文元素融入图片，prompt 要明确写出 Chinese style, Hanfu, traditional Chinese 等
- 图片 URL 有时效，尽快下载发送

---

## 公众号/视频号内容风格（默认设置）

**封面图默认风格：anime/cartoon（卡通动漫风格）**
- clean lines, soft colors, high quality cartoon
- 人物：戴眼镜的程序员爸爸 + 传统文化元素（古籍、山水）
- 场景：温馨书房或现代家居

**公众号封面图（重要！）：**
- ⚠️ 宽高比：**21:9**（MiniMax API 不支持 2.35:1，用 21:9 ≈ 2.33:1）
- 推荐尺寸：900×383 px 或 1080×450 px（裁剪到 21:9 即可）
- 文件大小：≤ 5MB
- 格式：JPG/PNG

**公众号配图（文中插图）：**
- 风格：简约卡通 + 中国风元素
- 比例：3:4 竖版（公众号封面是 2.35:1，不要混淆）
- prompt 示例：
  ```
  A cute cartoon style Chinese programmer father with glasses, sitting at desk working on laptop, beside him traditional Chinese ancient philosophy books, warm cozy study room, anime style illustration, clean lines, soft colors, 3:4 vertical aspect ratio
  ```

**视频号封面：**
- 风格：真人感卡通 or 写实插画
- 比例：9:16 竖版
- 要体现内容主题（育儿/历史/程序员）
