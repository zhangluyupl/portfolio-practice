# MEMORY.md — 长期记忆

## 用户基本信息
- 称呼：luyu
- 中国人，1989年生
- 出生于山东烟台，在北京工作
- 职业：程序员
- 有一个儿子，5岁左右（2021年生）
- 时区：Asia/Shanghai

## 已配置工具
- **微信推送**：openclaw message send，支持渠道 wechat，用户ID：o9cq809eGr7RPqXvU6WWeqETSpKA@im.wechat
- **GetNote 知识库**：已配置
  - **养育男孩**（EJXNdwZY，3条，已内化）：《你就是孩子最好的玩具》《何以为父》《养育男孩》
    - 内化：`learning/yangyu-nanhai/内化.md`
  - **个人认知**（BzJK82nl，20条）：道德经/道家哲学专辑（9条）+ 日常碎片
  - 内化：`learning/gerenzhizhang/内化.md`
  - 道家七品质（微妙玄通）、有无相生、反者道之动、儒道互补
- **万维钢读书**（d04xLrD0，共1680条笔记，实际拉取200条）：内容极混杂
  - 已内化：**梁宁·产品思维30讲**（28条）→ `learning/liangning/内化.md`
  - 已内化：**吴伯凡·孙子兵法**（28条）→ `learning/sunsi/核心框架.md`
  - 已内化：**武志红心理学**（75条）→ `learning/wuzhihong/内化.md`
  - 已内化：**财务报表分析**（37条）→ `learning/caiwu/内化.md`
  - `learning/wanweigang/` 含全部原始笔记和索引
- **天气**：wttr.in/Beijing

## 日常任务（Cron）
- **每日早安推送**：每天 18:00 执行，推送内容：北京时间天气+穿衣建议+一首诗词+知识库每日一句
  - cron key: d8988587-ffa0-46f1-9027-9957193806bb
  - 知识库"养育男孩"每日一句可从 GetNote 获取

## 学到的模式
- OpenClaw = 任务调度系统，复杂任务分"探索"和"收口"两轮
- 上下文要精简，避免 token 浪费
- 微信推送用 `openclaw message send -c wechat -r o9cq809eGr7RPqXvU6WWeqETSpKA@im.wechat`
