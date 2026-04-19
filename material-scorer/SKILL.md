---
name: material-scorer
description: 对 material-collector 收集的素材进行加权评分筛选，≥7分写入飞书多维表格创作池。触发词："素材打分"、"评分筛选"、"素材评分"、"入库创作池"。
---

# 素材评分 material-scorer

素材评分筛选 → 创作池入库。

## 业务背景

服务于 iLohhas乐活，内容需符合品牌定位：
- **核心话题**：左右脑管理哲学、OKR、组织进化、乐活人生、阶段理论
- **品牌调性**：认真、乐观、不怕失败
- **分发渠道**：视频号、小红书

详见 `references/user-profile.md`

## 核心流程

```
MATERIALS_JSON
  ↓
读取权重（references/weights.md）
  ↓
读取负样本库（state/rejected_topics.json）
  ↓
逐条评分 + 相似度过滤 + 多样性调控
  ↓
Tier A/B/C 分类
  ↓
Tier A → 写入飞书多维表格
  ↓
Tier C → 写入负样本库
  ↓
输出报告 + FILTER_JSON
```

## 评分维度

| 维度 | 满分 | 说明 |
|------|------|------|
| 热度/趋势 | 4 | 当前热度与上升趋势 |
| 争议性 | 2 | 讨论潜力与观点对立 |
| 高价值 | 3 | 信息密度与行动指导性 |
| 相关性 | 1 | 与乐活内容定位的匹配度 |

## 打分标准

**热度/趋势 (0-4)**
- 4分：当前热门话题，大量讨论
- 3分：近期热点，关注度上升（近3个月有大量新内容）
- 2分：稳定话题，持续有人讨论
- 1分：小众话题，关注度有限
- 0分：过时话题，几乎无人讨论

**新鲜度奖励/惩罚（Optional）**
- 推断来源时间：<72小时 → +0.5分
- >30天 → -0.5分
- 融入热度分，不单独计分

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
- 1分：涉及左右脑管理、OKR、组织进化、乐活人生、阶段理论等核心话题
- 0分：关联较弱

## 得分计算

```
FinalScore = Σ(维度得分 × 权重) / Σ(权重) × 10 - NegPenalty
```

归一化到 0-10 分（保留1位小数）。

## 相似度过滤（Negative Penalty）

读取 `state/rejected_topics.json`，对每条候选计算与被淘汰选题的相似度：

```bash
python3 ../material-pool/scripts/material_pool_state.py similarity --text "{title}" --against rejected --topk 3
```

**惩罚规则：**
- 相似度 ≥ 0.85 → 强惩罚（直接淘汰或 -3分降权）
- 0.75 ≤ 相似度 < 0.85 → 软惩罚 -2分
- 相似度 < 0.75 → 无惩罚

## 多样性调控

**同来源衰减**：同一域名/平台的多条素材，从第2条起：
```
score *= 0.6^(N-1)
```
第1条素材得分不变，第2条×0.6，第3条×0.36……

**话题聚类去重**：同一话题标签下仅保留得分最高的1条，其余标记为 Tier C。

## 入库判断

```
FinalScore ≥ threshold → Tier A（入选创作池）
FinalScore 5 ~ threshold-1 → Tier B（待定）
FinalScore < 5 → Tier C（淘汰）
```

## 创作池表格处理

### 查找表格
用 `feishu_bitable_app(action=list)` 查找名为"创作池"的表格。

### 创建表格（如不存在）
在用户默认文件夹下新建"创作池"多维表格。

### 表格字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 标题 | 文本 | 素材标题 |
| 摘要 | 文本 | 2-3句话概括 |
| 来源URL | 超链接 | `{link, text}` |
| 来源平台 | 单选 | 微信公众号/百度/谷歌/其他 |
| 话题标签 | 多选 | 如"左右脑OKR"、"组织文化" |
| 内容类型 | 单选 | 高价值干货/热点评论/深度解析/行业观察 |
| 热度评分 | 数字 | 0-10 |
| 争议性评分 | 数字 | 0-10 |
| 高价值评分 | 数字 | 0-10 |
| 相关性评分 | 数字 | 0-10 |
| 综合得分 | 数字 | 最终加权得分（0-10） |
| 创作角度 | 文本 | 建议的切入点 |
| 推荐风格 | 单选 | 高价值干货/犀利观点/热点评论/故事洞察/技术解析 |
| 状态 | 单选 | 待创作/已创作/已放弃 |
| 入选时间 | 日期 | 毫秒时间戳 |

### 批量写入流程
1. `batch_create` 写入除"来源URL"外的所有字段
2. `update` 逐条补上"来源URL"（`{link, text}`）

## 权重配置

文件：`references/weights.md`

```yaml
weights:
  w_trending: 4
  w_controversy: 2
  w_value: 3
  w_relevance: 1
  
  threshold: 7
```

## 输出格式

### 用户报告

```markdown
# 素材评分报告

## 筛选时间
{timestamp}

## 权重配置
- 热度 {w_trending}、争议性 {w_controversy}、高价值 {w_value}、相关性 {w_relevance}
- 阈值 {threshold}分

### Tier A：入选（≥{threshold}分）

| # | 标题 | 综合得分 | 热度 | 争议性 | 高价值 | 相关性 | 负向惩罚 |
|---|------|----------|------|--------|--------|--------|----------|
| 1 | ... | {score} | {t}/4 | {c}/2 | {v}/3 | {r}/1 | -{neg_penalty} |

### Tier B：待定（5-{threshold-1}分）
...

### Tier C：淘汰（<5分）
...

## 创作建议
入选 **{n}** 个，建议优先级：
1. **{title}**（{score}分）- {reason}

创作池：{bitable_url}
```

### FILTER_JSON（机器可读块）

```json
FILTER_JSON
{
  "schema_version": "material_filter.v1",
  "timestamp": "{timestamp}",
  "profile": {
    "domains": ["左右脑管理", "OKR", "组织进化", "乐活人生"],
    "persona_style": "认真、乐观、不怕失败"
  },
  "items": [
    {
      "title": "...",
      "scores": {
        "trending": 0,
        "controversy": 0,
        "value": 0,
        "relevance": 0,
        "neg_penalty": 0,
        "freshness": 0
      },
      "final_score": 0,
      "tier": "A|B|C",
      "reasons": ["..."],
      "similarity": {
        "max": 0.0,
        "matched": [{"id": "rej_xxx", "score": 0.0, "title": "..."}]
      }
    }
  ]
}
```

## 执行步骤

1. **接收 MATERIALS_JSON**
2. **读取权重** — `references/weights.md`
3. **读取负样本库** — `state/rejected_topics.json`（无则跳过相似度过滤）
4. **逐条评分**
   - 打4个维度分
   - 推断新鲜度（Optional）
   - 计算原始加权得分
   - 相似度过滤 → NegPenalty
5. **多样性调控** — 来源衰减 + 话题聚类去重
6. **分类 Tier** — A/B/C
7. **处理多维表格** — 查找或新建"创作池"
8. **写入 Tier A** — 分步写入（先核心字段，后URL）
9. **Tier C 入库负样本** — `python3 ../material-pool/scripts/material_pool_state.py reject --topic-json '{...}'`
10. **追加事件日志** — `python3 ../material-pool/scripts/material_pool_state.py event --event filter.scored --payload-json '{...}'`
11. **输出报告 + FILTER_JSON**
