---
name: video-producer
description: |
  AI视频制作技能。根据用户输入的主题，自动生成5张图×口播的短视频（幻灯片+配音）。
  
  使用场景：
  - 用户说"帮我制作一个视频"、"生成一个视频"、"做个育儿视频"
  - 用户说"根据这个主题生成视频内容"
  - 用户说"帮我拍视频"、"做个短视频"
  - 用户提供了主题，想生成对应的视频素材
  
  当用户想要制作短视频、育儿内容、或提到视频+主题相关需求时，优先触发此技能。
  
  此技能不限于育儿场景，任何主题均可。
  
  注意：如果用户想要的是视频编辑（如替换片段、调整顺序），使用edit命令。
---

# Video Producer

用 MiniMax API 从主题生成短视频（幻灯片+配音）。

## 核心流程

```
用户主题 → M2-her生成5段口播(每段40字)
         → 每段口播生成英文图片描述
         → image-01生成5张图
         → TTS合成配音
         → FFmpeg幻灯片(Ken Burns效果)+配音→成品
```

## 环境要求

- Python 3 + `requests` 库
- FFmpeg（Mac: `brew install ffmpeg`）
- MiniMax API Key（Code Plan套餐）

## 快速使用

```bash
# 基本用法（5张图，≤30秒）
python3 scripts/production_pipeline.py --topic "5岁男孩发脾气怎么办"

# 指定图片数量和最大时长
python3 scripts/production_pipeline.py --topic "育儿" --images 3 --max-dur 20

# 指定输出目录
python3 scripts/production_pipeline.py --topic "主题" --output /path/to/output
```

## 参数说明

| 参数 | 默认值 | 说明 |
|:---|:---|:---|
| `--topic` | 必填 | 视频主题 |
| `--images` | 5 | 图片数量（建议3-5张） |
| `--max-dur` | 30.0 | 最大时长（秒），配音会自动加速 |
| `--output` | outputs/ | 输出目录 |

## 输出结构

```
outputs/run_YYYYMMDD_HHMMSS_主题/
├── script.txt          # 原始口播脚本
├── prompts.txt         # 英文图片提示词
├── img_01.jpg ~ img_05.jpg  # 生成的图片
├── audio.mp3           # 配音
├── meta.json           # 元数据
└── final_主题_时长s.mp4  # 成品视频
```

## 视频编辑命令

生成完视频后，如果用户想要：
- **调整时长**：用 `--max-dur` 重新生成
- **换主题**：直接指定新主题
- **修改口播内容**：告诉用户具体想改什么，重新生成

## API Key 配置

如果还没配置过 MiniMax API Key：

1. 在 MiniMax 开放平台获取 Code Plan 的 API Key
2. 运行时通过环境变量注入：
   ```bash
   export MINIMAX_API_KEY="你的key"
   python3 scripts/production_pipeline.py --topic "你的主题"
   ```

## 常见问题

**配音太长/太短？**
- 调整 `--max-dur` 参数，系统会自动加速或减速配音

**想要更短的视频？**
- 减少 `--images` 数量（如 `--images 3`）
- 或降低 `--max-dur`（如 `--max-dur 15`）

**成品在哪里？**
- 默认在 `outputs/` 目录下，按时间戳组织
- 告诉用户具体路径

**API报错？**
- 检查 MINIMAX_API_KEY 是否正确
- 检查网络连接
- 确认 Code Plan 套餐额度充足
