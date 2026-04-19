# 评分权重配置

## 说明

此文件控制素材评分时的权重系数。修改后下一轮评分生效。

## 权重格式

```yaml
weights:
  w_trending: 4      # 热度/趋势权重（满分4）
  w_controversy: 2   # 争议性权重（满分2）
  w_value: 3         # 高价值权重（满分3）
  w_relevance: 1     # 相关性权重（满分1）
  threshold: 7        # 入选阈值（≥7分进创作池）
```

## 调整示例

- 加重热度权重：`w_trending: 5`（满分也要相应改为5）
- 放宽阈值：`threshold: 6`
- 收紧阈值：`threshold: 8`
