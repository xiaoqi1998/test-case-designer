# test-case-designer

测试用例设计器 skill(ZCode / Claude Code 通用):把 **原型图(Figma)、PRD、接口文档、智能合约**
四类素材变成可执行、可追溯、不漏关键风险的测试用例。

只管**设计生成**;执行测试/提缺陷/出报告请配合作者另一个 skill `qa-testing` 接力。

## 核心特性

- **业务理解门槛**:先生成三色置信度(✅依据/🔶推测/❓不懂)的业务理解文档给用户核对,
  确认前禁止写用例——理解错了后面全错
- **不确定坚决不猜**(铁律0):无依据的预期留空标【待确认】,归入悬置项等用户拍板;
  允许一层 Oracle 显式推导(一致性/历史/声明/惯例)且必须标注类型
- **四层展开**:功能 9 维(正向/边界/异常/并发/权限/一致性/配置/状态机/安全)
  + 业务流程层(主/备/异常流 × 6 种 E2E)+ 非功能 3 维(ISO 25010 裁剪)
  + CRUD×权限实体矩阵
- **双格式输出**:xlsx(11 列 + 实际结果列 pass/fail/skip/block 四色下拉,只能选)
  或 pytest(断言动态读配置、失败零副作用断言)
- **追溯防漏**:功能点→用例映射 sheet + 覆盖核对脚本,漏测格红字标出
- **实战沉淀**:数值不硬编码、破坏性操作探测式验证、配置写快照还原等铁律
  全部来自真实踩坑(详见 references/feedback.md)

## 安装

```bash
git clone <本仓库>
# 方式一:个人全局(所有项目可用)
cp -r test-case-designer ~/.agents/skills/
# 方式二:项目级
cp -r test-case-designer <你的项目>/.agents/skills/
```

依赖(Python 3.10+):`openpyxl`(xlsx 写入);Figma 取数可选,token 自动从
`~/.zcode/cli/config.json` 读取,读不到时会提示输入。

## 使用

对 ZCode / Claude Code 说:

> 分析这个 Figma 原型 <链接>,结合 PRD <路径>,先给我业务理解,确认后写测试用例输出 xlsx

或触发词:写测试用例 / 设计用例 / 测试点分析 / 补充用例 / 合约测试点。

## 目录结构

```text
test-case-designer/
├── SKILL.md                 # 7 步工作流 + 铁律(入口)
├── references/
│   ├── business-flow.md     # 第10维:业务理解文档模板 + 流程层方法
│   ├── test-dimensions.md   # 9+4 维清单 + Oracle 测试预言
│   ├── case-formats.md      # xlsx 11列/优先级规则/pytest模板
│   ├── figma-analysis.md    # Figma REST 取数方法
│   ├── prd-analysis.md      # 验收矩阵/规则句式/模糊词/事件流
│   ├── api-analysis.md      # 接口契约分析方法
│   ├── contract-analysis.md # 合约(函数/权限/事件)分析方法
│   └── feedback.md          # 用户纠正沉淀(持续完善)
├── scripts/
│   ├── figma_fetch.py       # Figma 拉取(pages/frames/texts/tree)
│   ├── xlsx_writer.py       # 用例追加 + 四色下拉 + 追溯sheet
│   └── trace_check.py       # 覆盖核对(功能点/维度/优先级)
└── assets/
    └── case_template.xlsx   # 11列模板(下拉已配)
```

## 与 qa-testing 的分工

| | test-case-designer | qa-testing |
|---|---|---|
| 职责 | 设计生成(素材→用例) | 执行与交付(执行/缺陷/报告) |
| 触发 | 写用例/测试点/业务梳理 | 跑测试/提缺陷/出报告 |

连续意图("写用例并执行")时:本 skill 先行,qa-testing 接力执行段。

## License

MIT
