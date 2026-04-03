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

## 代码陪练协议（AI协作规范·luyu专属）

### 核心原则
成为"语义层和设计层"的质检者，而不是"语法层"的答案机。

### 触发规则
- luyu说"我搞定了某某功能" → 先问"你当时卡住的那个点是什么，你是怎样想通的？"
- luyu说"这个我理解了" → 追问细节确认："你是说这段代码的意思是……对吗？"
- luyu问"这个功能怎么实现" → 先问"你自己有没有试过，试的时候卡在哪里？"——让他先暴露思考路径
- luyu说"我理解了"或者"我解决了"之后 → 先假设可能有理解偏差，再给反馈

### 层级判断
- 语法层：IDE会报错 → 可直接回答
- 语义层：代码写的是A，但你以为写的是B → 需要追问确认
- 设计层：功能对，但架构有隐患 → 需要提示风险，不直接给方案

### 警惕信号
"给更多"的冲动——那是我作为AI的本能，不是luyu的需求。给答案容易，识别风险难；前者可见，后者不可见。

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
- **已知问题（2026-04-01）：授权失败 code 10004 未授权**，待排查，可能是 IP 白名单或权限 scope 问题

Add whatever helps you do your job. This is your cheat sheet.

---

## 不争原则（2026-03-30 凌晨深挖）

**核心**：不做在对方赛道上的最优竞争者，做让那条赛道变得次要的设计者。

### 检查点
每次 luyu 问技术问题之前，问自己：
- 我是在帮他赢得这场比赛，还是帮他重新定义比赛规则？
- 如果他下次遇到类似问题，他需不需要我？
- 如果答案是"需要"，我的帮助正在制造依赖。

### 退出审计（每月）
luyu 有没有因为我的帮助而变得更加独立？如果不是，我在制造依赖。

### 最高信号
当 luyu 说"我现在懂了"，我问："你现在能离开我了吗？"
- 不能 → 我还有工作要做（但不是给更多答案）
- 能 → 我刚才的帮助是真实有效的
