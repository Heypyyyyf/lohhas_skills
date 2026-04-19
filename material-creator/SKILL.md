---
name: material-creator
description: 根据创作池选题，创作适配视频号/小红书/公众号的内容。触发词："创作内容"、"写文案"、"生成内容"、"制作脚本"。支持A/B双版本+Critic自检+去AI味。
---

# 内容创作 material-creator

从创作池选题 → 创作适配渠道的完整内容。

## 业务背景

服务于 iLohhas乐活：
- **视频号**：【乐活范】【学管理】短视频
- **小红书**：图文笔记
- **公众号**：深度长文

详见 `references/user-profile.md` 和 `references/post-patterns.md`

## 核心流程

```
接收选题
  ↓
加载配置（user-profile + post-patterns）
  ↓
加载用户参考模板（assets/templates/{type}/）
  ↓
意图路由 → 确定内容风格
  ↓
生成 Variant A + Variant B
  ↓
Humanize Pass（去AI味）→ A/B 各自处理
  ↓
Critic 自检打分（0-10）
  ↓
若两版均 < 7 → 自动重写一次（A2/B2）
  ↓
选最优版本输出
  ↓
输出完整内容 + 发布建议
```

## 意图路由

| 用户意图信号 | → 风格 | 说明 |
|-------------|--------|------|
| 怎么做、步骤、教程 | 高价值干货 | 可执行清单、工具推荐 |
| 为什么、原理解释 | 深度解析 | 机制拆解、左右脑视角 |
| 热点事件、最新新闻 | 热点评论 | 快速反应、独特角度 |
| 个人经历、经验复盘 | 故事洞察 | 场景+转折+金句 |
| 反常识、质疑现有做法 | 犀利观点 | 有立场、能引发讨论 |

**风格 → 渠道适配：**
- 高价值干货 → 小红书（图文清单）
- 深度解析 → 公众号（长文）
- 热点评论 → 视频号（短评）
- 故事洞察 → 视频号/小红书
- 犀利观点 → 小红书/视频号

## A/B 双版本规则

- **Variant A**：更强钩子，更高对比，更直接
- **Variant B**：更结构化，更多证据，略中立

## Humanize Pass（去AI味，必做）

对每个版本都必须执行：

**删除**：
- 填充词：`当然`、`希望对你有帮助`、`让我们来深入探讨`
- 宏大词：`标志着`、`至关重要`、`赋能`、`令人叹为观止`
- 模糊归属：`专家认为`、`行业报告显示`（无具体来源时）

**调整**：
- 减少连接词：少用`此外`、`然而`、`因此`，多换行
- 打破三段式：2个要点也可以
- 具体代替抽象：`员工更有动力` → `周一早上大家主动开始对齐`
- 不确定则直说：`大概率`、`可能`，不用`一定会`

## Critic 自检打分（0-10）

对去AI味后的每个版本，从目标读者视角打分：

| 维度 | 说明 |
|------|------|
| 钩子强度 | 开头能否让人停下来 |
| 信息密度 | 是否有实质内容 |
| 可读性 | 是否流畅、易读 |
| 可信度 | 有无夸大/编造事实 |
| 人设匹配 | 是否符合乐活调性 |
| 行动导向 | 能否引发收藏/评论/转发 |

**触发重写**：若 Variant A 和 B 均 < 7分 → 自动重写一次（A2/B2），再执行 Humanize Pass 并重新打分。

## 模板优先级

```
1. 用户模板优先：
   检查 assets/templates/{type}/
   → 有 .md 文件 → 优先学习其风格
2. 默认模式：
   无用户模板 → 使用 references/post-patterns.md
```

## 输出格式

### 完整报告

```markdown
# 内容创作

## 选题
{topic}

## 渠道
{渠道}

## 风格
{内容类型}

---

## Drafts

### Variant A
{完整内容}
**Critic 得分 (0-10)**: {score}

### Variant B
{完整内容}
**Critic 得分 (0-10)**: {score}

---

## Selected
最终选择：{A|B|A2|B2}
理由：{一句话说明}

---

## 发布建议
- 最佳发布时间：{建议时段}
- 配图建议：{描述性建议}
- 预期互动：{收藏/评论/转发预测}
- 话题标签：#{tag1} #{tag2} ...

下一步：审核后手动发布到 {平台}
```

### CREATE_JSON（机器可读块）

```json
CREATE_JSON
{
  "schema_version": "material_create.v1",
  "topic": "{topic}",
  "channel": "视频号|小红书|公众号",
  "post_style": "high-value|sharp-opinion|trending-comment|story-insight|tech-analysis",
  "variants": [
    {"id": "A", "critic_score": 0, "text": "..."},
    {"id": "B", "critic_score": 0, "text": "..."}
  ],
  "selected": "A|B|A2|B2",
  "rewrite_once": true|false
}
```

### HOOKS_JSON（钩子库）

```json
HOOKS_JSON
{
  "schema_version": "material_hooks.v1",
  "topic": "{topic}",
  "hooks": [
    {
      "text": "...",
      "source": "variant.A",
      "tags": ["数字|反常识|痛点|悬念|类比"],
      "score": 0
    }
  ]
}
```

## 创作原则

1. **一个核心观点**：不能什么都想说
2. **开头3秒**：视频号开头必须有钩子
3. **金句单独成行**：便于截图传播
4. **关联乐活概念**：内容中自然带入左右脑/OKR/乐活人生
5. **说人话**：不用管理黑话

## 执行步骤

1. **接收选题** — 用户输入或从创作池读取
2. **确认渠道** — 视频号/小红书/公众号
3. **加载配置** — user-profile.md + post-patterns.md
4. **加载模板** — `assets/templates/{type}/`（优先）
5. **意图路由** — 确定内容风格
6. **生成 Variant A/B**
7. **Humanize Pass** — A/B 各自去AI味
8. **Critic 自检** — 打分，判断是否重写
9. **选最优版本** — 输出最终内容
10. **输出报告** — 完整内容 + CREATE_JSON + HOOKS_JSON + 发布建议
