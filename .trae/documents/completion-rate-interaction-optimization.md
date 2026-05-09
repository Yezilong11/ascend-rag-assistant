# 完成率交互优化计划

## 问题分析

### 问题1：进度条重复显示

在 `SkillNodeCard.tsx` 中存在两个独立的进度条元素：
- **第119-143行**：自定义 div 实现的只读进度条 + 百分比文字
- **第144-162行**：Ant Design `Slider` 组件（可拖动）

两者视觉上形成两条进度条，且功能重叠。

### 问题2：滑块交互不够精准

Ant Design `Slider` 步长为 5%，用户难以精确定位到具体百分比（如 83%、92% 等）。

---

## 实施步骤

### 步骤1：合并进度条，移除重复

**文件**: `frontend/src/components/skilltree/SkillNodeCard.tsx`

**方案**: 移除自定义 div 只读进度条，仅保留 Ant Design `Slider` 作为唯一的进度展示和交互元素。将百分比数字嵌入 Slider 右侧，形成一行式布局：

```
[========= Slider =========] 83%
```

### 步骤2：增加精准输入交互方式

**文件**: `frontend/src/components/skilltree/SkillNodeCard.tsx`

**方案**: 在百分比数字上添加点击编辑功能：
- 默认状态：显示 `83%` 文字
- 点击后：切换为 `<InputNumber>` 输入框，用户可输入 0-100 的精确数值
- 按 Enter 或失焦时：提交值并切回文字显示
- 按 Escape 时：取消编辑，恢复文字显示

布局结构：
```
技能名称                        [入门]
描述文字...
📖 理论  ⏱ 10h
[========= Slider =========] [83%] ← 点击可编辑
```

### 步骤3：样式优化

- Slider 样式与暗色主题协调
- InputNumber 弹出时样式与卡片一致
- 完成率 100% 时百分比文字变为绿色
- 完成率 0% 时百分比文字为灰色

### 步骤4：构建验证

- 运行 `npx tsc --noEmit` 类型检查
- 运行 `npx vite build` 构建验证

---

## 涉及文件

| 文件 | 操作 |
|------|------|
| `frontend/src/components/skilltree/SkillNodeCard.tsx` | 修改：合并进度条 + 添加精准输入 |
