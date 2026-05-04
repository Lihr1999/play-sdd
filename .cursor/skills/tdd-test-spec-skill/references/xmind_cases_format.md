# XMind 用例数据格式

`generate_xmind.py` 脚本接受两种 JSON 格式：

## 格式1：scenarios 分组（推荐）

```json
[
  {
    "category": "模块名称测试用例",
    "scenarios": {
      "场景名称": [
        {
          "id": "TC-001",
          "title": "用例标题",
          "priority": "P0",
          "precondition": "前置条件",
          "steps": ["步骤1", "步骤2"],
          "testData": "测试数据",
          "expectedResult": "预期结果"
        }
      ]
    }
  }
]
```

## 格式2：cases 列表（无场景分组）

```json
[
  {
    "category": "模块名称测试用例",
    "cases": [
      {
        "id": "TC-001",
        "title": "用例标题",
        "priority": "P0",
        "precondition": "前置条件",
        "steps": ["步骤1", "步骤2"],
        "testData": "测试数据",
        "expectedResult": "预期结果"
      }
    ]
  }
]
```

## 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| category | string | 是 | 模块名称，显示为一级气泡节点 |
| scenarios | object | 否 | 场景分组，key 为场景名，value 为用例数组 |
| cases | array | 否 | 无场景分组时直接列用例 |
| id | string | 是 | 用例ID，如 TC-001 |
| title | string | 是 | 用例标题 |
| priority | string | 是 | P0 / P1 / P2 |
| precondition | string | 否 | 前置条件 |
| steps | array | 否 | 执行步骤列表 |
| testData | string | 否 | 测试数据 |
| expectedResult | string | 否 | 预期结果 |

## 生成的 XMind 层级结构

```
{需求名称}-测试用例
├── 模块名称测试用例 (N条)           ← bubble 样式（彩色圆角矩形）
│   ├── 场景名称                     ← fork 样式
│   │   └── TC-001 用例标题 [P0]    ← fork 样式
│   │       ├── 前置条件: ...
│   │       ├── 步骤1: ...
│   │       ├── 测试数据: ...
│   │       └── 预期结果: ...
│   └── ...
└── ...
```

参考示例：`references/xmind用例示例.mm`
