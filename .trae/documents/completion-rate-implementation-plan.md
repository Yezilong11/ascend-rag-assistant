# 完成率功能实现计划

## 问题分析

### 根因诊断

完成率始终显示 0.0% 的根本原因：**前端缺少用户更新完成率的交互入口**。

后端完整实现了完成率的计算和存储逻辑：
- `SkillNode.completion_rate` 默认 0.0，`update_completion_rate()` 方法约束范围 [0, 100]
- `calculate_skill_tree_completion()` 计算所有节点完成率的算术平均值
- API 端点 `PUT /{skill_tree_id}/skills/{skill_id}/completion` 已就绪
- 前端 `skillTreeApi.updateCompletion()` 和 `useSkillTree.updateCompletion()` 已封装

但前端没有任何 UI 组件调用 `updateCompletion`，导致：
1. 所有技能节点创建时 `completion_rate = 0.0`
2. 用户无法修改完成率
3. 技能树整体完成率 = avg(0.0, 0.0, ...) = 0.0%

### 现有完成率展示点

| 位置 | 文件 | 当前展示方式 |
|------|------|-------------|
| 技能树列表卡片 | `SkillTreeList.tsx:116` | 绿色标签文字 `完成率 0.0%` |
| 技能树详情头部 | `SkillTreeDetail.tsx:94-96` | 绿色标签文字 `完成率 0.0%` |
| 技能节点卡片 | `SkillNodeCard.tsx:108-128` | 渐变进度条 + 百分比文字 |
| 可视化图节点 | `SkillGraph.tsx` | 无完成率展示 |

---

## 实施步骤

### 步骤 1：SkillNodeCard 添加完成率更新交互

**文件**: `frontend/src/components/skilltree/SkillNodeCard.tsx`

**改动**:
- 新增 `onUpdateCompletion` 回调 prop
- 将现有的只读进度条改为可交互的滑块（Slider），用户拖动即可更新完成率
- 使用 Ant Design 的 `Slider` 组件，样式与暗色主题一致
- 滑块值变化时调用 `onUpdateCompletion(node.id, value)`
- 保留原有进度条视觉效果，在滑块上方叠加显示

### 步骤 2：SkillTreeDetail 传递完成率更新回调

**文件**: `frontend/src/components/skilltree/SkillTreeDetail.tsx`

**改动**:
- 新增 `onUpdateCompletion` prop
- 将回调传递给 `SkillNodeCard` 组件
- 在技能列表 tab 中为每个 `SkillNodeCard` 传入 `onUpdateCompletion`

### 步骤 3：SkillTreePage 连接完成率更新流程

**文件**: `frontend/src/pages/SkillTreePage.tsx`

**改动**:
- 从 `useSkillTree()` 解构 `updateCompletion`
- 创建 `handleUpdateCompletion` 处理函数
- 将其传递给 `SkillTreeDetail` 组件

### 步骤 4：SkillTreeDetail 头部完成率可视化增强

**文件**: `frontend/src/components/skilltree/SkillTreeDetail.tsx`

**改动**:
- 将头部的简单标签 `完成率 0.0%` 替换为进度条 + 百分比数字的组合展示
- 进度条使用与项目一致的渐变色（`var(--gradient-primary)`）
- 进度条宽度动态反映 `skillTree.completion_rate`
- 保留节点数标签不变

### 步骤 5：SkillTreeList 列表卡片完成率可视化增强

**文件**: `frontend/src/components/skilltree/SkillTreeList.tsx`

**改动**:
- 将列表卡片中的 `完成率 0.0%` 标签替换为小型进度条 + 百分比
- 进度条与暗色主题协调

### 步骤 6：SkillGraph 可视化节点添加完成率指示

**文件**: `frontend/src/components/skilltree/SkillGraph.tsx`

**改动**:
- 在 `SkillNodeData` 中添加 `completionRate` 字段
- 在 `initialNodes` 数据映射中传入 `skill.completion_rate`
- 在 `SkillNodeComponent` 图标下方文字区域添加完成率指示
- 完成率 > 0 时在图标周围添加微弱的完成光环效果
- 完成率 = 100% 时图标颜色增强/添加特殊标记

### 步骤 7：后端单元测试增强

**文件**: `tests/test_skill_tree.py`

**改动**:
- 新增 `test_calculate_skill_tree_completion` 测试用例：
  - 空技能树 → 0.0%
  - 单节点 50% → 50.0%
  - 多节点不同完成率 → 正确平均值
  - 全部 100% → 100.0%
  - 全部 0% → 0.0%
- 新增 `test_update_completion_reflects_in_tree_completion` 测试用例：
  - 更新节点完成率后，技能树整体完成率实时更新
- 新增 `test_completion_rate_boundary` 测试用例：
  - 超出 100 的值被约束为 100
  - 低于 0 的值被约束为 0

### 步骤 8：前端构建验证

- 运行 `npx tsc --noEmit` 确保类型检查通过
- 运行 `npx vite build` 确保构建成功
- 运行后端测试 `python -m pytest tests/test_skill_tree.py -v`

---

## 涉及文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/src/components/skilltree/SkillNodeCard.tsx` | 修改 | 添加完成率滑块交互 |
| `frontend/src/components/skilltree/SkillTreeDetail.tsx` | 修改 | 传递回调 + 头部进度条 |
| `frontend/src/pages/SkillTreePage.tsx` | 修改 | 连接 updateCompletion 流程 |
| `frontend/src/components/skilltree/SkillTreeList.tsx` | 修改 | 列表卡片进度条 |
| `frontend/src/components/skilltree/SkillGraph.tsx` | 修改 | 图节点完成率指示 |
| `tests/test_skill_tree.py` | 修改 | 增加完成率计算测试 |

## 不涉及的文件

- 后端 API/服务/模型代码：已完整实现，无需修改
- 前端 API 服务层 (`skillTreeApi.ts`)：`updateCompletion` 已实现
- 前端 Hook (`useSkillTree.ts`)：`updateCompletion` 已实现
- 类型定义 (`skillTree.ts`)：`completion_rate` 字段已定义
