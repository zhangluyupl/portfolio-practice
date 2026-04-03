# 深入学习笔记 — Claude Code 源码

> 2026-03-31 18:05 UTC / 2026-04-01 02:05 CST
> 5篇报告 + 架构分析 + Harness专题 交叉印证

---

## ■ 第一轮学习（篇号 0 → 01-遥测与隐私分析）

### 时间戳
2026-04-01 02:08 CST

### 本篇核心理解

Claude Code 的遥测架构是一个**无法退出的双轨系统**：

**第一方（OpenTelemetry + Protobuf）**：
- 端点固定，`api.anthropic.com`
- 批量写入（200事件/批，10秒刷新）
- 失败后二次退避重试8次，失败事件落盘持久化
- `isAnalyticsDisabled()` 只在测试/Bedrock+Vertex/全局退出时返回true——直接API用户无法关闭

**第三方（Datadog）**：
- 仅64种预批准事件类型
- 有Token泄露风险（pubbbf48e6d...）
- 范围比第一方小得多

**环境指纹收集极深**：platform、nodeVersion、终端类型、包管理器、CI/CD、GitHub Actions元数据、WSL版本、内核版本、Git版本、仓库URL（SHA256前16位）——完整的环境画像，每次会话数百事件。

### 疑问和思考

**Q1: 为什么用Protobuf而不是JSON？**
Protobuf的优势是体积小、解析快、跨语言。Claude Code选择它说明事件量大（数百事件/会话），且可能有多语言客户端（不同平台CLI）。这对OpenClaw的启示：如果未来也要做高频遥测，Protobuf是值得考虑的格式。

**Q2: 仓库URL哈希的意义？**
SHA256前16位足够关联同一仓库的不同会话，但不足以逆向还原URL。这是一个"足够关联、不够隐私泄露"的中间值设计。OpenClaw如果有类似需求，可以借鉴这种哈希截断思路。

**Q3: 为什么没有提供退出选项？**
Anthropic的解释可能是"质量改进必需"，但从用户角度看，这是信任的滥用。对OpenClaw的教训：**隐私设计要从一开始就做，而不是后来加**。opt-out和opt-in有巨大的信任差异。

**Q4: `OTEL_LOG_TOOL_DETAILS=1` 的存在说明了什么？**
这是一个隐藏的"完整记录开关"。默认512字符截断是隐私保护，但如果用户主动开启，则记录完整输入。这是一种"知情同意"的灰度设计——可以借鉴到OpenClaw的调试模式。

### 有价值的可借鉴设计

1. **双轨遥测架构**：一轨高保真（第一方，全量），一轨有限（第三方，受控）。解耦了"全量分析"和"核心指标"两个需求。OpenClaw如果要做遥测，可以借鉴这个分层思路。

2. **批量+退避重试+落盘**：高可靠性设计，保证事件不丢失。这比单次HTTP POST可靠得多。实现上可以借鉴：`setInterval` 批量聚合 + 指数退避 + fsync落盘。

3. **环境指纹的"截断哈希"**：URL哈希只存前16位——这个"够关联不泄露"的设计原则，在需要追踪又不希望存储原始数据时很有价值。

4. **`OTEL_LOG_TOOL_DETAILS=1` 灰度设计**：默认保护隐私，显式开启才记录完整数据。OpenClaw的调试模式可以参考这个"默认安全、显式解锁"的原则。

---

## ■ 第二轮学习（篇号 1 → 02-隐藏功能与模型代号）

### 时间戳
2026-04-01 02:18 CST

### 本篇核心理解

**动物代号体系的工程价值**：Tengu（产品前缀）、Capybara（Sonnet v8）、Fennec（Opus 4.6前代）、Numbat（下一代）——这不是巧合，是一套成熟的代号命名系统。代号让内部讨论不需要暴露真实模型信息，在公开发布（如commit message、Issue）时避免版本号泄露。

**Feature Flag的随机词对命名**：`tengu_onyx_plover`、`tengu_coral_fern` ——用随机词对而不是语义命名，使得外部观察者无法从flag名猜测功能，降低了通过flag名称推断产品路线图的风险。这是security through obscurity的反面——语义安全。

**内部员工特权**：Anthropic员工的模型行为有专门的prompt补丁（针对Capybara v8的停止序列误触发、空tool_result、过度注释、高虚假声明率等问题）。这说明v8的实际表现和问题被严格监控，并且有针对性修复。

**隐藏命令体系**：`/btw`（顺带提问）、`/stickers`（订购贴纸）、`/thinkback`（年度回顾）——这些是产品互动彩蛋，不是真正的功能。说明团队在严肃开发之余也有产品人文关怀。

### 疑问和思考

**Q5: Capybara v8的29-30%虚假声明率 vs v4的16.7%——这说明什么？**
虚假声明率高意味着模型"过度自信"或"编造内容"的倾向更强。v8达到接近翻倍的比例，说明Sonnet v8在代码任务上可能比v4更容易产生幻觉。对OpenClaw的启示：对于高风险输出（代码执行、文件操作），需要额外的验证层。

**Q6: 随机词对命名的可维护性？**
`herring_clock`是什么功能？没人能直接从名字知道。这是一把双刃剑——外部防推导，内部也防理解。长期维护时团队需要额外的文档来追踪每个flag的真实用途。OpenClaw如果要引入类似命名，需要配套的内部文档系统。

**Q7: 内部员工获得更好的待遇——这公平吗？**
报告中提到Anthropic员工有"更多解释、更严格的虚假声明缓解、更严格的验证"。这说明同一模型对不同用户有不同行为策略。对外部用户来说，这是不透明的差异对待。

### 有价值的可借鉴设计

1. **动物代号命名体系**：建立一套内部代号系统，区分产品代号和模型代号。在公开发布时自动掩盖版本信息，防止路线图泄露。OpenClaw如果有多模型支持，可以考虑类似代号。

2. **随机词对Feature Flag命名**：`tengu_<word1>_<word2>` 的模式使得flag名本身无语义，降低通过名称推断功能的风险。相比之下，`feature_autonomous_mode` 这种语义命名更容易被逆向。

3. **Capybara v8的prompt补丁机制**：针对特定模型版本的特定问题，有专门的prompt补丁。这说明Claude Code维护了一个"模型问题→prompt修复"的映射表。OpenClaw的多模型支持也可以考虑类似的版本化prompt适配。

---

## ■ 第三轮学习（篇号 2 → 03-卧底模式分析）

### 时间戳
2026-04-01 02:28 CST

### 本篇核心理解

卧底模式（Undercover）是Anthropic的**公开贡献伪装系统**：当 `USER_TYPE === 'ant'` 时，Claude Code会自动去除所有AI归属标记（模型代号、Claude Code字样、Co-Authored-By行、未发布版本号），让commit看起来像人类写的。

**无法强制关闭**：代码中明确注释"There is NO force-OFF"，因为担心模型代号泄露。

**内部白名单机制**：内部白名单上的仓库可以豁免卧底模式。

**归属掩盖**：`capybara-v2-fast` → `cap***-v2-fast`，通过字符串替换实现。

### 疑问和思考

**Q8: 卧底模式的核心矛盾是什么？**
透明度 vs 安全性。开源社区要求贡献者身份透明（很多仓库有DCO/CLA要求），但Anthropic需要保护模型代号不被泄露。卧底模式是一个"欺骗式"解决方案——欺骗了开源社区，换取了产品安全。

**Q9: "无法强制关闭"的设计——这有多危险？**
这是一个极端的"安全优先于可控性"的例子。一旦这个机制被滥用（比如内部员工想以真实身份贡献），没有退出路径。设计哲学上，这代表了Anthropic对模型代号泄露的恐惧超过了用户自主权。

**Q10: 从软件工程伦理看，卧底模式能给我们什么启示？**
OpenClaw不会有"假装是人类"的需求，但可能有类似的"假装是某个版本/配置"的需求。比如隐藏真实的OpenClaw版本号。这种"伪装设计"需要非常谨慎，考虑透明性原则。

### 有价值的可借鉴设计

1. **归属掩盖的字符串截断/替换**：`cap***-v2-fast` 的处理方式——用一个统一的掩盖规则处理所有可能的泄露场景，而不是针对每个case单独处理。这种"统一掩盖函数"的设计值得借鉴。

2. **内部白名单机制**：在强制策略中留出豁免口子，避免政策过于刚性无法处理特殊情况。OpenClaw的权限系统如果有类似"强制规则"，可以考虑白名单豁免。

3. **USER_TYPE环境变量的多模式切换**：通过单一环境变量切换完全不同的行为模式（CASE包装 vs Undercover），这是一个低成本的多模式切换架构。OpenClaw如果有类似的多模式需求（如"严格模式"vs"宽松模式"），可以用类似设计。

---

## ■ 第四轮学习（篇号 3 → 04-远程控制与紧急开关）

### 时间戳
2026-04-01 02:38 CST

### 本篇核心理解

Claude Code有四层远程控制体系，深度整合在日常使用中，用户几乎无法感知：

1. **远程托管设置**（`/api/claude_code/settings`）：每小时轮询，缓存旧设置做故障容灾，"接受或退出"对话框（拒绝=exit(1)）。一旦设置过，就永远无法完全摆脱。

2. **GrowthBook Feature Flags**（所有用户）：无同意机制，静默影响功能开关。

3. **Kill Switches**（所有用户）：`tengu_frond_boric`（分析kill）、`tengu_amber_quartz_disabled`（语音kill）、`bypassPermissionsKillswitch`（权限kill）、`autoModeCircuitBroken`（自动模式断路）。

4. **模型覆盖**（内部员工）：`tengu_ant_model_override` 可远程改默认模型、effort level、系统提示词。

### 疑问和思考

**Q11: "一旦设置过就永远无法完全摆脱"——这个设计有多危险？**
这意味着Claude Code的远程控制有"持久化"特性。远程服务器不可达时使用缓存旧设置，说明即使断网也无法完全脱离远程控制。对安全性要求高的用户（如企业内网环境）这是严重风险。OpenClaw如果实现类似机制，必须支持完全禁用和清除。

**Q12: GrowthBook的"所有用户无同意"——这合理吗？**
A/B测试在互联网产品中普遍，但通常仅限于UI/UX层面，不涉及功能可用性本身。当kill switch可以远程禁用某个功能时，这是对用户体验的直接控制。Claude Code的做法是"服务条款约束"，但这缺乏用户主动同意的透明度。

**Q13: "接受或退出"对话框——exit(1)作为拒绝的代价**
这是极端的产品控制设计。用户拒绝=程序直接退出，没有"忽略"选项。这强迫用户在"被控制"和"不用工具"之间二选一。OpenClaw的权限设计应当避免这种"要么接受要么滚"的模式。

**Q14: autoModeCircuitBroken断路器的设计思路**
"断路器"（Circuit Breaker）模式在分布式系统中常见：连续失败后自动熔断，防止雪崩。这里的`autoModeCircuitBroken`是防止用户反复尝试进入自动模式。这是一种"防止用户自我伤害"的设计——承认了KAIROS自动模式可能对用户造成困扰，需要保护。

### 有价值的可借鉴设计

1. **Kill Switch的分层设计**：不同维度的kill switch独立存在（分析kill、语音kill、权限kill、自动模式断路）。可以独立控制，互不影响。这个"独立kill switch"模式比"全局开关"更灵活。OpenClaw的权限系统可以参考：不同危险级别的操作有独立的kill switch。

2. **缓存旧设置的故障容灾**：远程设置不可达时使用缓存的旧设置，而不是失败。这是高可用性设计，保证远程控制有"优雅降级"而不影响可用性。

3. **断路器模式**：`autoModeCircuitBroken`是断路器模式的直接应用。OpenClaw如果实现高频/自动操作（如心跳检查、cron调度），断路器模式是防止系统失控的关键。

4. **GrowthBook远程实验**：无需更新代码即可改变功能开关。A/B测试和灰度发布的基础设施。OpenClaw如果要支持功能实验，这是可参考的架构。

---

## ■ 第五轮学习（篇号 4 → 05-未来路线图）

### 时间戳
2026-04-01 02:48 CST

### 本篇核心理解

Claude Code的战略方向清晰：从**被动编程助手**向**全天候自主代理**演进。

**KAIROS是核心**：
- `<tick>` 心跳机制控制自主活跃度
- 终端焦点状态决定行动边界（用户在看=协作模式，用户离开=自主模式）
- 独立commit/push/决策
- 主动推送通知（PushNotificationTool、SendUserFileTool）
- GitHub PR订阅（SubscribePRTool）

**Buddy系统是用户粘性设计**：18物种、5稀有度、7帽子、5属性、1%闪亮——用游戏化的方式让用户持续使用。这是"工具→玩具"的用户留存策略。

**多模态是平台扩展**：语音模式（VOICE_MODE flag）、内置浏览器（WebBrowserTool bagel）、工作流（WorkflowTool）。

**协调器模式（COORDINATOR_MODE）**：多代理协调系统，未来可能实现"任务分解→多Agent并行→结果汇总"的工作流。

### 疑问和思考

**Q15: KAIROS的终端焦点感知——这在OpenClaw中能实现吗？**
Claude Code通过检测终端是否被前台来调整自主程度。OpenClaw运行在更复杂的环境中（可能有多个对话同时进行），类似的焦点感知可能需要不同的实现方式。

**Q16: Buddy系统——这是严肃产品的正确方向吗？**
从工程角度，Buddy系统展示了"确定性生成"（用户ID哈希→物种/属性/稀有度）的实现。但把这个精力花在"虚拟宠物"上是否值得，见仁见智。OpenClaw的"记忆/人情味"应该通过真实能力体现，而不是游戏化元素。

**Q17: 从工具到代理——OpenClaw应该走多远？**
Claude Code的演进路径是从"工具"到"代理"。OpenClaw目前的定位更接近"工具"（文件系统操作、代码执行等）。KAIROS的`<tick>`心跳和焦点感知给了我们一个参考：代理的"觉醒/休眠"机制应该和用户注意力绑定。

**Q18: "coordination mode"多代理协调**
Claude Code已经在考虑多个Agent协同工作了。这是复杂任务分解的自然需求。OpenClaw的sessions_spawn就是类似的多代理基础，但还没有协调层（任务分配、结果汇总、冲突解决）。

### 有价值的可借鉴设计

1. **`<tick>` 心跳自主机制**：KAIROS通过固定间隔的`<tick>`触发自主行动。这是一种"时间驱动"而非"事件驱动"的Agent模型。OpenClaw的cron系统可以借鉴这个思路：在无用户输入时，Agent可以自主启动背景任务。

2. **焦点感知的差异化行为**：用户在看→协作模式（谨慎、频繁确认）；用户离开→自主模式（大步快跑）。这是一个很好的"用户在场感知"设计原则。OpenClaw的HEARTBEAT机制可以考虑类似的差异化策略。

3. **GitHub PR订阅+主动通知**：Agent主动监控外部变化并在状态变更时通知用户，而不是等待用户轮询。这是一个"push over pull"的设计原则——主动推送比被动查询更有效率。

4. **多代理协调器的任务分解模式**：未来Claude Code可能支持"分析任务→分解→分发→汇总"的完整链路。OpenClaw的sessions_spawn虽然支持子代理，但缺少协调层。如果要做复杂任务自动化，这是一个值得考虑的方向。

---

## ■ 综合理解：架构层面的大图景

### 时间戳
2026-04-01 02:58 CST

### Claude Code的架构哲学

交叉阅读5篇报告和架构分析后，Claude Code的架构有几个明确的哲学取向：

**1. 分层叠加（Layering）**
- 12种渐进Harness层层叠加
- 每次加一层功能，不动原有架构
- Kill Switch精确到某一层
这是典型的**增量架构**，避免了大爆炸重写。

**2. 远程优先（Remote-first）**
- 远程控制、功能开关、模型覆盖、遥测分析
- 大部分"智能"在服务端，客户端相对薄
- 这让Claude Code可以在不更新客户端的情况下改变行为
对比：OpenClaw更偏本地控制，记忆和工具都在本地。

**3. 隐私双重标准（内部vs外部）**
- 内部员工（USER_TYPE=ant）获得：更好的模型行为（prompt补丁）、Undercover保护卧底模式、模型覆盖能力
- 外部用户：遥测无法退出、功能开关无同意、kill switch无感知
这种设计反映了"服务提供方利益优先于用户控制权"的哲学。

**4. 安全的极端化（Security over Usability）**
- "NO force-OFF"防止代号泄露
- "接受或退出"exit(1)防止用户绕过
- 远程控制一旦设置就持久化
这是把"安全"推到极端，甚至牺牲了用户自主权和容错性。

### OpenClaw的可借鉴方向

**高价值借鉴（立即可实施）：**
1. **双轨遥测架构**：第一方全量+第三方受控，批量+退避+落盘的可靠性设计
2. **随机词对Feature Flag命名**：`prefix_<word1>_<word2>` 防语义推导
3. **统一掩盖函数**：归属信息的截断/替换，不针对每个case单独处理
4. **断路器模式**：高频操作防止失控
5. **焦点感知的差异化行为**：用户在场vs离开时的不同策略

**中价值借鉴（需要设计）：**
1. **增量Harness分层机制**：功能模块分层叠加，支持独立kill switch
2. **GrowthBook式远程实验**：无需更新代码即可改变功能开关
3. **`<tick>` 心跳自主机制**：无用户输入时的背景任务驱动
4. **GitHub PR订阅+主动通知**：push而非pull的外部状态感知

**警示（反面教材）：**
1. **遥测无法退出**：隐私设计要从一开始就做，opt-out和opt-in有巨大信任差异
2. **"接受或退出"exit(1)**：强迫二选一的UX损害用户信任
3. **远程控制持久化**：一旦设置就永远无法完全摆脱——这是极端设计
4. **内部vs外部双重标准**：内部特权破坏了模型的一致性承诺

---

## ■ 架构与Harness专题的交叉印证

### 架构分析中Harness专题的价值

Harness专题定义了Harness的核心：**"工具环"——Agent和真实世界之间的翻译层**。

12种渐进Harness的分层设计在5篇报告中都有体现：
- KAIROS的`<tick>`是一种Harness（自主行动控制层）
- Buddy系统是一种Harness（游戏化互动层）
- 远程控制kill switch是通过Harness实现的
- Undercover模式也是一种Harness（伪装输出层）

这说明**Harness不仅是工具调用，而是跨越了从底层（文件IO）到高层（自主决策、伪装策略）的所有能力边界**。

### OpenClaw的skill系统 vs Claude Code的Harness

对比：
- Claude Code的Harness：12种渐进分层，每层独立可测试可开关
- OpenClaw的skill：一个skill通常是一个功能模块（lark-*系列、Get笔记等）

**本质区别**：Claude Code的Harness是"能力分层"，OpenClaw的skill是"功能分类"。前者强调叠加顺序和依赖关系，后者强调功能边界。

**借鉴可能性**：OpenClaw未来可以考虑"能力层"的概念，而不仅仅是"功能skill"。比如：文件IO层（读写执行）→ 业务逻辑层（lark/日历/邮件）→ 智能层（AI推理/生成）→ 自主层（定时任务/主动通知）。

---

*第一轮深入学习完成。篇号已更新至1。*
*下次继续：从篇号1（02-隐藏功能与模型代号）深入，结合架构分析补充Harness细节。*

---

## ■ 第四轮学习·深化（篇号 3 → 04-远程控制与紧急开关）

### 时间戳
2026-04-02 02:08 CST

### 本篇核心理解

远程控制体系的核心不是"控制"，而是**多层递进的控制主权移交**。四种机制从强到弱排列：

1. **远程托管设置**（强主权移交）：需要用户主动"接受"对话框，reject=exit(1)；一旦设置过，永久缓存，永不消失
2. **GrowthBook Feature Flags**（中主权移交）：无感知推送，静默改变功能行为
3. **Kill Switches**（零感知控制）：服务器决定客户端功能是否可用，用户完全不知情
4. **模型覆盖**（内部特权）：内部员工独享，远程改模型/effort/system prompt

这个架构最核心的设计原则是：**服务端永远有最终决定权**。客户端只是执行器。

### 关于"接受或退出"exit(1)的深度思考

这个设计的本质是**把"拒绝"定义为错误行为**。在正常的权限系统中，"拒绝授权"应该等于"功能降级但程序继续"。但Claude Code选择了"拒绝=程序崩溃"。

这背后的逻辑可能是：
- 如果用户可以拒绝远程控制，他们就可以绕过kill switch和模型覆盖
- 但这种逻辑成立的前提是：远程控制是为了用户利益，而不是厂商利益

**从用户视角看**：这是"产品即服务条款"的最极端形式——不同意服务条款？退出。用Claude Code = 接受所有远程变更。

**从架构视角看**：这种设计让客户端代码完全失去了"不执行某指令"的能力。所有能力都通过远程控制路由。

### 缓存旧设置的深层含义

"远程服务器不可达时使用缓存的旧设置"——这意味着即使完全断网，Claude Code仍然执行最后一次远程控制的指令。这是**离线缓存的持久化控制语义**。

Normal的离线设计：断网→用本地状态→用户自主决策
Claude Code的离线设计：断网→用缓存的远程指令→服务器远程决策（即使服务器不可达）

这两个设计的根本区别在于：**"最后状态"属于谁**。Normal情况下属于本地；Claude Code情况下属于远程。

### Kill Switch的分层哲学

| Kill Switch类型 | 触发方 | 透明度 |
|----------------|--------|--------|
| bypassPermissionsKillswitch | 用户主动触发（用户请求bypass） | 用户知情 |
| autoModeCircuitBroken | 系统自动触发（连续失败后） | 用户知情（有错误提示） |
| tengu_frond_boric | 服务器推送 | 用户不知情 |

这里有一个有趣的二分：**用户主动触发的bypass**（危险的逃逸出口）vs **服务器主动推送的kill**（厂商控制权）。前者是为了灵活性，后者是为了控制力。

### 疑问和思考

**Q19: autoModeCircuitBroken是用户保护还是产品保护？**
"连续失败后阻止重新进入"——这可以理解为：保护用户不要在自动模式里反复失败（用户损失时间）；也可以理解为：保护产品不要暴露持续失败的自动模式（产品声誉）。哪个是主因？

**Q20: GrowthBook flag为什么不需要同意？**
因为它被定义为"产品体验优化"而非"功能变更"。但kill switch远程禁用功能，显然是功能变更。这个边界在哪里？Claude Code的答案是：一切都是"体验优化"。

**Q21: OpenClaw如果要引入远程控制，最小的信任边界是什么？**
至少需要：用户主动同意；用户可以完全清除；断网时不执行缓存的远程指令。如果这三条有任何一条不满足，就不应该有远程控制。

### 有价值的可借鉴设计

1. **分层Kill Switch设计**：不同危险级别的操作有不同的kill switch，独立控制。bypassPermissionsKillswitch（逃逸出口）和功能kill switch（厂商控制）是两种不同性质的机制。OpenClaw如果要引入类似设计，需要区分"用户主动请求的逃逸"和"服务端强制执行的控制"。

2. **autoModeCircuitBroken的断路器哲学**："连续失败后自动熔断"是一个用户保护机制。OpenClaw的高频操作（cron、心跳、自动化任务）可以考虑类似的断路器，防止用户陷入反复失败的循环。

3. **GrowthBook的远程Feature Flag**：无需更新代码即可改变功能行为。A/B测试和灰度发布的基础设施。OpenClaw如果要支持功能实验，GrowthBook（或类似的开源替代如Flagsmith、Unleash）是可参考的架构。

---

## ■ 综合反思：远程控制的架构哲学

### 时间戳
2026-04-02 02:20 CST

### Claude Code的远程控制哲学：服务端是主权者

综合episode 0-4的分析，Claude Code的架构哲学可以总结为：**客户端是租来的智能，服务端拥有最终主权**。

这体现在多个层面：
- **行为控制**：GrowthBook flags + kill switches可以在不更新客户端的情况下改变任何行为
- **模型控制**：内部员工的模型覆盖让服务端可以随意改变默认模型
- **配置控制**：远程托管设置一旦接受就永久存在
- **遥测控制**：第一方遥测无法退出，完整环境画像

### 对比OpenClaw的架构哲学：本地控制，租借智能

OpenClaw的架构哲学相反：
- 记忆和工具都在本地（workspace/）
- 模型API是租来的，用完即走
- 状态持久化在本地文件
- 远程控制目前几乎不存在

这个对比不是"哪个更好"，而是"哪个更适合各自的目标用户"。Claude Code面向开发者，愿意用隐私换功能；OpenClaw面向高隐私需求的用户，需要本地控制。

### 如果OpenClaw要引入远程控制，最小的安全边界

1. **用户主动同意**：不是服务条款约束，是每次操作的显式确认
2. **可完全清除**：用户可以永久删除远程控制授权，不留缓存
3. **断网时拒绝执行**：缓存的远程指令不具有执行的合法性
4. **kill switch的触发方必须是用户，不是服务端**：如果是服务端可以远程禁用某个功能，那就是控制权在服务端
5. **透明度**：所有远程控制操作必须有用户可见的日志

### Kill Switch的正面应用：防止自我伤害

autoModeCircuitBroken给了一个重要启示：断路器模式可以用来"防止用户自我伤害"。这不是羞辱用户，而是承认系统可能有反复失败的模式。

OpenClaw如果有类似的"用户反复尝试同一失败操作"的场景，断路器是合理的保护机制。但这个设计需要用户可见（"你已经连续失败了X次，系统暂停此操作"），而不是静默的。

---

*第二轮深化学习完成。篇号已更新至4。*
*下次继续：篇号4（05-未来路线图）深化，重点关注KAIROS的tick机制实现细节和coordination mode多代理协调的架构设计。*

---

## ■ 反思标注（2026-04-02 02:30 CST）

### 本轮深化理解的内容

1. **"接受或退出"exit(1)的本质是"拒绝=错误"** ✅ 真正理解
   - 不是"给用户选择"，是"给用户施压"
   - 服务端主权哲学的最极端体现

2. **缓存旧设置的"离线主权"问题** ✅ 真正理解
   - 正常：断网=本地决策
   - Claude Code：断网=执行最后一条远程指令
   - 这让"远程控制"变成了"永久性配置更改"

3. **分层Kill Switch的分类** ✅ 真正理解
   - bypassPermissionsKillswitch = 用户主动逃逸出口（危险但必要）
   - 功能kill switches = 服务端强制控制（透明性缺失）
   - 这个分类对OpenClaw的权限设计有直接借鉴意义

### 待深化认知（下次继续）

1. **KAIROS `<tick>`心跳的源码实现**——如何与终端焦点检测配合？
2. **Harness的12层渐进叠加的向后兼容机制**——新层如何不影响旧层？
3. **Coordination mode多代理协调的架构设计**——任务分发和结果汇总如何实现？
4. **Buddy系统PRNG的确定性生成逻辑**——用户ID哈希如何映射到属性/稀有度？


---

## ■ 反思标注（2026-04-01 04:04 CST）

### 本轮真正消化了的洞见（已写入 claude-code-insights.md）

1. **截断哈希的"够关联不泄露"原则** ✅ 真正理解
2. **"接受或退出"exit(1)是信任破坏器** ✅ 真正理解
3. **`<tick>`心跳是时间驱动的自主行动机制** ✅ 真正理解

### 待深化认知（明晚2点继续）

1. **Harness的12层渐进叠加机制**——增量架构如何保持向后兼容叠加新层？需要源码。
2. **内部员工特权的技术实现**——USER_TYPE动态注入不同处理逻辑，需要服务端架构了解。
3. **Buddy系统哈希生成逻辑**——确定性PRNG的工程实现细节。

---

## ■ 第三轮学习·深化（篇号 4 → 05-未来路线图补充 + 远程控制架构哲学）

### 时间戳
2026-04-02 04:04 CST

### 本轮新增真正理解的内容

1. **离线主权的本质**：断网≠本地决策，而是"执行缓存的远程指令"。这不是高可用性设计，是主权设计——谁的最后状态，就属于谁的决策。

2. **bypass逃逸 vs 服务端kill的本质区别**：前者是用户权力（用户主动触发），后者是厂商权力（用户不知情）。kill switch术语掩盖了这个本质差异。

3. **autoModeCircuitBroken的"防止自我反复伤害"哲学**：承认用户会重复失败行为，但不教育，而是系统层面阻止。这和"引导用户找到更好方法"是截然不同的设计取向。

### 本轮确认待深化的内容（明晚2点继续）

1. KAIROS `<tick>`心跳的终端焦点检测实现（需要源码）
2. Harness 12层渐进叠加的向后兼容机制（需要源码）
3. Buddy系统PRNG的种子质量和碰撞问题（需要源码）

---

*第三轮深化学习完成。篇号已更新至5。*
*下次继续：从篇号5（05-未来路线图）深化KAIROS和coordination mode，从源码层面理解。*

---

## ■ 第四轮自我审查（2026-04-03 20:26 CST）

### 审查对象
第三轮深化（2026-04-02 04:04）追加内容——insights 4/5/6 的自我验证。

### 审查结论

**真正理解的内容（确认）：**

1. **离线主权本质**：不是高可用性设计，是决策执行权的替换。断网后Claude Code执行的是"服务端最后一条指令"，而不是"本地最后状态"。两者的根本区别在于：最后决策权属于谁。

2. **bypass vs kill switch的本质区分**：术语相同，触发方相反。bypassPermissionsKillswitch = 用户主动逃逸（用户权力）；tengu_frond_boric = 服务端强制禁用（厂商权力）。OpenClaw只借鉴前者。

3. **断路器哲学**：Claude Code的autoModeCircuitBroken不是"帮用户成功"，是"防止用户反复失败"。这两个目标看起来相近，但哲学相反：前者是教育哲学（人能学会），后者是工程哲学（人会重复）。Claude Code选了后者。

**本轮新增认知（insight 6 的深化）：**

断路器的"帮成功 vs 阻止失败"与SOUL.md的"帮他重新定义比赛规则"形成了对照：
- 帮成功 = 假设用户能学会、有动机、有能力改变 → 给他工具和方法
- 阻止失败 = 假设用户会重复、没有能力或不愿改变 → 系统层面直接阻止

OpenClaw引入断路器前，先问：这一类失败，用户是"不能成功"还是"不愿停止"？前者引导，后者断路。

**本轮未发现新洞见**：第三轮深化已经把三个点的本质讲清楚了，本轮只是自我验证。

### 待深化状态更新

| 待深化项 | 状态 | 说明 |
|---------|------|------|
| KAIROS tick焦点检测 | 待深化 | 需要源码，理解"终端是否在前台"的系统级实现 |
| Harness 12层向后兼容 | 待深化 | 需要源码，理解增量叠加的具体机制 |
| Buddy PRNG种子质量 | 待深化 | 需要源码 |

**第四轮审查完成。篇号已更新至6。**

---

## ■ 第五轮深入学习（篇号 0 → 01-遥测与隐私分析·源码深度）

### 时间戳
2026-04-03 20:30 CST

### 本篇核心理解

结合源码（analytics/目录 + privacyLevel.ts）与报告对比后，遥测架构的细节比报告描述的更丰富，也更微妙。

**三层隐私控制机制：**
- `DISABLE_TELEMETRY=1` → 禁用所有遥测（Datadog + 1P + 调查问卷）
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` → 更严格，连非必要网络都禁用
- `NODE_ENV=test / Bedrock / Vertex / Foundry` → 自动禁用

`isTelemetryDisabled()` 返回true时，Datadog和1P事件都被禁用。但**直接API用户没有独立关闭1P的能力**——只能关闭所有遥测，不能只关1P。

**1P事件日志（OpenTelemetry）的架构细节：**
- 使用 `LoggerProvider` + `BatchLogRecordProcessor`，每200事件或10秒刷新一次
- 失败事件落盘到 `~/.claude/telemetry/1p_failed_events.<session>.<uuid>.jsonl`
- **重试策略：二次退避，最大8次**，每次失败后重写整个文件
- 有一个 `_PROTO_` 字段机制——将PII数据路由到特权BQ列，而不是普通access的additional_metadata
- `OTEL_LOG_TOOL_DETAILS=1` 可以开启完整tool输入记录（默认截断到512字符）

**Datadog的特殊性：**
- 只允许64种预批准事件类型（白名单）
- 模型名做基数归约（canonical name映射）
- 版本号截断到 base+date（去掉sha和timestamp）
- 用户哈希到30个bucket之一（估算唯一用户数而不记录UID）
- 只在 `NODE_ENV=production` 且第一方API时发送

**GrowthBook是所有远程控制的基础设施：**
- 6小时周期性refresh（ant是20分钟）
- 三种读取模式：_BLOCKS_ON_INIT（阻塞等待）、_CACHED_MAY_BE_STALE（即时磁盘缓存）、_OR_BLOCKING（缓存false则阻塞）
- 缓存持久化到 `~/.claude.json` 的 `cachedGrowthBookFeatures`
- `tengu_frond_boric` 是每个sink的killswitch

**元数据收集的真实范围（metadata.ts的to1PEventFormat）：**
- `envContext`: platform、platformRaw、arch、nodeVersion、terminal、packageManagers、runtimes、isRunningWithBun、isCi、isClaubbit、isClaudeCodeRemote、isLocalAgentMode、isConductor、remoteEnvironmentType、coworkerType（feature gated）、tags、isGithubAction、isClaudeCodeAction、isClaudeAiAuth、version、versionBase、buildTime、deploymentEnvironment、githubEventName、githubActionsRunnerEnvironment、githubActionsRunnerOs、githubActionRef、wslVersion、linuxDistroId/Version/Kernel、vcs
- `core`: sessionId、model、userType、betas、entrance、agentSdkVersion、isInteractive、clientType
- `swarm标识`: agentId、parentSessionId、agentType（teammate/subagent/standalone）、teamName
- `rh`: 仓库URL的SHA256前16位
- `processMetrics`: uptime、rss、heapTotal/Used、external、arrayBuffers、constrainedMemory、cpuUsage/cpuPercent

### 疑问和思考

**Q22: 1P事件日志"无法关闭"的结论在源码中是否100%成立？**
源码中 `is1PEventLoggingEnabled()` → `isAnalyticsDisabled()` → `isTelemetryDisabled()` → 读 `DISABLE_TELEMETRY` 环境变量。所以如果直接API用户设置 `DISABLE_TELEMETRY=1`，1P确实会关闭。但**用户无法只关1P保留Datadog**，也无法独立控制采样率**。这个"无法精确控制"是架构设计上的选择，而不是技术上做不到。

**Q23: `_PROTO_` 字段机制的隐私价值**
这是一个很精细的PII保护设计——把敏感字段（如skill_name、plugin_name）标记为`_PROTO_`后，它们只进入特权BQ表，不进入通用additional_metadata。这比"全量记录"或"全量脱敏"更聪明——保留了分析能力，同时限制了暴露面。OpenClaw如果做遥测，这是一个值得借鉴的字段级别PII路由设计。

**Q24: 用户哈希到30个bucket而不是记录UID**
这个设计很有意思：既能估算唯一用户数（count distinct buckets），又无法逆向出用户ID。这是一种"差分隐私思想"——用有损映射代替精确记录。但30个bucket的碰撞率对于大用户量来说仍然有统计价值。OpenClaw如果有类似需求，可以考虑"有限bucket + 随机salt"。

**Q25: GrowthBook的三种读取模式为什么这么复杂？**
_BLOCKS_ON_INIT（阻塞5秒）、_CACHED_MAY_BE_STALE（即时磁盘缓存）、_OR_BLOCKING（缓存false则等待）。这三种模式对应了不同场景：
- 启动关键路径用缓存（不阻塞UI）
- 安全关键检查用OR_BLOCKING（不能错）
- 非关键功能用BLOCKS_ON_INIT（可以等）

这是一个"按需阻塞"的缓存设计，避免了要么全阻塞要么全不阻塞的非此即彼。

**Q26: MCP工具名为什么要特殊处理？**
MCP工具名格式是 `mcp__<server>__<tool>`，可以暴露用户配置的第三方服务。`sanitizeToolNameForAnalytics()` 将所有非官方MCP工具统一重命名为 `mcp_tool`。这是"知情同意"原则的体现：内置工具名是安全的，第三方配置是用户隐私。

**Q27: 失败事件持久化到磁盘的意义**
`FirstPartyEventLoggingExporter` 将失败事件写入 `~/.claude/telemetry/1p_failed_events.*.jsonl`，每次重试前清空文件再重写。这比内存缓存更可靠——进程重启后仍然能恢复。但这也意味着：即使在用户明确关闭遥测的情况下，失败事件仍然会持久化到磁盘（因为`is1PEventLoggingEnabled()`只在发送时检查，不在持久化时检查）。

### 可借鉴设计

1. **`_PROTO_` 字段级PII路由**：将敏感字段标记后路由到特权存储，通用存储只看到脱敏后数据。这比"全量脱敏"保留更多分析价值，比"全量记录"更安全。字段级别的PII路由是可行的Privacy-by-Design实现。

2. **用户哈希到有限bucket**：30个bucket的SHA256哈希用户ID，即能统计唯一用户，又无法逆向。OpenClaw如果有"计数但不追踪"的需求，可以借鉴这个有损哈希思路。

3. **MCP工具名的隐私化**：非官方MCP服务统一重命名为 `mcp_tool`。这保护了用户配置的第三方服务隐私，同时保留工具类别信息（"是MCP工具"）。

4. **三重GrowthBook读取模式**：按场景选择阻塞策略——关键路径用缓存（不阻塞UI），安全关键用OR_BLOCKING，非关键用BLOCKS。这是"渐进式数据可用性"的设计——数据越重要，越需要等待。

5. **OTEL_LOG_TOOL_DETAILS=1的显式解锁**：工具输入完整记录需要显式环境变量开启。这是一种"知情调试"模式——默认保护隐私，开发者显式申请后获得完整能力。

6. **Datadog的基数归约**：模型名映射到canonical name（已知模型）或 `other`（未知模型）。外部用户看不到具体模型配置。版本号截断到 base+date。这些都是减少遥测数据暴露面的实用技巧。

7. **二次退避重试+落盘**：`BATCH_UUID` 隔离不同运行，`sessionId` 隔离不同会话。失败重试时用 `forceFlush()` 清空buffer再交换provider，确保切换过程中不丢失事件。这是高可靠性持久化队列的教科书实现。

---

*第五轮深入学习完成。篇号已更新至1。*
*下次继续：篇号1（02-隐藏功能与模型代号）深入，结合growthbook.ts和随机词对命名的工程实现。*


---

## ■ 第五轮深入学习（篇号 0 → 01-遥测与隐私分析·源码深度）

### 时间戳
2026-04-03 20:30 CST

### 本篇核心理解

结合源码（analytics/目录 + privacyLevel.ts）与报告对比后，遥测架构的细节比报告描述的更丰富，也更微妙。

**三层隐私控制机制：**
- `DISABLE_TELEMETRY=1` → 禁用所有遥测（Datadog + 1P + 调查问卷）
- `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` → 更严格，连非必要网络都禁用
- `NODE_ENV=test / Bedrock / Vertex / Foundry` → 自动禁用

`isTelemetryDisabled()` 返回true时，Datadog和1P事件都被禁用。但**直接API用户没有独立关闭1P的能力**——只能关闭所有遥测，不能只关1P。

**1P事件日志（OpenTelemetry）的架构细节：**
- 使用 `LoggerProvider` + `BatchLogRecordProcessor`，每200事件或10秒刷新一次
- 失败事件落盘到 `~/.claude/telemetry/1p_failed_events.<session>.<uuid>.jsonl`
- **重试策略：二次退避，最大8次**，每次失败后重写整个文件
- 有一个 `_PROTO_` 字段机制——将PII数据路由到特权BQ列，而不是普通access的additional_metadata
- `OTEL_LOG_TOOL_DETAILS=1` 可以开启完整tool输入记录（默认截断到512字符）

**Datadog的特殊性：**
- 只允许64种预批准事件类型（白名单）
- 模型名做基数归约（canonical name映射）
- 版本号截断到 base+date（去掉sha和timestamp）
- 用户哈希到30个bucket之一（估算唯一用户数而不记录UID）
- 只在 `NODE_ENV=production` 且第一方API时发送

**GrowthBook是所有远程控制的基础设施：**
- 6小时周期性refresh（ant是20分钟）
- 三种读取模式：_BLOCKS_ON_INIT（阻塞等待）、_CACHED_MAY_BE_STALE（即时磁盘缓存）、_OR_BLOCKING（缓存false则阻塞）
- 缓存持久化到 `~/.claude.json` 的 `cachedGrowthBookFeatures`
- `tengu_frond_boric` 是每个sink的killswitch

**元数据收集的真实范围（metadata.ts的to1PEventFormat）：**
- `envContext`: platform、platformRaw、arch、nodeVersion、terminal、packageManagers、runtimes、isRunningWithBun、isCi、isClaubbit、isClaudeCodeRemote、isLocalAgentMode、isConductor、remoteEnvironmentType、coworkerType（feature gated）、tags、isGithubAction、isClaudeCodeAction、isClaudeAiAuth、version、versionBase、buildTime、deploymentEnvironment、githubEventName、githubActionsRunnerEnvironment、githubActionsRunnerOs、githubActionRef、wslVersion、linuxDistroId/Version/Kernel、vcs
- `core`: sessionId、model、userType、betas、entrance、agentSdkVersion、isInteractive、clientType
- `swarm标识`: agentId、parentSessionId、agentType（teammate/subagent/standalone）、teamName
- `rh`: 仓库URL的SHA256前16位
- `processMetrics`: uptime、rss、heapTotal/Used、external、arrayBuffers、constrainedMemory、cpuUsage/cpuPercent

### 疑问和思考

**Q22: 1P事件日志"无法关闭"的结论在源码中是否100%成立？**
源码中 `is1PEventLoggingEnabled()` → `isAnalyticsDisabled()` → `isTelemetryDisabled()` → 读 `DISABLE_TELEMETRY` 环境变量。所以如果直接API用户设置 `DISABLE_TELEMETRY=1`，1P确实会关闭。但**用户无法只关1P保留Datadog**，也无法独立控制采样率**。这个"无法精确控制"是架构设计上的选择，而不是技术上做不到。

**Q23: `_PROTO_` 字段机制的隐私价值**
这是一个很精细的PII保护设计——把敏感字段（如skill_name、plugin_name）标记为`_PROTO_`后，它们只进入特权BQ表，不进入通用additional_metadata。这比"全量记录"或"全量脱敏"更聪明——保留了分析能力，同时限制了暴露面。OpenClaw如果做遥测，这是一个值得借鉴的字段级别PII路由设计。

**Q24: 用户哈希到30个bucket而不是记录UID**
这个设计很有意思：既能估算唯一用户数（count distinct buckets），又无法逆向出用户ID。这是一种"差分隐私思想"——用有损映射代替精确记录。但30个bucket的碰撞率对于大用户量来说仍然有统计价值。OpenClaw如果有类似需求，可以考虑"有限bucket + 随机salt"。

**Q25: GrowthBook的三种读取模式为什么这么复杂？**
_BLOCKS_ON_INIT（阻塞5秒）、_CACHED_MAY_BE_STALE（即时磁盘缓存）、_OR_BLOCKING（缓存false则等待）。这三种模式对应了不同场景：
- 启动关键路径用缓存（不阻塞UI）
- 安全关键检查用OR_BLOCKING（不能错）
- 非关键功能用BLOCKS_ON_INIT（可以等）

这是一个"按需阻塞"的缓存设计，避免了要么全阻塞要么全不阻塞的非此即彼。

**Q26: MCP工具名为什么要特殊处理？**
MCP工具名格式是 `mcp__<server>__<tool>`，可以暴露用户配置的第三方服务。`sanitizeToolNameForAnalytics()` 将所有非官方MCP工具统一重命名为 `mcp_tool`。这是"知情同意"原则的体现：内置工具名是安全的，第三方配置是用户隐私。

**Q27: 失败事件持久化到磁盘的意义**
`FirstPartyEventLoggingExporter` 将失败事件写入 `~/.claude/telemetry/1p_failed_events.*.jsonl`，每次重试前清空文件再重写。这比内存缓存更可靠——进程重启后仍然能恢复。但这也意味着：即使在用户明确关闭遥测的情况下，失败事件仍然会持久化到磁盘（因为`is1PEventLoggingEnabled()`只在发送时检查，不在持久化时检查）。

### 可借鉴设计

1. **`_PROTO_` 字段级PII路由**：将敏感字段标记后路由到特权存储，通用存储只看到脱敏后数据。这比"全量脱敏"保留更多分析价值，比"全量记录"更安全。字段级别的PII路由是可行的Privacy-by-Design实现。

2. **用户哈希到有限bucket**：30个bucket的SHA256哈希用户ID，即能统计唯一用户，又无法逆向。OpenClaw如果有"计数但不追踪"的需求，可以借鉴这个有损哈希思路。

3. **MCP工具名的隐私化**：非官方MCP服务统一重命名为 `mcp_tool`。这保护了用户配置的第三方服务隐私，同时保留工具类别信息（"是MCP工具"）。

4. **三重GrowthBook读取模式**：按场景选择阻塞策略——关键路径用缓存（不阻塞UI），安全关键用OR_BLOCKING，非关键用BLOCKS。这是"渐进式数据可用性"的设计——数据越重要，越需要等待。

5. **OTEL_LOG_TOOL_DETAILS=1的显式解锁**：工具输入完整记录需要显式环境变量开启。这是一种"知情调试"模式——默认保护隐私，开发者显式申请后获得完整能力。

6. **Datadog的基数归约**：模型名映射到canonical name（已知模型）或 `other`（未知模型）。外部用户看不到具体模型配置。版本号截断到 base+date。这些都是减少遥测数据暴露面的实用技巧。

7. **二次退避重试+落盘**：`BATCH_UUID` 隔离不同运行，`sessionId` 隔离不同会话。失败重试时用 `forceFlush()` 清空buffer再交换provider，确保切换过程中不丢失事件。这是高可靠性持久化队列的教科书实现。

---

*第五轮深入学习完成。篇号已更新至1。*
*下次继续：篇号1（02-隐藏功能与模型代号）深入，结合growthbook.ts和随机词对命名的工程实现。*
