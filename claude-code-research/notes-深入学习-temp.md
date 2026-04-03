
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
