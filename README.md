# 太极两仪 · 成长股研究体系

> 先分两仪，再看四象，再用六条标准过安检；把“好公司 / 好股票 / 好买点”分开。

**Current version:** `2.2.0`

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)

## 这是什么

一个为 Codex 设计的成长股研究 skill，也可以作为通用研究框架参考。

它把公开的成长股投资方法，组织成一套更容易执行的研究语言：

- **阴仪**：公司质量、增速、现金流、估值、管理层；
- **阳仪**：行业景气、价格趋势、资金、政策、市场认可；
- **四象**：共振、左侧、主题、退潮，只做研究排序；
- **六条标准**：业绩、增长动能、供需、想象力、市场认可、管理层；
- **三层判断**：好公司、好股票、好买点必须分开；
- **增强块**：增长拆解、订单台账、估值桥、筹码/减持、四象迁移、数据可信度。

## 这不是什么

- 不是荐股工具，不给买卖点、目标价、仓位比例；
- 不是实时行情/财报抓取器，不联网补数据；
- 不是技术分析、K 线、缠论或短线择时工具；
- 不是收益承诺，也不替代使用者自己的判断。

## 核心模型

| 层 | 看什么 | 回答的问题 |
|---|---|---|
| 阴仪 | 营收、利润、扣非、现金流、毛利率、订单、竞争格局、估值、管理层 | 这是不是一家好公司？ |
| 阳仪 | 行业景气、价格趋势、52 周新高、资金流、板块效应、政策、拥挤度 | 它现在是不是好股票？ |
| 四象 | 阴仪与阳仪合参 | 研究优先级排第几？ |
| 六条标准 | 硬门槛 | 够不够格？ |
| 守中 | 交易纪律 | 不偏执、不单吊、不加杠杆 |

### 四象

| 四象 | 阴仪：景气/基本面 | 阳仪：价格/资金 | 研究含义 |
|---|---|---|---|
| 太阳·共振 | 上行 | 上行 | 重点研究；仍需过六条标准，不追高 |
| 少阳·左侧 | 上行 | 未确认 | 跟踪基本面，等价格确认；不把便宜当买点 |
| 少阴·主题 | 未确认/下行 | 上行 | 只按反弹或主题处理，防拥挤和证伪 |
| 太阴·退潮 | 下行 | 下行 | 等待或回避，不因跌得多抄底 |

四象是**研究排序**，不是买卖信号。

### 六条标准

1. 业绩硬增速：营收/利润/主营增速是否达标，是否亏损；
2. 新增长动能：新产品、新服务、新市场、新应用场景是否已兑现；
3. 强供需矛盾：是否供不应求、满产、排队、涨价且量增；
4. 充足想象力：天花板、渗透率、可复制性、海外空间；
5. 市场认可度：是否持续创新高、有板块效应、资金合力；
6. 管理层背书：增持、回购、股权激励、业绩承诺。

原体系要求六条同时成立（AND），不是加权平均；第 6 条可适度放宽，其余五条是硬门槛。

### 增强块

| 增强块 | 解决什么问题 |
|---|---|
| 增长拆解 | 防止“新业务翻倍”掩盖“总营收下滑” |
| 订单台账 | 防止战略协议、框架协议、送样被写成正式订单 |
| 估值桥 | 防止高 PE/PS 只凭感觉说贵或便宜 |
| 筹码/减持 | 防止把减持、回购、融资余额直接等同于基本面 |
| 四象迁移 | 防止四象变成静态标签，补上升级/降级条件 |
| 数据可信度 | 用 S1–S5 区分公告、公司 IR、媒体、研报、传闻 |

## 目录结构

```text
taiji-liangyi-growth/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── assets/
│   ├── review-template.md
│   └── review-template-enhanced.md
├── references/
│   ├── taiji-method.md
│   ├── analysis-blocks.md
│   ├── criteria.md
│   ├── growth-quality.md
│   ├── valuation-expectations.md
│   ├── data-protocol.md
│   ├── future-industry-map.md
│   ├── industry-analysis.md
│   ├── market-regime.md
│   ├── selection.md
│   ├── trading-discipline.md
│   ├── research-workflow.md
│   ├── cases-and-era.md
│   ├── pitfalls.md
│   ├── glossary.md
│   ├── framework.md
│   ├── source-provenance.md
│   └── source-text.md
├── scripts/
│   └── screen.py
└── tests/
    ├── prompts.md
    ├── analysis-blocks-prompts.md
    └── sample-screen.csv
```

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/AlanDoDo/taiji-liangyi-growth.git
```

### 2. 安装到 Codex

macOS / Linux：

```bash
mkdir -p ~/.codex/skills
cp -R taiji-liangyi-growth ~/.codex/skills/
```

Windows PowerShell：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.codex\skills" | Out-Null
Copy-Item -Recurse -Force .\taiji-liangyi-growth "$env:USERPROFILE\.codex\skills\"
```

如果设置了 `CODEX_HOME`，把目标目录换成 `$env:CODEX_HOME\skills`。

### 3. 开始使用

在 Codex 中直接说：

```text
用太极两仪体检一下这家公司，数据截止 2026-11-13，这是财报/CSV。
```

```text
用四象过一遍 AI 电力、机器人、创新药，判断谁是共振、谁是左侧、谁是主题。
```

```text
用增强模板分析这家公司：重点做增长拆解、订单台账、估值桥、筹码和四象迁移。
```

```text
复盘这笔交易：买入理由、持有过程、卖出理由，哪里违反体系？
```

## CSV 初筛

`scripts/screen.py` 只做本地确定性初筛，不联网、不构成投资建议。

```bash
python scripts/screen.py --input tests/sample-screen.csv --format markdown
```

支持的字段别名包括：营收增速、单季营收增速、归母/净利增速、扣非增速、市值、距 52 周高点、一年新高、新增长、供需、想象力、管理层背书等。字段缺失会输出“缺口”，不会自动补全。

## 设计原则

- **单入口 + 按需 references**：入口只放路由、硬规则和输出契约，避免一次加载全部内容。
- **证据分层**：区分 `原文观点`、`事实`、`推断`、`缺口`。
- **四象不是信号**：共振不等于买入，退潮不等于必跌。
- **好公司 ≠ 好股票 ≠ 好买点**：公司质量、市场趋势、估值赔率必须分开写。
- **不荐股**：不提供买卖点、目标价、仓位比例或收益承诺。
- **数据来源分级**：S1 公告/财报 > S2 公司 IR > S3 政府/协会/数据库 > S4 媒体/研报 > S5 传闻。
- **新业务不能替代总报表**：新业务占比低时，必须同时写总营收增速和新业务占比。
- **订单分约束力**：L1 正式订单/中标/合同；L2 战略采购/框架协议；L3 意向/备忘录；L4 送样/demo/试点。

## 数据边界

- 本仓库不包含实时行情、实时财报或联网抓取。
- 需要当前数据时，请提供 CSV/Excel、公告原文或财报，并写清 `as_of_date`、市场、股票池、来源。
- 港股、美股需要单独确认币种、报告期、公告日和财年口径。
- `references/future-industry-map.md` 是研究议程，不是买入名单。

## 免责声明

本项目是个人学习与研究用的框架整理，不构成投资建议、招揽或收益承诺。市场有风险，任何决策由使用者自行承担。

## 来源、许可与贡献

- 原始方法论、六条标准、五条不买与原始案例：见 [ATTRIBUTION.md](ATTRIBUTION.md)；
- 上游参考仓库：见 [ATTRIBUTION.md](ATTRIBUTION.md)；
- 本项目的“太极两仪 / 四象 / 听劲 / 守中”组织层：本项目贡献者；
- 公开版不包含原文全文，仅保留来源占位与上游链接；
- 代码与项目组织层采用 [MIT License](LICENSE)；
- 第三方许可见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)；
- 贡献指南见 [CONTRIBUTING.md](CONTRIBUTING.md)，变更记录见 [CHANGELOG.md](CHANGELOG.md)。

## License

[MIT](LICENSE)
