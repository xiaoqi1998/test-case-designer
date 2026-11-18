# -*- coding: utf-8 -*-
"""覆盖核对器 —— test-case-designer skill 配套脚本。

用法:
    python trace_check.py --cases cases.json [--features F1,F2] [--markdown out.md]

功能(注意:维度命中为关键词启发式,仅作漏测提示——
    "未覆盖"不代表一定漏,人工复核;标题措辞改变会导致误报/漏报):
    1. 功能点覆盖:每功能点用例数(0 条 = ⚠️ 漏测)
    2. 维度覆盖:按用例标题/预期关键词推断 10 维(9+业务流程)命中情况
    3. 优先级分布统计
输出控制台报告;--markdown 同时写文件。

维度关键词映射(命中任一即算该维有覆盖):
    正向: 成功|创建|正常|展示|查询
    边界: 边界|长度|精度|上限|下限|为空|空格|大小写|超长|科学计数
    异常: 失败|错误|拒绝|无效|非法|异常|超时|报错|不存在
    并发: 并发|幂等|重复提交|连点|重放
    权限: 权限|越权|无权|403|角色|跨用户|伪造
    一致性: 一致|守恒|恒等|对账|核对|分录|相等
    配置: 配置|联动|后台改|还原|快照
    状态机: 状态|流转|终态|跳转|取消|过期|回退
    安全: XSS|转义|泄露|安全|注入
    流程: 端到端|E2E|旅程|全流程|生命周期|主线
"""
import argparse
import json
import re

DIM_KEYWORDS = {
    "正向": r"成功|创建|正常|展示|查询|列表|详情",
    "边界": r"边界|长度|精度|上限|下限|为空|空格|大小写|超长|科学计数|负数",
    "异常": r"失败|错误|拒绝|无效|非法|异常|超时|报错|不存在|拦截",
    "并发": r"并发|幂等|重复提交|连点|重放|双击",
    "权限": r"权限|越权|无权|403|角色|跨用户|伪造|停用",
    "一致性": r"一致|守恒|恒等|对账|核对|分录|相等|合计",
    "配置": r"配置|联动|后台改|还原|快照|expectedVersion",
    "状态机": r"状态|流转|终态|跳转|取消|过期|回退|RESET",
    "安全": r"XSS|转义|泄露|安全|注入|script",
    "流程": r"端到端|E2E|旅程|全流程|生命周期|主线|全链",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", required=True)
    ap.add_argument("--features")
    ap.add_argument("--markdown")
    args = ap.parse_args()

    cases = json.load(open(args.cases, encoding="utf-8"))
    lines = []
    P = lines.append
    P("# 覆盖核对报告")
    P("")

    # 功能点覆盖
    if args.features:
        feats = [f.strip() for f in args.features.split(",")]
        P("## 功能点覆盖")
        P("")
        P("| 功能点 | 用例数 | 状态 |")
        P("|---|---:|---|")
        miss = 0
        for f in feats:
            n = sum(1 for c in cases if f in (str(c.get("mod2", "")) + str(c.get("title", ""))))
            tag = "✅" if n else "⚠️ 漏测"
            miss += 0 if n else 1
            P("| %s | %d | %s |" % (f, n, tag))
        P("")
        P("漏测功能点:**%d**" % miss)
        P("")

    # 维度覆盖
    P("## 维度覆盖(按关键词推断)")
    P("")
    P("| 维度 | 命中用例数 | 状态 |")
    P("|---|---:|---|")
    hay = "\n".join(str(c.get("title", "")) + str(c.get("expect", ""))
                    + str(c.get("steps", "")) for c in cases)
    miss_dim = 0
    for dim, pat in DIM_KEYWORDS.items():
        n = len(re.findall(pat, hay, re.I))
        tag = "✅" if n else "⚠️ 无覆盖"
        miss_dim += 0 if n else 1
        P("| %s | %d | %s |" % (dim, n, tag))
    P("")
    P("未覆盖维度:**%d**" % miss_dim)
    P("")

    # 优先级分布
    P("## 优先级分布")
    P("")
    from collections import Counter
    pc = Counter(str(c.get("priority", "?")) for c in cases)
    P("| 优先级 | 数量 |")
    P("|---|---:|")
    for k in ("P0", "P1", "P2"):
        if pc.get(k):
            P("| %s | %d |" % (k, pc[k]))
    P("")
    P("**用例总数:%d**" % len(cases))

    report = "\n".join(lines)
    print(report)
    if args.markdown:
        open(args.markdown, "w", encoding="utf-8").write(report)
        print("\n已写入: %s" % args.markdown)


if __name__ == "__main__":
    main()
