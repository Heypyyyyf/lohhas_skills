---
name: material-pool
description: 素材收集、评分筛选、入库创作池。从关键词触发，先走 material-collector 的4轮搜索收集素材，再按 material-filter 体系加权打分，≥7分写入飞书多维表格创作池。触发词："素材筛选"、"收集素材并评分"、"创建内容池"、"素材打分"、"入库创作池"。
---

# material-pool

素材 → 评分筛选 → 创作池入库全流程。

## 核心流程

```
关键词输入
  ↓
[阶段一] 素材收集（material-collector）
  ↓
[阶段二] 加权评分（x-filter 体系）
  ↓
[阶段三] 入库创作池（飞书多维表格）
```

---

## 阶段一：素材收集

完整复用 material-collector skill 的四轮搜索流程，生成结构化素材报告 + `MATERIALS_JSON` 块。

触发后按以下顺序执行：

**第一轮：权威来源**
```
site:mp.weixin.qq.com {keyword}
{keyword} 官方公告
{keyword} GitHub
```

**第二轮：深度解析**
```
{keyword} 详细介绍
{keyword} 教程 tutorial
{keyword} how it works
```

**第三轮：对比评测**
```
{keyword} vs {竞品}
{keyword} 评测 review
{keyword} 优缺点
```

**第四轮：补充验证**
分析前三轮缺口，补充最新动态

---

## 阶段二：加权评分

对阶段一产出的每条素材，按以下维度打分：

### 评分维度与权重（默认）

| 维度 | 权重 | 满分 | 说明 |
|------|------|------|------|
| 热度/趋势 | w_trending | 4 | 当前热度与上升趋势 |
| 争议性 | w_controversy | 2 | 讨论潜力与观点对立 |
| 高价值 | w_value | 3 | 信息密度与行动指导性 |
| 相关性 | w_relevance | 1 | 与账号定位的匹配度 |

**权重来源优先级：**
1. `references/weights.md`（用户自定义配置）
2. 下述默认值

### 默认权重

```yaml
weights:
  w_trending: 4
  w_controversy: 2
  w_value: 3
  w_relevance: 1
  threshold: 7   # ≥7分进入创作池
```

### 各维度打分标准

**热度/趋势 (0-4)**
- 4分：当前热门话题，大量讨论
- 3分：近期热点，关注度上升
- 2分：稳定话题，持续有人讨论
- 1分：小众话题，关注度有限
- 0分：过时话题，几乎无人讨论

**争议性 (0-2)**
- 2分：明显争议，多方观点对立
- 1分：存在不同看法，可引发讨论
- 0分：共识性话题，难以引发讨论

**高价值 (0-3)**
- 3分：硬核干货，可直接指导行动
- 2分：有价值信息，提供新视角
- 1分：一般信息，了解即可
- 0分：低价值，无实质内容

**相关性 (0-1)**
- 1分：与账号定位高度相关
- 0分：与账号定位关联较弱

### 权重可调说明

用户可随时通过"调整权重"指令修改 `references/weights.md`，修改后下一轮评分生效。

### 最终得分计算

```
FinalScore = Σ(维度得分 × 权重系数)
```

例（默认权重）：
- 热度4 × 4 + 争议1 × 2 + 价值3 × 3 + 相关1 × 1 = 16 + 2 + 9 + 1 = 28
- 归一化：28 / (4+2+3+1) × 10 ≈ 7.0

---

## 阶段三：入库创作池

### 判断逻辑

```
FinalScore ≥ threshold(默认7分) → Tier A（入选创作池）
FinalScore 5-6分 → Tier B（待定）
FinalScore < 5分 → Tier C（淘汰）
```

### 飞书多维表格处理

1. **查询是否已有创作池表格**
   - 用 `feishu_bitable_app(action=list)` 查找名为"创作池"的多维表格
   - 若无，则在用户默认文件夹下新建，命名为"创作池"

2. **表格字段设计**

   | 字段名 | 类型 | 说明 |
   |--------|------|------|
   | 标题 | 文本 | 素材标题 |
   | 摘要 | 文本 | 2-3句话概括 |
   | 来源URL | 超链接 | 原始链接 |
   | 来源平台 | 单选 | 微信公众号/百度/谷歌/其他 |
   | 话题标签 | 多选 | 按话题聚类打标签 |
   | 内容类型 | 单选 | 高价值干货/热点评论/深度解析/行业观察 |
   | 热度评分 | 数字 | 0-10 |
   | 争议性评分 | 数字 | 0-10 |
   | 高价值评分 | 数字 | 0-10 |
   | 相关性评分 | 数字 | 0-10 |
   | 综合得分 | 数字 | 最终加权得分（0-10） |
   | 创作角度 | 文本 | 建议的切入点 |
   | 推荐风格 | 单选 | 高价值干货/犀利观点/热点评论/故事洞察/技术解析 |
   | 状态 | 单选 | 待创作/已创作/已放弃 |
   | 入选时间 | 日期 | 入库日期 |

3. **写入记录**
   - Tier A 的每条素材创建一条记录
   - Tier B 和 Tier C 不写入表格，仅在报告中展示

4. **写入顺序（重要）**
   - 第一步：`batch_create` 入库除"来源URL"外的所有字段
   - 第二步：`update` 逐条补充"来源URL"字段（格式：`{"link": "url", "text": "显示文字"}`）
   - ⚠️ 原因：超链接字段在 batch_create 中格式处理较繁琐，分步写入更稳定

---

## 输出格式

### 用户报告

```markdown
# 素材池管理报告

## 筛选时间
{timestamp}

## 权重配置
| 维度 | 权重 | 满分 |
|------|------|------|
| 热度/趋势 | {w_trending} | 4 |
| 争议性 | {w_controversy} | 2 |
| 高价值 | {w_value} | 3 |
| 相关性 | {w_relevance} | 1 |
| **阈值** | - | **{threshold}** |

---

### Tier A：入选创作池（≥{threshold}分）

| # | 标题 | 综合得分 | 热度 | 争议性 | 高价值 | 相关性 |
|---|------|----------|------|--------|--------|--------|
| 1 | ... | {score}/10 | {t}/4 | {c}/2 | {v}/3 | {r}/1 |

### Tier B：待定（5-6分）
...

### Tier C：淘汰（<5分）
...

## 创作建议

入选 **{n}** 个选题，建议优先级：
1. **{top_title}**（{score}分）- {reason}
2. **{second_title}**（{score}分）- {reason}

创作池表格：{bitable_url}
```

### 机器可读块

```json
POOL_JSON
{
  "schema_version": "material_pool.v1",
  "timestamp": "{timestamp}",
  "weights": {
    "trending": {w_trending},
    "controversy": {w_controversy},
    "value": {w_value},
    "relevance": {w_relevance},
    "threshold": {threshold}
  },
  "tier_a": [{...}],
  "tier_b": [{...}],
  "tier_c": [{...}],
  "bitable_app_token": "{app_token}"
}
```

---

## 执行步骤

1. **接收关键词** — 用户输入的核心主题
2. **执行四轮搜索** — 按 material-collector 流程收集素材
3. **读取权重配置** — 查 `references/weights.md`，不存在则用默认值
4. **逐条评分** — 按维度打分，计算 FinalScore
5. **分类 Tier** — A/B/C
6. **处理多维表格** — 查找或新建"创作池"表格，按需创建字段
7. **写入 Tier A 记录**
   - 第一步：`feishu_bitable_app_table_record(action=batch_create)` 入库除"来源URL"外的所有字段
   - 第二步：`feishu_bitable_app_table_record(action=update)` 逐条补上"来源URL"字段（格式：`{"link": "url", "text": "显示文字"}`）
8. **输出报告** — 汇总展示

---

## 字段格式避坑（飞书多维表格）

### 超链接（URL）字段

❌ 错误写法（会报 `URLFieldConvFail`）：
```json
{"来源URL": "https://example.com"}
```

✅ 正确写法：
```json
{"来源URL": {"link": "https://example.com", "text": "显示文字"}}
```

超链接字段必须传对象 `{link, text}`，不能直接传字符串。

### 数字字段

直接传数值，无需特殊格式：
```json
{"综合得分": 7.6}
```

### 日期字段

传毫秒时间戳（Unix ms）：
```json
{"入选时间": 1744862400000}
```

### 多选字段

传字符串数组：
```json
{"话题标签": ["全脑领导力", "HBDI"]}
```

---

## 权重配置说明

权重文件路径：`references/weights.md`

格式：
```yaml
weights:
  w_trending: 4
  w_controversy: 2
  w_value: 3
  w_relevance: 1
  threshold: 7
```

调整方式：告诉小白"把争议性权重调到3分"或"阈值改成8分"，小白自动更新此文件。
