# Lohhas Skills

> 乐活内容创作 Skills —— AI 驱动的内容生产工作流

## 📦 包含 Skills

### 1. material-collector
素材收集技能，通过四轮深度网页搜索收集热门素材。

**功能：**
- 微信公众号/百度/谷歌多平台搜索
- 话题扩展与变体生成
- 去重与聚类
- 结构化素材报告

**触发词：** 找素材、筛选素材、研究素材、热门素材、趋势素材

---

### 2. material-scorer
素材评分筛选技能，对收集的素材进行加权评分。

**评分维度：**
- 热度/趋势 (0-4)
- 争议性 (0-2)
- 高价值 (0-3)
- 相关性 (0-1)

**触发词：** 素材打分、评分筛选、素材评分、入库创作池

---

### 3. material-creator
内容创作技能，根据选题创作适配视频号/小红书/公众号的内容。

**功能：**
- A/B 双版本创作
- Critic 自检机制
- 去 AI 味处理
- 多平台适配

**触发词：** 创作内容、写文案、生成内容、制作脚本

---

### 4. material-pool
素材池管理，全流程整合技能。

**功能：**
- 素材收集（material-collector）
- 评分筛选（material-scorer）
- 创作池入库（飞书多维表格）

**触发词：** 素材筛选、收集素材并评分、创建内容池

---

## 🚀 快速开始

### 克隆到 OpenClaw Skills 目录

```bash
# 克隆仓库
git clone https://github.com/Heypyyyyf/lohhas_skills.git

# 复制到 OpenClaw skills 目录
cp -r lohhas_skills/* ~/.openclaw/skills/

# 重启 OpenClaw
openclaw restart
```

### 验证安装

```bash
openclaw skills list
```

应该能看到这 4 个 skill：
- `material-pool`
- `material-creator`
- `material-collector`
- `material-scorer`

---

## 📋 工作流程

```
素材收集 (material-collector)
      ↓
素材评分 (material-scorer)
      ↓
创作池入库 (飞书多维表格)
      ↓
内容创作 (material-creator)
```

---

## 📄 License

MIT License
