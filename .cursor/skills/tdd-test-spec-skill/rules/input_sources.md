# 输入源处理规则

## OpenSpec `spec.md`（`openspec/specs` 下指定能力目录）

- **路径约定**（满足任一即视为本类输入）  
  - 主目录：`openspec/specs/<能力目录名>/spec.md`（例：`openspec/specs/bff-game-api/spec.md`）  
  - 用户指定：只给能力名（如 `bff-game-api`）则拼为上述路径；或给仓库相对路径 / 绝对路径 / `@文件`  
  - 归档只读变更（可选，用于对照历史）：`openspec/changes/archive/**/specs/<能力目录名>/spec.md`（与当前 `openspec/specs` 同时给出时，以 **`openspec/specs` 现行版优先**）  
- **工具**：不用 MCP；Read 读取对应 `spec.md`。
- **需求名称**：`<能力目录名>` 转可读标题（如 `bff-game-api` →「BFF 游戏 API」）；或取文件中首个 `### Requirement:` 所属主题提炼。

### OpenSpec 文档结构 → 用例映射

| 元素 | 映射 |
|------|------|
| `## ADDED Requirements` / `## MODIFIED Requirements` 等小节 | 测试分模块 / 大章节 |
| `### Requirement: …` | 对应「功能要求」模块；一条 Requirement 下多 Scenario → 一组相关用例 |
| `#### Scenario: …` | 用例标题与场景名；**WHEN** → 前置 + 操作；**THEN** → 预期结果 |
| 文中的接口路径、HTTP 方法、状态码、`{ error: … }` | 接口测试步骤与断言素材 |

### 与其它输入合并

- 仅 **spec.md**：可直接生成用例（Scenario 已含主路径时，按 `generation_rules.md` 补反向/边界）。  
- **spec.md + Superpowers plan / design**：spec 为**行为与验收**来源，plan 为**实现范围与文件**；冲突以 **spec（现行 openspec/specs）** 为准。  
- 多能力：用户可指定多个 `openspec/specs/<id>/spec.md`，输出中分能力建章节，用例 ID 加前缀或分段编号避免重复。

### 缺失处理

- 路径不存在或目录内无 `spec.md` → 提示核对 `<能力目录名>` 或列出 `openspec/specs/` 下可选目录名。

---

## Superpowers Implementation Plan（本地 Markdown）

- **路径约定**（满足任一即视为本类输入）  
  - 默认：`docs/superpowers/plans/**/*.md`  
  - 用户指定：仓库内相对路径、工作区绝对路径、或 `@文件` 指向的 `*Implementation Plan*.md`  
- **工具**：不用 MCP；用 Read 读全文，**超长文件**可按 `## Task N` 分段读取，避免漏 Task。
- **需求名称**：取一级标题 `# … Implementation Plan` 中特征名（去掉 `Implementation Plan`）；若无则提炼 **Goal** 一句为简称。

### 优先解析（高 → 低）

| 区块 | 用途 |
|------|------|
| **Goal / Architecture / Tech Stack** | 测试范围、分层、技术栈、环境前提 |
| **File Map**（表格或目录树） | 模块/文件级测试范围、端侧划分（web/bff/service） |
| **`## Task N` + Step 标题** | 功能点清单；每个 Task 可对应一大类用例模块 |
| 代码块中的 **对外契约** | 接口路径、HTTP 方法、公开 `interface`/`type` 字段、枚举字面量、错误码/文案 |

### 从 Plan 推导可测点

- 将 **Goal** 与 **Architecture** 中的结果承诺 → 顶层 **E2E / 验收** 用例。  
- 将 **File Map** 中的路由/文件 → **接口**或**组件**用例分区。  
- 将每个 **Task** 的 Step 描述（非纯粘贴代码）→ **步骤级**用例；同一行为在多个 Step 重复则合并。  
- 类型/接口代码块 → 与 `rules/mode_selection.md` 结合：多条件决定字段值 → 走服务端接口结构；仅 UI/流程 → 客户端结构。

### 忽略或降权

- 块引用 `> **For agentic workers:**` 及子技能名（与功能验收无关）。  
- 纯操作型说明：如「Replace the contents of」「Run pnpm test」— 不单独成用例，除非明确新的可测行为。  
- 大段实现代码：不逐行出用例；只抽 **契约** 与 **枚举/边界**（如 `status: 'in_progress' | 'completed' | 'claimed'` 每种一条覆盖思路）。

### 可选合并输入

- 同需求下若存在 `docs/superpowers/specs/*-design.md`（或用户在消息里一并给出），与 Plan **合并**为需求来源：Plan 偏实施边界，design 偏产品与交互约束；冲突时以 **design / 用户声明** 为准。

### 缺失处理

- 仅标题无 Goal/File Map → 提示补充同目录 design 或粘贴 Goal；仍无法收敛则停止生成并说明缺口。

---

## 飞书文档
- **触发条件**：链接为企业飞书 Wiki，主机名匹配 `*.feishu.cn`（示例：`https://wiki.example.feishu.cn/...`）
- **工具**：`mcp__feishu_wiki_mcp__feishu_get_doc_content`
- **缺失处理**：提示用户粘贴文档内容，配置见 `references/mcp_setup.md`

## Figma 设计稿
- **触发条件**：链接包含 `www.figma.com`
- **工具**：`mcp__Framelink_Figma_MCP__get_figma_data`
- **分析规则**：
  - 包含 `BEFORE`/`before` 的节点 → 旧样式，忽略
  - 包含 `AFTER`/`after` 的节点 → 新样式，分析
  - 包含"交互说明"的内容 → 结合 PRD 生成交互测试用例
- **缺失处理**：提示用户提供截图，配置见 `references/mcp_setup.md`

## 需求文档 / 技术方案（必需其一）

以下**至少一种**作为需求来源即可；可与 **OpenSpec `openspec/specs/.../spec.md`**、Superpowers plan、飞书、Figma 组合（组合时合并去重，冲突按「用户当前消息明确指定的文档」优先；与现行 spec 冲突时以 **openspec/specs 下现行 spec.md** 为准）。

### 需要分析的章节（目录标题含以下关键词）
- 需求、实验、方案、功能设计、交互设计

### 忽略的章节
目录标题含：项目背景、简介、埋点、附录、节奏
章节标题含：埋点、数据统计、指标、监控
其他：打了删除线的内容
