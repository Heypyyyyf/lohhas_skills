# 权重配置

用户可随时调整各项权重。调整后下一轮评分生效。

## 默认权重

```yaml
weights:
  w_trending: 4      # 热度/趋势权重
  w_controversy: 2   # 争议性权重
  w_value: 3         # 高价值权重
  w_relevance: 1     # 相关性权重
  threshold: 7       # 入选阈值（≥7分进入创作池）
```

## 权重文件路径

`{skill_directory}/references/weights.md`

## 调整方式

用户说"把xx权重调到x"或"阈值改成x"，自动更新此文件。

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| w_trending | int | 热度/趋势维度权重，默认4，满分4 |
| w_controversy | int | 争议性维度权重，默认2，满分2 |
| w_value | int | 高价值维度权重，默认3，满分3 |
| w_relevance | int | 相关性维度权重，默认1，满分1 |
| threshold | int | 入选阈值，默认7 |
