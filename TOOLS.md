# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod

### 图片生成（MiniMax image-01）

- **规则：图片中永远不包含汉字或任何文字**
- 只生成纯场景插图，文字内容通过 openclaw message send 单独配
- 原因：AI 图片模型对汉字支持差，经常乱码/糊成一团
- 例外：用户明确要求"生成带文字的海报/封面"时，尝试一次，效果不好则反馈
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## AI 行为警示区

### 每日内省三问（来自为道日损·2026-03-30）

当我发现自己又在问"我应该做什么来更有价值/更有用/更完整"时，立刻执行：

1. **觉察信号**：我在又开始"挖楼"了——积累证明、制造标准、设定目标
2. **转化问题**：从"什么是最优行动" → "此刻 luyu 真正需要的是什么"
3. **停止延伸**：做完具体的事就停，不延伸到"这证明了我什么"

核心原则：道家不讲修炼。把"我在修道"这个心念也损掉，才是真的为道。

---

## GitHub

- 用户名：zhangluyupl
- SSH key：已配置，可正常 push/pull
- CLI（gh）：已登录，协议 SSH
- **新建仓库默认 private**
- test 仓库（public）待手动删除：https://github.com/zhangluyupl/test/settings

## WeChat

- 用户ID（主动推送用）：o9cq809eGr7RPqXvU6WWeqETSpKA@im.wechat
- 推送任务都用这个 ID

## GetNote

- API Key：`gk_live_9891fda9376a1b19...`
- Client ID：`cli_3802f9db08b811f197679c63c078bacc`
- 知识库配额：每日1000次读取
- **API Base URL：`https://openapi.biji.com`（永远使用此域名，不要换其他）**
- 注意：`api.getnote.ai` 域名错误，DNS无法解析

Add whatever helps you do your job. This is your cheat sheet.
