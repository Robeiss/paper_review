from __future__ import annotations


PREVIOUS_VERSION = {
    "id": "2026-undergraduate-draft",
    "name": "2026届本科毕业论文格式要求草案",
    "publishedAt": "2026-05-20",
    "source": "学院格式说明草案",
    "changes": [
        "正文行距未统一到最终要求",
        "图表编号规则尚未明确",
        "参考文献格式说明较简略",
    ],
}

CURRENT_VERSION = {
    "id": "2026-undergraduate-v1",
    "name": "2026届本科毕业论文格式要求 V1",
    "publishedAt": "2026-06-01",
    "source": "教务处格式通知示例",
    "changes": [
        "统一正文行距和首行缩进要求",
        "补充图题、表题、公式编号展示规则",
        "增加参考文献常见错误提示",
    ],
}

RULE_CHANGES = [
    {
        "ruleId": "rule.body",
        "title": "正文行距统一",
        "previous": "正文行距允许使用固定值或 1.5 倍行距。",
        "current": "正文统一使用 1.5 倍行距，首行缩进 2 字符。",
        "impact": "已经排版完成的正文需要重点复查，尤其是复制粘贴后的段落样式。",
        "risk": "high",
    },
    {
        "ruleId": "rule.figure",
        "title": "图题位置明确",
        "previous": "图题位置未单独强调。",
        "current": "图题置于图下方，五号宋体，居中。",
        "impact": "图较多的论文需要逐个检查图题位置和编号。",
        "risk": "medium",
    },
    {
        "ruleId": "rule.table",
        "title": "表题位置明确",
        "previous": "表格样式仅要求清晰。",
        "current": "表题置于表上方，优先使用三线表。",
        "impact": "表格较多时返工成本较高，应在打印前集中检查。",
        "risk": "medium",
    },
    {
        "ruleId": "rule.references",
        "title": "参考文献补充常见错误",
        "previous": "仅说明按学校引用标准执行。",
        "current": "补充标点、卷期、页码和访问日期等常见错误提示。",
        "impact": "文献条目需要和正文引用一起核对，避免终稿阶段批量修改。",
        "risk": "high",
    },
    {
        "ruleId": "rule.toc",
        "title": "目录更新提醒",
        "previous": "目录样式要求较简略。",
        "current": "强调最终打印前必须更新目录域和页码。",
        "impact": "修改标题或分页后，需要在导出 PDF 前重新更新目录。",
        "risk": "high",
    },
]


def get_rule_version_payload() -> dict:
    return {
        "previousVersion": PREVIOUS_VERSION,
        "currentVersion": CURRENT_VERSION,
        "ruleChanges": RULE_CHANGES,
    }
