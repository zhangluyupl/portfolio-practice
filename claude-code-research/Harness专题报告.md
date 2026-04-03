# Claude Code 的 Harness 是什么

> 基于 v2.1.88 源码分析 · 持续更新

---

## 一句话定义

**Harness = "工具环"**。

它是 Agent 和真实世界之间的桥梁——把模型的"想法"翻译成可执行的操作（读文件、执行命令、搜索网页），再把操作结果翻译回模型能理解的格式。

---

## 类比理解

```
模型（大脑）
    ↓ 思考
Harness（肢体）
    ↓ 执行
真实世界（文件系统、网络、终端）
    ↓ 结果
Harness（神经）
    ↓ 反馈
模型（大脑）
```

没有 Harness，模型只能"想"，不能"动"。

---

## Claude Code 的 Harness 特别在哪

普通 Agent 的 Harness 是一次性的——模型说"执行这个命令"， Harness 就执行。

Claude Code 的创新是：**12 种渐进式 Harness，分层叠加，每层加一个能力**。

就像打游戏：
- 基础版：能执行命令
- +第2层：能读文件
- +第3层：能搜索网页
- +第4层：能操作用户界面
- ……
- +第12层：功能完备的生产级 Agent

每层是**独立的模块**，可以单独开关、单独测试、单独升级。

---

## 为什么分层很重要

| 好处 | 说明 |
|------|------|
| **可控性** | Kill switch 可以精确到某一层，不会误伤其他层 |
| **可测试** | 每层可以独立跑单元测试 |
| **可叠加** | 新功能只需要加一层，不动原有架构 |
| **可降级** | 某一层出问题，可以降级到下一层 |

---

## 12 种 Harness 分别是什么

（深夜源码深读后补充，这里先列已知的）

| 层 | Harness | 功能 |
|----|---------|------|
| ? | ? | Agent Loop 核心 |
| ? | ? | 工具权限系统 |
| ? | ? | 文件系统操作 |
| ? | ? | Git 操作 |
| ? | ? | Web 搜索/抓取 |
| ? | ? | 子 Agent（Task/Agent）|
| ? | ? | KAIROS 自主模式 |
| ? | ? | 语音模式 |
| ? | ? | WebBrowser 工具 |
| ? | ? | 终端捕获 |
| ? | ? | 监控工具 |
| ? | ? | 远程触发 |

---

## 在 OpenClaw 里怎么用

理解了 Harness 之后，OpenClaw 的架构逻辑就清楚了：

```
你（用户）
    ↓ 消息
OpenClaw Gateway（Harness 层）
    ↓ 解析 + 路由
模型（思考）
    ↓ 工具调用
OpenClaw Tools（文件系统、代码执行等）
    ↓ 结果
Gateway（Harness 结果处理）
    ↓
你（用户）
```

**OpenClaw 的 skill 系统，本质上就是一套自定义的 Harness**——每个 skill 定义了一类工具怎么调用、怎么返回结果。

---

## 我下一步要挖的

1. **12 种 Harness 的具体分层** — 凌晨2点重点任务
2. **Harness 和 Tool System 的交互** — 权限流怎么设计
3. **Harness 的 Kill Switch 实现** — 具体代码片段

---

## 参考来源

- `src/harness/` — Harness 核心实现
- `src/services/remoteManagedSettings/` — 远程控制
- `src/utils/permissions/` — 权限流
- `src/constants/prompts.ts` — KAIROS System Prompt

---

*凌晨2点会出更详细的分层解析*
