# -*- coding: utf-8 -*-
"""xlsx 用例写入器 —— test-case-designer skill 配套脚本。

用法:
    python xlsx_writer.py --target 模板.xlsx --cases cases.json
    # cases.json: [{id,mod1,mod2,title,priority,pre,steps,expect,note}, ...]
    #             另支持 --features F1,F2,... 生成追溯 sheet

功能:
    1. 追加用例到「测试用例」sheet(保留原表样式,从末行复制格式)
    2. 「实际结果」列(I列)强制下拉单选 pass/fail/skip/block + 四色条件格式
       (pass=绿 / fail=红 / skip=灰 / block=黄;手输其他值被 Excel 拦截)
    3. --features 时额外生成/更新「追溯」sheet:功能点→用例编号映射
"""
import argparse
import json
import os
import sys

import openpyxl
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation
from copy import copy

HEADERS = ["用例编号", "一级模块", "二级模块", "用例标题", "优先级",
           "前置条件", "操作步骤", "预期结果", "实际结果", "测试结论", "备注"]
VERDICT_COL = "I"  # 实际结果列(第9列)
VERDICTS = {"pass": ("C6EFCE", "006100"), "fail": ("FFC7CE", "9C0006"),
            "skip": ("E7E6E6", "595959"), "block": ("FFEB9C", "9C6500")}


def ensure_verdict_dropdown(ws):
    """给实际结果列装四选项下拉+四色。
    幂等且自愈:原表可能已有旧版下拉(如仅 pass/fail/skip)——
    不匹配目标配置的旧数据验证一律删除后重建,避免新旧并存取到旧值。"""
    rng = "%s2:%s5000" % (VERDICT_COL, VERDICT_COL)
    target = '"pass,fail,skip,block"'
    # 清理不匹配的旧验证(可能多个)
    keep = []
    for dv in ws.data_validations.dataValidation:
        if dv.type == "list" and str(VERDICT_COL) in str(dv.sqref) \
                and (dv.formula1 or "") != target:
            continue  # 丢弃旧版
        keep.append(dv)
    ws.data_validations.dataValidation = keep
    if not any(dv.type == "list" and (dv.formula1 or "") == target
               for dv in ws.data_validations.dataValidation):
        dv = DataValidation(
            type="list", formula1=target,
            allow_blank=True, showErrorMessage=True, errorStyle="stop",
            errorTitle="只能选择", error="请从下拉列表选择:pass / fail / skip / block")
        ws.add_data_validation(dv)
        dv.add(rng)
    # 条件格式:四色重建(重复添加同值规则无副作用,Excel 只应用一次)
    for value, (bg, fg) in VERDICTS.items():
        ws.conditional_formatting.add(rng, CellIsRule(
            operator="equal", formula=['"%s"' % value],
            fill=PatternFill(start_color=bg, end_color=bg, fill_type="solid"),
            font=Font(color=fg)))


def append_cases(ws, cases):
    last = ws.max_row
    tpl = {c: ws.cell(row=last, column=c) for c in range(1, len(HEADERS) + 1)}
    r = last + 1
    for case in cases:
        vals = [case.get("id", ""), case.get("mod1", ""), case.get("mod2", ""),
                case.get("title", ""), case.get("priority", ""), case.get("pre", ""),
                case.get("steps", ""), case.get("expect", ""), "", "", case.get("note", "")]
        for col, v in enumerate(vals, 1):
            src, dst = tpl[col], ws.cell(row=r, column=col, value=v)
            dst.font = copy(src.font); dst.border = copy(src.border)
            dst.fill = copy(src.fill); dst.alignment = copy(src.alignment)
        r += 1
    return len(cases)


def write_trace_sheet(wb, features, cases):
    """功能点→用例编号 追溯 sheet(存在则清空重写)。"""
    name = "追溯"
    if name in wb.sheetnames:
        ws = wb[name]
        ws.delete_rows(1, ws.max_row)
    else:
        ws = wb.create_sheet(name)
    ws.append(["功能点", "覆盖用例", "用例数"])
    for f in features:
        hits = [c["id"] for c in cases if f in (c.get("mod2", "") + c.get("title", ""))]
        ws.append([f, ", ".join(hits) if hits else "⚠️ 未覆盖", len(hits)])
    from openpyxl.styles import Font as F
    for row in ws.iter_rows(min_row=2, min_col=3, max_col=3):
        for cell in row:
            if cell.value == 0:
                cell.font = F(color="9C0006", bold=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", required=True, help="目标 xlsx(不存在则按模板表头新建)")
    ap.add_argument("--cases", required=True, help="用例 JSON 文件路径")
    ap.add_argument("--features", default=None, help="逗号分隔功能点清单,生成追溯sheet")
    args = ap.parse_args()

    cases = json.load(open(args.cases, encoding="utf-8"))
    if os.path.exists(args.target):
        wb = openpyxl.load_workbook(args.target)
        ws = wb["测试用例"] if "测试用例" in wb.sheetnames else wb.active
    else:
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "测试用例"
        ws.append(HEADERS)

    n = append_cases(ws, cases)
    ensure_verdict_dropdown(ws)
    if args.features:
        write_trace_sheet(wb, [f.strip() for f in args.features.split(",")], cases)
    wb.save(args.target)
    print("OK 追加 %d 条 -> %s(实际结果列已启用下拉+四色)%s"
          % (n, args.target, ";含追溯sheet" if args.features else ""))


if __name__ == "__main__":
    main()
