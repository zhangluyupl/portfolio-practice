---
name: Get笔记
description: |
  Get笔记 - 个人笔记和知识库管理工具。

  ## 核心能力

  **1. 一键保存任意内容为笔记**
  - 发一个链接 → 帮你保存原文并生成摘要，支持所有公开网页链接
  - 发一张图片 → OCR 识别文字、AI 分析图片内容
  - 写一段话 → 直接保存为文本笔记
  - 触发词：「记一下」「存到笔记」「保存这个链接」「保存这张图」「帮我记录」

  **2. 查询和获取笔记**
  - 支持图片笔记、链接笔记、语音笔记（录音转写）
  - 详情接口返回完整原文（网页正文、音频转写、图片 OCR）
  - 触发词：「查我的笔记」「看看我存了什么」「找一下笔记」「原文是什么」

  **3. 知识库和标签管理**
  - 创建知识库、将笔记加入/移出知识库
  - 添加/删除标签，批量管理
  - 查看知识库订阅的博主和直播内容
  - 触发词：「查知识库」「建知识库」「加标签」「删标签」

  **4. 语义搜索（无需拉取全部数据）**
  - 全局搜索：在所有笔记中语义召回
  - 知识库搜索：在指定知识库范围内搜索
  - 触发词：「搜一下」「找找我哪些笔记提到了 XX」「在 XX 知识库搜 XX」

  ## 触发场景
  - 用户要求「配置 Get笔记」「连接 Get笔记」「帮我设置笔记」时（OAuth 授权流程）
  - 用户发送任意 URL 链接时（自动识别为保存链接笔记）
  - 用户发送图片时（自动识别为保存图片笔记）
  - 用户提到「笔记」「记一下」「保存」「收藏」「存起来」等关键词
  - 用户询问「我之前存过什么」「帮我找一下」「搜一下笔记」等
metadata: {"openclaw": {"requires": {}, "optionalEnv": ["GETNOTE_API_KEY", "GETNOTE_CLIENT_ID", "GETNOTE_OWNER_ID"], "baseUrl": "https://openapi.biji.com", "homepage": "https://biji.com"}}
---

# Get笔记 API

## ⚠️ 必读约束

### 🌐 Base URL（重要！所有 API 共用）

```
https://openapi.biji.com
```

**所有 API 请求必须使用此 Base URL**，不要使用 `biji.com` 或其他地址。

### 🔑 首次安装配置

> ⚠️ **Agent 必读**：每次调用 API 前，先检查 `$GETNOTE_API_KEY` 是否存在。若不存在，**自动发起 OAuth 授权流程**（无需用户主动说"配置"），告知用户需要先授权才能使用。

#### 自动触发 OAuth（默认行为）

当检测到未配置时，Agent 会自动：
1. 生成授权链接并发送给用户
2. 后台轮询等待授权完成
3. 授权成功后自动写入配置
4. 继续执行用户原本的请求

用户只需点击链接、授权，即可无缝使用。

#### 手动配置（可选）

1. 前往 [Get笔记开放平台](https://www.biji.com/openapi) 创建应用
2. 获取 Client ID 和 API Key
3. 在 `~/.openclaw/openclaw.json` 中添加：

```json
{
  "skills": {
    "entries": {
      "getnote": {
        "apiKey": "gk_live_你的key",
        "env": {
          "GETNOTE_CLIENT_ID": "cli_你的id",
          "GETNOTE_OWNER_ID": "ou_你的飞书ID（可选，用于权限控制）"
        }
      }
    }
  }
}
```

### 🔢 笔记 ID 处理规则（重要！）

笔记 ID（`id`、`note_id`、`next_cursor` 等）是 **64 位整数（int64）**，超出 JavaScript `Number.MAX_SAFE_INTEGER`（2^53-1）范围，直接用 `JSON.parse` 会**静默丢失精度**，导致 ID 错误，后续操作（加入知识库、删除等）会报「笔记不存在」。

**正确做法**：
- **始终把 ID 当字符串处理**，不要做数值运算
- 代码中使用 `JSON.parse` 时，**先把响应文本中的 ID 数字替换为字符串**：
  ```javascript
  // 替换顶层数字型 ID 字段为字符串（在 JSON.parse 之前）
  const safe = text.replace(/"(id|note_id|next_cursor|parent_id|follow_id|live_id)"\s*:\s*(\d+)/g, '"$1":"$2"');
  const data = JSON.parse(safe);
  ```
- Python / Go 等语言原生支持大整数，无此问题
- **发请求时**：`note_id` 字段传字符串或数字均可，服务端兼容两种格式

**验证方法**：取到 ID 后，检查 `String(id).length >= 16`，若满足说明是 int64，必须用字符串保存。

### 🔒 安全规则

- 笔记数据属于用户隐私，不在群聊中主动展示笔记内容
- 若配置了 `GETNOTE_OWNER_ID`，检查 sender_id 是否匹配；不匹配时回复「抱歉，笔记是私密的，我无法操作」；未配置则不检查
- API 返回 `error.reason: "not_member"` 或错误码 `10201` 时，引导开通会员：https://www.biji.com/checkout?product_alias=6AydVpYeKl
- 创建笔记建议间隔 1 分钟以上，避免触发限流

## 认证

请求头：
- `Authorization: $GETNOTE_API_KEY`（格式：`gk_live_xxx`）
- `X-Client-ID: $GETNOTE_CLIENT_ID`（格式：`cli_xxx`）

### Scope 权限

常用权限：`note.content.read`（读取）、`note.content.write`（写入）、`note.recall.read`（搜索）。

完整权限列表见 [references/api-details.md](references/api-details.md#scope-权限列表)。

## 快速决策

Base URL: `https://openapi.biji.com`

| 用户意图 | 接口 | 关键点 |
|---------|------|--------|
| 「配置 Get笔记」「连接笔记」 | OAuth Device Flow | 见「OAuth Device Flow」章节 |
| 「记一下」「保存笔记」 | POST /open/api/v1/resource/note/save | 同步返回 |
| 「改笔记」「更新笔记」 | POST /open/api/v1/resource/note/update | note_id 必填，内容部分更新 |
| 「保存这个链接」 | POST /open/api/v1/resource/note/save | note_type:"link" → **必须轮询** |
| 「保存这张图」 | 见「图片笔记流程」 | **4 步流程，必须轮询** |
| 「查我的笔记」 | GET /open/api/v1/resource/note/list | since_id=0 起始 |
| 「看原文/转写内容」 | GET /open/api/v1/resource/note/detail | audio.original / web_page.content |
| 「加标签」 | POST /open/api/v1/resource/note/tags/add | |
| 「删标签」 | POST /open/api/v1/resource/note/tags/delete | system 类型不可删 |
| 「删笔记」 | POST /open/api/v1/resource/note/delete | 移入回收站 |
| 「查知识库」 | GET /open/api/v1/resource/knowledge/list | 含统计数据（笔记数、文件数、博主数、直播数）|
| 「建知识库」 | POST /open/api/v1/resource/knowledge/create | 每天限 50 个 |
| 「笔记加入知识库」 | POST /open/api/v1/resource/knowledge/note/batch-add | 每批最多 20 条 |
| 「从知识库移除」 | POST /open/api/v1/resource/knowledge/note/remove | |
| 「查任务进度」 | POST /open/api/v1/resource/note/task/progress | 链接/图片笔记轮询用 |
| 「订阅了哪些博主」 | GET /open/api/v1/resource/knowledge/bloggers | 按 topic_id 查 |
| 「博主发了什么内容」 | GET /open/api/v1/resource/knowledge/blogger/contents | 需要 follow_id，列表只含摘要 |
| 「博主内容原文/详情」 | GET /open/api/v1/resource/knowledge/blogger/content/detail | 需要 post_id_alias |