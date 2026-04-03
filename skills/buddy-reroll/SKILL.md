# buddy-reroll Skill

清理 Claude Code buddy 并 reroll，直到出金色传说。

## 已知限制

- any-buddy 需要 bun/npm 安装，在 OpenClaw exec 环境里网络超时
- **reroll 必须在你自己终端里做**，我只能帮你清理 companion

## 手动操作步骤（你自己终端跑）

```bash
# 第一步：清除旧 buddy
# 打开 ~/.claude.json，删除 "companion": {...} 这段，保存

# 第二步：抽新 buddy
claude
# 进入后输入
/buddy
# 看结果，不满意就 Ctrl+C 退出，重复第一步+第二步
```

## 我能帮你做的

1. 清除 companion 字段（直接执行）
2. 检查 ~/.claude.json 里的 userID（用于算传说 seed）

## 调用方式

```
/buddy-reroll clear    # 清除 companion
/buddy-reroll status   # 查看当前 buddy 状态
/buddy-reroll open     # 打开 ~/.claude.json 让你编辑
```
