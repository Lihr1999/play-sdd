---
name: TDD 生成核心测试用例
description: 根据需求文档、Figma、技术方案、OpenSpec（openspec/specs/…/spec.md）、Superpowers 实施计划（docs/superpowers/plans）等输入生成核心测试用例与测试 spec。用户要测试用例、测试 spec、TDD 测试文档时触发。
---

## 概述
根据需求文档、设计稿、技术方案、**OpenSpec spec.md**、**Superpowers Implementation Plan** 等输入自动生成测试用例，帮助 QA 快速构建用例集合。

## 工作流程

```
0. 版本检测
 → 1. 输入源路由（飞书/Figma MCP｜openspec/specs/…/spec.md｜Superpowers plan｜用户粘贴）
 → 2. 输入解析（按 input_sources 规则提取可测点）
 → 3. 内容获取
 → 4. 用例生成（按 `rules/mode_selection.md` 定模式）
 → 5. 输出 Markdown
 → 6. 生成 XMind
```

---

## MCP 工具依赖

| 工具名称 | 工具标识 | 触发条件 |
|---------|---------|---------|
| 飞书文档MCP | `mcp__feishu_wiki_mcp` | 链接含企业飞书 Wiki（`*.feishu.cn`） |
| Figma MCP | `mcp__Framelink_Figma_MCP` | 链接含 `www.figma.com` |
| 造数MCP | `Community_AI_Data_Tool` | 需要构造测试数据时 |

**本地文件（无 MCP）**  
- `openspec/specs/<能力名>/spec.md`：见 `input_sources` 中 OpenSpec 节。  
- `docs/superpowers/plans/**/*.md`：Superpowers 实施计划。

---

## 规则

- **输入源处理**：`rules/input_sources.md`（飞书/Figma/需求文档/**OpenSpec spec.md**/**Superpowers plan**）
- **用例生成约束**：`rules/generation_rules.md`（埋点剔除、内容来源限制）
- **测试模式选择**：`rules/mode_selection.md`（根据需求类型选择客户端/服务端/A·B实验模式）
- **服务端接口测试**：`rules/server_interface_rules.md`（判定表法、等价类划分、接口测试文档结构）
- **A/B 实验测试**：`rules/ab_experiment_rules.md`（四步法、页面覆盖三层分类、覆盖度自查）

---

## 输出格式

### 测试用例字段
| 字段 | 说明 |
|------|------|
| ID | 唯一标识符 |
| 标题 | 测试用例标题 |
| 描述 | 详细描述 |
| 前置条件 | 执行依赖 |
| 执行步骤 | 具体步骤 |
| 预期结果 | 成功标准 |
| 端 | 服务端/客户端 |
| 优先级 | P0/P1/P2 |

### 文档结构（客户端/功能测试）
```markdown
# {需求名称}测试用例

## 一、测试概述
### 1.1 测试范围
### 1.2 测试环境

## 二、{模块名称}测试用例
### TC-001: {测试项名称}
| 用例ID | 测试项 | 前置条件 | 测试步骤 | 预期结果 | 优先级 |
...

## 测试用例统计
```

### 文档结构（服务端接口测试）

当需求涉及**服务端接口字段逻辑**（如接口返回值由多条件组合决定）时，使用以下结构：

```markdown
# {需求名称}测试用例

## 一、测试概述
### 1.1 测试范围
### 1.2 接口说明
- 接口、被测字段、依赖算法字段、异常兜底逻辑

### 1.3 核心判断逻辑（伪代码）
### 1.4 测试设计方法论说明（判定表法 / 等价类划分 / 错误推测法）
### 1.5 Mock 测试方案（T1环境 mock 配置步骤）

## 二、判定表（决策路径全覆盖）
> 穷举所有条件组合，每行对应一条用例

| 规则 | C1: 条件A | C2: 条件B | ... | 预期结果 | 用例 |

## 三、测试用例
> 接口：`/xxx`，验证字段：`fieldName`

| 用例ID | 测试项 | 设计方法 | Mock: 字段A | Mock: 字段B | 预期结果 | 优先级 |
|--------|--------|---------|------------|------------|---------|--------|
| TC-001 | ...    | 等价类   | `"值"`     | `"值"`     | `true`  | P0     |
...

## 四、测试用例统计
```

**接口测试用例表格设计原则：**
- 所有用例合并为一张横向表格（不拆分为多个竖表）
- Mock 的多个字段各占独立一列，便于对比
- 设计方法列标注：等价类 / 判定表 / 错误推测
- 枚举类型的每个枚举值单独一行（独立等价类，需逐一覆盖）
- 异常/兜底场景（字段缺失、非枚举值）单独成行，标注兜底逻辑

参考示例：`references/测试spec示例.md`（含接口测试示例）

---

## XMind 输出

### 生成步骤

Markdown 文档生成完毕后，自动将用例数据转换为 XMind 格式：

**调用脚本**（优先使用本仓库内技能目录；若仅全局安装再改用 `~/.claude/skills/...`）：

```bash
python3 .cursor/skills/tdd-test-spec-skill/scripts/generate_xmind.py \
  --output "{输出路径}/{需求名称}-测试用例.xmind" \
  --title "{需求名称}-测试用例" \
  --cases '{JSON格式的用例数据}'
```

**用例数据 JSON 格式：**

详见 `references/xmind_cases_format.md`（含两种格式说明与字段定义）。

**XMind 层级结构：**
```
{需求名称}-测试用例
├── 模块名称测试用例 (N条)
│   ├── 场景名称
│   │   └── TC-001 用例标题 [P0]
│   │       ├── 前置条件: ...
│   │       ├── 步骤1: ...
│   │       ├── 步骤2: ...
│   │       ├── 测试数据: ...
│   │       └── 预期结果: ...
│   └── ...
└── ...
```

### 输出文件位置

输出到**当前工作目录**，不创建子目录：

```
{当前目录}/
├── {需求名称}-测试spec.md         # Markdown格式
└── {需求名称}-TDD测试用例.xmind   # XMind格式
```

参考示例：`references/xmind用例示例.mm`

---

## 默认配置

| 配置项 | 默认值 |
|-------|-------|
| 测试环境 | T1 |
| 测试账号 | 使用造数MCP工具获取 |

---
