# Figma 原型分析方法

## Token 获取(自动优先)

1. 读 `~/.zcode/cli/config.json` → `mcp.servers.figma-dev.env.FIGMA_API_KEY`
2. 读不到 → 问用户要 personal access token
3. 都没有 → 请用户导出截图/文本,走降级路径(不阻塞)

## REST API 用法(base: https://api.figma.com/v1,header: X-Figma-Token)

| 目的 | 调用 | 说明 |
|---|---|---|
| 文件页面结构 | GET /files/{key}?depth=2 | key 从 URL `/design/<key>/` 提取 |
| 指定 Frame | GET /files/{key}/nodes?ids=1:234,5:678 | 一次可逗号多个 |
| 图片 | GET /images/{key}?ids=... | 需要视觉细节时 |

优先用配套脚本:`python scripts/figma_fetch.py <figma_url> --pages` 等,免手写。

## 提取方法(实战验证)

1. **选版本页面**:文件常有多版本页(V1.0/V1.1/V1.2/草稿)——**用最新正式版**,
   草稿页(名字带 草稿/draft)排除;不确定哪个最新就问用户。
2. **遍历顶层 Frame**:Frame 名即功能名(中文常见:「搜索」「创建SFT-基础信息」「导航栏」),
   每个交互型 Frame → 候选功能点。
3. **提取文本**:递归 walk nodes,type==TEXT 的 characters 去重收集。
   文本就是素材:placeholder=输入约束、按钮名=操作、Tab名+计数=结果结构、
   错误文案(Frmae 里孤立的提示句)=异常预期。
4. **识别控件类型**(按子节点构成推断):
   - 输入框:Rectangle+placeholder文本 → 边界用例来源
   - Tab/分段:多个短文本并列(常带计数 all(61)/Tokens(20)) → 分类切换用例
   - 列表:重复结构的 Group(n) → 行字段与跳转用例
   - 状态对(Frame名含 成功/失败/加载中/空) → 状态机用例
5. **原型画不了的信息主动标注**:交互触发方式(防抖/回车)、接口行为、边界数值
   ——这些进悬置项,不编造。

## 注意

- Figma URL 的 node-id 是 `0-1` 格式,API 要转 `0:1`(横杠换冒号)
- 1s 级 K线类数据源比对不可行(保留期短),只比结构与字段
- 拿到的所有 Frame ID 记进用例备注列,形成追溯
