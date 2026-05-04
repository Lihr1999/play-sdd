#!/usr/bin/env python3
"""
测试用例 XMind 生成脚本（新版 JSON 格式）

参考 FreeMind .mm 格式：
  - 模块级节点（level 1）：bubble 样式 —— 彩色圆角矩形，加粗白字
  - 子节点（level 2+）：fork 样式 —— 无背景，仅连接线

支持两种数据格式：
  1. scenarios 分组: {"category": "...", "scenarios": {"场景名": [case, ...]}}
  2. cases 列表:     {"category": "...", "cases": [case, ...]}

每条 case 字段:
  id, title, priority, precondition, steps (list), testData, expectedResult

使用方法:
  python3 generate_xmind.py --output out.xmind --title "标题" --cases '[...]'
"""

import zipfile
import os
import json
import argparse
import uuid
from xml.sax.saxutils import escape

# ── 颜色配置（参考 FreeMind/XMind 默认配色盘） ────────────
MODULE_COLORS = [
    ("#4472C4", "#FFFFFF"),  # 蓝
    ("#ED7D31", "#FFFFFF"),  # 橙
    ("#70AD47", "#FFFFFF"),  # 绿
    ("#FF4B4B", "#FFFFFF"),  # 红
    ("#7030A0", "#FFFFFF"),  # 紫
    ("#00B0F0", "#FFFFFF"),  # 浅蓝
    ("#FFC000", "#000000"),  # 黄
    ("#C00000", "#FFFFFF"),  # 深红
]

FORK_STYLE = {
    "type": "topic",
    "properties": {
        "shape-class": "org.xmind.topicShape.noshape",
    },
}


def new_id() -> str:
    return str(uuid.uuid4())


def bubble_style(index: int) -> dict:
    fill, text = MODULE_COLORS[index % len(MODULE_COLORS)]
    return {
        "type": "topic",
        "properties": {
            "shape-class": "org.xmind.topicShape.roundedRect",
            "fill-color": fill,
            "fo:color": text,
            "fo:font-weight": "bold",
            "line-color": fill,
        },
    }


# ── 节点构建 ──────────────────────────────────────────────

def leaf(title: str) -> dict:
    """最末层节点（步骤、前置条件、预期结果等），fork 样式"""
    return {"id": new_id(), "class": "topic", "title": title, "style": FORK_STYLE}


def case_node(case: dict) -> dict:
    """单条测试用例节点（level 2），fork 样式"""
    tc_id = case.get("id", "TC-?")
    title = case.get("title", "未命名用例")
    priority = case.get("priority", "P2")
    precondition = case.get("precondition", "")
    steps = case.get("steps", [])
    test_data = case.get("testData", "")
    expected = case.get("expectedResult", "")

    children = []
    if precondition:
        children.append(leaf(f"前置条件: {precondition}"))
    for i, step in enumerate(steps, 1):
        children.append(leaf(f"步骤{i}: {step}"))
    if test_data:
        children.append(leaf(f"测试数据: {test_data}"))
    if expected:
        children.append(leaf(f"预期结果: {expected}"))

    node = {
        "id": new_id(),
        "class": "topic",
        "title": f"{tc_id}: {title} [{priority}]",
        "style": FORK_STYLE,
    }
    if children:
        node["children"] = {"attached": children}
    return node


def scenario_node(name: str, cases: list) -> dict:
    """场景分组节点（level 2，有 scenarios 时使用），fork 样式"""
    node = {
        "id": new_id(),
        "class": "topic",
        "title": name,
        "style": FORK_STYLE,
    }
    if cases:
        node["children"] = {"attached": [case_node(c) for c in cases]}
    return node


def category_node(category: dict, color_index: int) -> dict:
    """模块分类节点（level 1），bubble 样式"""
    name = category.get("category", "未分类")
    scenarios = category.get("scenarios", {})
    cases = category.get("cases", [])

    # 统计总用例数
    total = sum(len(v) for v in scenarios.values()) if scenarios else len(cases)
    title = f"{name} ({total}条)"

    children = []
    if scenarios:
        for sc_name, sc_cases in scenarios.items():
            children.append(scenario_node(sc_name, sc_cases))
    else:
        for c in cases:
            children.append(case_node(c))

    node = {
        "id": new_id(),
        "class": "topic",
        "title": title,
        "style": bubble_style(color_index),
    }
    if children:
        node["children"] = {"attached": children}
    return node


# ── 文件内容构建 ──────────────────────────────────────────

def build_content_json(title: str, cases_data: list) -> str:
    root = {
        "id": new_id(),
        "class": "topic",
        "title": title,
        "structureClass": "org.xmind.ui.map.unbalanced",
        "children": {
            "attached": [
                category_node(cat, i) for i, cat in enumerate(cases_data)
            ]
        },
    }
    sheet = {
        "id": new_id(),
        "class": "sheet",
        "title": "Sheet 1",
        "rootTopic": root,
    }
    return json.dumps([sheet], ensure_ascii=False, indent=2)


def build_metadata_json() -> str:
    return json.dumps(
        {
            "dataStructureVersion": "3",
            "creator": {"name": "TestGen", "version": "1.4.1"},
            "layoutEngineVersion": "5",
        },
        ensure_ascii=False,
    )


def build_manifest_json() -> str:
    return json.dumps(
        {"file-entries": {"content.json": {}, "metadata.json": {}}},
        ensure_ascii=False,
    )


def build_content_xml_compat(title: str) -> str:
    """旧版 XMind 兼容占位（不含实际内容，仅提示）"""
    t = escape(title)
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'
        '<xmap-content xmlns="urn:xmind:xmap:xmlns:content:2.0" version="2.0">\n'
        '<sheet id="sheet_compat">\n'
        f'<title>{t}</title>\n'
        '<topic id="root_compat">\n'
        f'<title>{t} (请使用 XMind 2022 或更高版本打开)</title>\n'
        '</topic>\n'
        '</sheet>\n'
        '</xmap-content>'
    )


# ── 打包 .xmind ───────────────────────────────────────────

def create_xmind(output_path: str, title: str, cases_data: list) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("content.json", build_content_json(title, cases_data))
        zf.writestr("metadata.json", build_metadata_json())
        zf.writestr("manifest.json", build_manifest_json())
        zf.writestr("content.xml", build_content_xml_compat(title))

    return output_path


# ── 命令行入口 ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="生成 XMind 测试用例文件（新版 JSON 格式）")
    parser.add_argument("--output", required=True, help="XMind 文件输出路径")
    parser.add_argument("--title", required=True, help="根节点标题")
    parser.add_argument("--cases", required=True, help="JSON 格式的用例数据")
    args = parser.parse_args()

    try:
        cases_data = json.loads(args.cases)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        return 1

    try:
        path = create_xmind(args.output, args.title, cases_data)
        total = sum(
            sum(len(v) for v in c.get("scenarios", {}).values())
            if c.get("scenarios")
            else len(c.get("cases", []))
            for c in cases_data
        )
        print(f"✅ XMind 文件已生成: {path}")
        print(f"   用例总数: {total}  |  文件大小: {os.path.getsize(path)} bytes")
        return 0
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
