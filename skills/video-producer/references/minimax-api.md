# MiniMax API 参考（Code Plan）

## 验证过的端点

| 能力 | 端点 | 模型 | 说明 |
|:---|:---|:---|:---|
| 文本对话 | POST `/v1/text/chatcompletion_v2` | M2-her | 无thinking |
| 语音合成 | POST `/v1/t2a_async_v2` + GET `/v1/query/t2a_async_query_v2?task_id=` | speech-2.8-hd | 异步，轮询 |
| 视频生成 | POST `/v1/video_generation` + GET `/v1/query/video_generation?task_id=` | MiniMax-Hailuo-2.3 | 异步 |
| 图片生成 | POST `/v1/image_generation` | image-01 | 同步，支持aspect_ratio |
| 文件下载 | GET `/v1/files/retrieve?file_id=` | - | 获取download_url |

## TTS 音色

可用 voice_id：
- `male-qn-qingse`（中文男声，推荐）
- `female-tianmei`（中文女声）

speed 参数可调（1.0=正常，2.0=最快）

## 图片参数

```json
{
  "model": "image-01",
  "prompt": "英文描述",
  "aspect_ratio": "16:9",
  "response_format": "url",
  "n": 1
}
```

## 已知问题

- M2-her 模型对复杂格式遵循不稳定，一次生成5段内容容易重复
- 解决方案：用5次独立调用代替一次生成多段
- image-01-live（支持中文图片嵌入）不在当前套餐内
