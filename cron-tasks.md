# Cron 任务清单

> 更新日期：2026-03-30
> 位置：`~/.openclaw/workspace/cron-tasks.md`

## 每日任务（实际运行）

| 时间 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 08:30 | 晨间科技简报 | ✅ ok | isolated |
| 09:00 | 早安推送（天气+穿衣+诗词+每日一句） | cron | 通过 openclaw message send |
| 09:00 | IoT学习提醒 | ✅ ok | isolated |
| 09:30 | 晨间·凌晨进化汇报 | ✅ ok | isolated |
| 10:00 | 深度技术研究（React/Python） | ✅ ok | isolated，15min超时 |
| 14:00 | Claude Code 每日学习 | ✅ ok | isolated |
| 16:00 | OpenClaw 官方文档每日学习 | ✅ ok | isolated |
| 18:00 | 育儿推送（5岁男孩） | ✅ ok | isolated，120s超时 |
| 21:00 | 认知提纯 | ✅ ok | isolated |
| 22:00 | 记忆整理 | ✅ ok | isolated |
| 22:00 | 戒酒打卡 | ✅ ok | isolated |

## 每周任务

| 时间 | 任务 | 状态 |
|------|------|------|
| 周六 15:00 | 知识库内化 | ✅ ok |
| 周日 15:00 | 项目维护 | ✅ ok |

## 凌晨任务

| 时间 | 任务 | 状态 | 备注 |
|------|------|------|------|
| 0:00 | 凌晨·认知复盘 | ✅ 已修复 | 走完五步内化流程 |
| 0-4时每整点 | 凌晨·整点进化 | ✅ ok | isolated |
| 每小时 | 凌晨·知识深挖 | ✅ ok | isolated |

## ⚠️ 已知问题（已修复）

- **凌晨·认知复盘**：路径解析错误（曾尝试写入 memory/MEMORY.md），2026-03-30 已重建，路径明确写死为 `/Users/lydd/.openclaw/workspace/MEMORY.md`

## 配置备注

- 微信推送命令：`openclaw message send -c wechat -r o9cq809eGr7RPqXvU6WWeqETSpKA@im.wechat`
- IoT 学习项目：iot-backend (FastAPI 8000) + iot-frontend (React :5173)
- 早安推送内容：北京时间天气 + 穿衣建议 + 诗词 + 知识库每日一句
