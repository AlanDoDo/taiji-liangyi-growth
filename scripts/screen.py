#!/usr/bin/env python3
"""Screen local stock data against the Taiji Liangyi six-criteria framework.

The script never fetches data from the network. It reads a user-provided CSV
or XLSX file, normalizes common Chinese/English column names, and reports
pass/fail/gap for the six criteria. Growth columns are expected in percent
units, for example 178 means 178%.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


COLUMN_ALIASES = {
    "name": ["name", "company", "公司", "公司名称", "标的", "股票"],
    "industry": ["industry", "行业", "所属行业", "板块"],
    "revenue_growth": [
        "revenue_growth",
        "营收增速",
        "营收同比",
        "revenue_yoy",
        "收入增速",
    ],
    "single_revenue_growth": [
        "single_revenue_growth",
        "单季营收增速",
        "q_revenue_yoy",
        "单季收入增速",
    ],
    "profit_growth": [
        "profit_growth",
        "归母增速",
        "净利增速",
        "净利润增速",
        "profit_yoy",
        "归母同比",
    ],
    "deducted_growth": [
        "deducted_growth",
        "扣非增速",
        "扣非净利增速",
        "deducted_yoy",
        "扣非同比",
    ],
    "single_profit_growth": [
        "single_profit_growth",
        "单季净利增速",
        "q_profit_yoy",
        "单季归母增速",
    ],
    "net_profit": ["net_profit", "净利润", "归母净利润", "net_profit_money"],
    "market_cap": ["market_cap", "市值", "总市值"],
    "price_vs_52w_high": [
        "price_vs_52w_high",
        "距52周高点",
        "距一年高点",
        "pct_of_52w_high",
        "距高点",
    ],
    "new_high": ["new_high", "一年新高", "创一年新高", "at_new_high", "新高"],
    "new_growth": ["new_growth", "新增长", "新产品", "新动能", "新业务"],
    "supply_demand": ["supply_demand", "供需", "供不应求", "强供需", "供需矛盾"],
    "imagination": ["imagination", "想象力", "空间", "天花板"],
    "management": ["management", "管理层", "增持", "管理层背书", "回购", "激励"],
    "notes": ["notes", "备注", "comment", "说明"],
}


def normalize_key(value: str) -> str:
    return (
        str(value)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .replace("（", "")
        .replace("）", "")
        .replace("(", "")
        .replace(")", "")
    )


def build_alias_map() -> dict[str, str]:
    alias_map: dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        alias_map[normalize_key(canonical)] = canonical
        for alias in aliases:
            alias_map[normalize_key(alias)] = canonical
    return alias_map


ALIAS_MAP = build_alias_map()

QUALITY_HINTS = {
    "并表": "提示：并表驱动，需用可比口径",
    "低基数": "提示：低基数，需看绝对额",
    "非经常": "提示：非经常性损益，需看扣非",
    "公允价值": "提示：公允价值/账面利润，主业单独看",
    "周期": "提示：周期属性，需拆量价与可持续性",
}


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return [dict(row) for row in reader]


def read_xlsx(path: Path, sheet: str | None) -> list[dict[str, Any]]:
    try:
        from openpyxl import load_workbook
    except ImportError as error:
        raise SystemExit(
            "读取 Excel 需要 openpyxl；请安装 openpyxl 或另存为 CSV。"
        ) from error

    workbook = load_workbook(path, read_only=True, data_only=True)
    worksheet = workbook[sheet] if sheet else workbook.active
    rows = list(worksheet.iter_rows(values_only=True))
    if not rows:
        return []

    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    records: list[dict[str, Any]] = []
    for row in rows[1:]:
        if all(cell is None or str(cell).strip() == "" for cell in row):
            continue
        record = {}
        for index, header in enumerate(headers):
            if header:
                record[header] = row[index] if index < len(row) else None
        records.append(record)
    return records


def read_input(path: Path, sheet: str | None) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return read_csv(path)
    if suffix in {".xlsx", ".xlsm"}:
        return read_xlsx(path, sheet)
    if suffix == ".xls":
        raise SystemExit("旧版 .xls 不支持；请另存为 .xlsx 或 .csv。")
    raise SystemExit(f"不支持的文件类型：{suffix}；请使用 .csv 或 .xlsx。")


def canonicalize_row(row: dict[str, Any]) -> dict[str, Any]:
    canonical: dict[str, Any] = {}
    extras: dict[str, Any] = {}
    for key, value in row.items():
        if key is None:
            continue
        canonical_key = ALIAS_MAP.get(normalize_key(str(key)))
        if canonical_key:
            canonical[canonical_key] = value
        else:
            extras[str(key)] = value
    canonical["extras"] = extras
    return canonical


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "").replace("，", "")
    if not text:
        return None
    if text.lower() in {"-", "—", "n/a", "na", "none", "null", "未知", "无", "不适用"}:
        return None

    multiplier = 1.0
    if text.endswith("亿"):
        text = text[:-1]
    elif text.endswith("万"):
        text = text[:-1]
        multiplier = 1e-4
    if text.endswith("%"):
        text = text[:-1]

    try:
        return float(text) * multiplier
    except ValueError:
        return None


def parse_tristate(value: Any) -> bool | str | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"yes", "y", "true", "1", "是", "有", "通过", "pass"}:
        return True
    if text in {"no", "n", "false", "0", "否", "无", "不通过", "fail"}:
        return False
    if text in {"partial", "部分", "部分满足", "partial "}:
        return "partial"
    return None


def format_percent(value: float | None) -> str:
    if value is None:
        return "缺口"
    return f"{value:.1f}%"


def assess_growth(row: dict[str, Any]) -> dict[str, str]:
    revenue = parse_number(row.get("revenue_growth"))
    single_revenue = parse_number(row.get("single_revenue_growth"))
    profit = parse_number(row.get("profit_growth"))
    deducted = parse_number(row.get("deducted_growth"))
    single_profit = parse_number(row.get("single_profit_growth"))
    net_profit = parse_number(row.get("net_profit"))

    growth_values = [
        value
        for value in [revenue, single_revenue, profit, deducted, single_profit]
        if value is not None
    ]
    if not growth_values:
        return {"status": "gap", "label": "缺口", "note": "缺增速数据"}
    if net_profit is not None and net_profit <= 0:
        return {"status": "fail", "label": "亏损", "note": "净利润 ≤ 0"}

    revenue_values = [value for value in [revenue, single_revenue] if value is not None]
    revenue_best = max(revenue_values) if revenue_values else None
    profit_best = max(
        [value for value in [profit, deducted, single_profit] if value is not None],
        default=None,
    )

    if revenue_best is None:
        if profit_best is not None and profit_best >= 40:
            return {
                "status": "gap",
                "label": "缺营收",
                "note": "利润/扣非高增，但缺营收增速；需补主营口径",
            }
        return {
            "status": "fail",
            "label": "增速<40%",
            "note": "缺营收且已知利润增速<40%",
        }

    detail = f"营收最高 {revenue_best:.1f}%"
    if profit_best is not None:
        detail += f"；利润/扣非最高 {profit_best:.1f}%"

    if revenue_best >= 40:
        return {"status": "pass", "label": "营收达标", "note": detail}
    if profit_best is not None and profit_best >= 40:
        return {
            "status": "fail",
            "label": "营收未达标",
            "note": detail + "；利润/扣非高增不能替代主营",
        }
    return {"status": "fail", "label": "增速<40%", "note": detail}


def assess_market(row: dict[str, Any]) -> dict[str, str]:
    new_high = parse_tristate(row.get("new_high"))
    drawdown = parse_number(row.get("price_vs_52w_high"))

    if new_high is True:
        if drawdown is not None and drawdown < -20:
            return {
                "status": "gap",
                "label": "数据冲突",
                "note": f"标记为新高，但距52周高点 {drawdown:.1f}%，请核对",
            }
        return {"status": "pass", "label": "命中", "note": "创一年新高"}
    if new_high is False:
        return {"status": "fail", "label": "未命中", "note": "未创一年新高"}
    if drawdown is None:
        return {"status": "gap", "label": "缺口", "note": "缺股价/52周高点"}
    if drawdown >= -20:
        return {
            "status": "gap",
            "label": "接近",
            "note": f"距52周高点 {drawdown:.1f}%，未确认新高",
        }
    return {"status": "fail", "label": "未命中", "note": f"距52周高点 {drawdown:.1f}%"}


def assess_flag(row: dict[str, Any], key: str) -> dict[str, str]:
    value = parse_tristate(row.get(key))
    if value is True:
        return {"status": "pass", "label": "命中", "note": ""}
    if value is False:
        return {"status": "fail", "label": "未命中", "note": ""}
    if value == "partial":
        return {"status": "gap", "label": "部分", "note": "部分满足，需补证据"}
    return {"status": "gap", "label": "缺口", "note": "缺数据"}


def assess_management(row: dict[str, Any]) -> dict[str, str]:
    value = parse_tristate(row.get("management"))
    if value is True:
        return {"status": "pass", "label": "命中", "note": "有增持/回购/激励"}
    if value is False:
        return {"status": "gap", "label": "未背书", "note": "第6条可放宽"}
    if value == "partial":
        return {"status": "gap", "label": "部分", "note": "第6条可放宽"}
    return {"status": "gap", "label": "缺口", "note": "第6条可放宽"}


def assess_company(row: dict[str, Any]) -> dict[str, Any]:
    growth = assess_growth(row)
    new_growth = assess_flag(row, "new_growth")
    supply_demand = assess_flag(row, "supply_demand")
    imagination = assess_flag(row, "imagination")
    market = assess_market(row)
    management = assess_management(row)

    hard_results = [growth, new_growth, supply_demand, imagination, market]
    hard_fail = any(item["status"] == "fail" for item in hard_results)
    material_gap = any(item["status"] == "gap" for item in hard_results)

    if hard_fail:
        conclusion = "不够格"
    elif material_gap:
        conclusion = "证据不足"
    elif management["status"] == "pass":
        conclusion = "够格"
    elif management["status"] == "gap":
        conclusion = "够格（管理层待验证）"
    else:
        conclusion = "够格（管理层可放宽）"

    note_parts = []
    if growth["note"]:
        note_parts.append(f"增长：{growth['note']}")
    if market["note"]:
        note_parts.append(f"市场认可：{market['note']}")
    if management["note"]:
        note_parts.append(f"管理层：{management['note']}")
    for label, item in [
        ("新增长", new_growth),
        ("供需", supply_demand),
        ("想象力", imagination),
    ]:
        if item["note"]:
            note_parts.append(f"{label}：{item['note']}")
    user_note = row.get("notes")
    if user_note:
        note_parts.insert(0, str(user_note))
    hint_text = " ".join(str(row.get(key, "")) for key in ["name", "industry", "notes"])
    for keyword, message in QUALITY_HINTS.items():
        if keyword in hint_text:
            note_parts.append(message)

    return {
        "公司": row.get("name") or "未命名",
        "行业": row.get("industry") or "未标行业",
        "增速": f"营收 {format_percent(parse_number(row.get('revenue_growth')))}"
        f" / 扣非 {format_percent(parse_number(row.get('deducted_growth')))}",
        "增长判定": growth["label"],
        "新增长": new_growth["label"],
        "供需": supply_demand["label"],
        "想象力": imagination["label"],
        "市场认可": market["label"],
        "管理层": management["label"],
        "结论": conclusion,
        "说明": "；".join(part for part in note_parts if part),
    }


def render_markdown(rows: list[dict[str, Any]], as_of: str, source: str) -> str:
    headers = [
        "公司",
        "行业",
        "增速",
        "增长判定",
        "新增长",
        "供需",
        "想象力",
        "市场认可",
        "管理层",
        "结论",
        "说明",
    ]
    lines = [
        f"数据截止：{as_of}",
        f"数据来源：{source}",
        "",
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for row in rows:
        values = [str(row.get(header, "")).replace("|", "/") for header in headers]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def render_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    from io import StringIO

    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def print_template() -> None:
    print(
        "公司,行业,营收增速,单季营收增速,归母增速,扣非增速,单季净利增速,"
        "净利润,市值,距52周高点,一年新高,新增长,供需,想象力,管理层,备注"
    )


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="用本地 CSV/Excel 做太极两仪六条标准初筛；不联网、不构成投资建议。"
    )
    parser.add_argument("--input", type=Path, help="CSV 或 XLSX 文件路径")
    parser.add_argument("--sheet", help="XLSX 工作表名，默认第一个")
    parser.add_argument("--as-of", default="未提供", help="数据截止日，如 2026-11-13")
    parser.add_argument("--source", default="用户输入", help="数据来源说明")
    parser.add_argument(
        "--format", choices=["markdown", "csv", "json"], default="markdown"
    )
    parser.add_argument("--template", action="store_true", help="打印 CSV 列模板")
    args = parser.parse_args()

    if args.template:
        print_template()
        return
    if not args.input:
        parser.error("需要 --input，或使用 --template 查看模板")
    if not args.input.exists():
        raise SystemExit(f"文件不存在：{args.input}")

    raw_rows = read_input(args.input, args.sheet)
    screened = [assess_company(canonicalize_row(row)) for row in raw_rows]

    if args.format == "markdown":
        print(render_markdown(screened, args.as_of, args.source))
        return
    if args.format == "csv":
        sys.stdout.write(render_csv(screened))
        return
    print(
        json.dumps(
            {"as_of": args.as_of, "source": args.source, "results": screened},
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
