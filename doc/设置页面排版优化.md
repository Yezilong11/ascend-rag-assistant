# 设置页面排版优化方案

## 一、需求文件分析

根据 `doc/change.md` 的要求，本次优化核心目标是：
1. **重构布局**：从当前三列卡片改为单列滚动布局（最大宽度900px）
2. **统一样式**：所有设置项采用左标签+右控件的一行布局
3. **分组重组**：将现有功能按5个分组重新组织
4. **功能保护**：严禁修改任何业务逻辑、API调用、数据绑定

---

## 二、当前页面结构分析

### 2.1 现有布局特点

| 组件 | 当前布局 | 问题 |
|------|----------|------|
| SettingsPage | 三列flex布局 | 内容分散，浏览不便 |
| EngineControl | 单卡片，嵌套表单 | 样式不一致 |
| KnowledgeBasePanel | 单卡片，网格统计 | 分组不清晰 |

### 2.2 当前样式变量（来自 tokens.css）

```css
--bg-primary: #0a0e1a;      /* 深色主背景 */
--bg-secondary: #111827;
--bg-tertiary: #1a1f35;
--bg-glass: rgba(17, 24, 39, 0.65);

--text-primary: #f0f4ff;     /* 主文字 */
--text-secondary: #8b95b0;   /* 次要文字 */
--text-tertiary: #5a6380;    /* 辅助文字 */

--neon-blue: #00d4ff;
--neon-green: #00ff88;
--neon-purple: #7b2fff;
--neon-amber: #ffb800;

--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
```

### 2.3 现有组件清单

| 组件 | 功能 | 保留要点 |
|------|------|----------|
| EngineControl | AI引擎启停控制 | loadModel/unloadModel 回调 |
| ModelSelector | 模型选择 | availableModels, value, onChange |
| RerankerConfig | 重排序配置 | enabled, model, topK 状态及回调 |
| KnowledgeBasePanel | 知识库管理 | stats, onAutoIngest, onUploadSuccess |
| FileUploader | 文件上传 | 原有拖拽/上传逻辑 |
| VLM Switch | 多模态开关 | vlmEnabled, setVlmEnabled |

---

## 三、优化方案详细设计

### 3.1 整体布局调整

| 项目 | 当前 | 优化后 |
|------|------|--------|
| 布局方式 | 三列flex | 单列滚动 |
| 内容宽度 | 自适应 | 最大900px，居中 |
| 卡片圆角 | var(--radius-sm)=8px | 统一16px |
| 分组间距 | 无 | 24px |
| 卡片内边距 | 20px | 0（内部项自己控制） |

### 3.2 卡片样式规范

```css
/* 深色模式卡片 */
.card {
  background: #1C1C1E;
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* 分组标题 */
.group-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  padding: 16px 20px 12px;
}
```

### 3.3 设置项样式规范

```css
/* 每行设置项 */
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 20px;
  border-bottom: 1px solid #2C2C2E; /* 深色分割线 */
}

.setting-item:last-child {
  border-bottom: none; /* 最后一项无分割线 */
}

/* 标签文字 */
.setting-label {
  font-size: 16px;
  font-weight: 450;
  color: #F0F0F0;
}

/* 右侧控件文字 */
.setting-value {
  font-size: 15px;
  color: #8E8E93;
}

/* 可点击项hover效果 */
.setting-item-clickable:hover {
  background: #2C2C2E;
  cursor: pointer;
}
```

### 3.4 开关样式规范

```css
/* 开关容器 */
.toggle {
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: #3A3A3C; /* 关闭状态 */
  position: relative;
  transition: all 0.3s;
}

.toggle.active {
  background: #007AFF; /* 开启状态 */
}

/* 开关滑块 */
.toggle-knob {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #fff;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all 0.3s;
}

.toggle.active .toggle-knob {
  left: 22px;
}
```

### 3.5 带箭头选择项样式

```css
.selection-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.selection-value {
  font-size: 15px;
  color: #8E8E93;
}

.chevron {
  color: #8E8E93;
  font-size: 18px;
}
```

---

## 四、分组重组方案

### 分组1：AI引擎控制

| 设置项 | 控件类型 | 数据绑定 |
|--------|----------|----------|
| 引擎状态 | 纯文本 | ragStatus.engine_loaded |
| 当前模型 | 带箭头选择项 | ragStatus.model_name |
| 重排序状态 | 带箭头选择项 | ragStatus.reranker_enabled |
| 操作 | 按钮 | 启动/停止AI引擎 |

### 分组2：多模态配置

| 设置项 | 控件类型 | 数据绑定 |
|--------|----------|----------|
| VLM图片描述 | 开关 + 描述文字 | vlmEnabled, setVlmEnabled |
| 图片描述模型 | 带箭头选择项 | vlm模型选择 |
| 知识库统计 | 纯文本 | stats.document_count, stats.chunk_count, stats.image_chunk_count |

### 分组3：多模态知识库管理

| 设置项 | 控件类型 | 数据绑定 |
|--------|----------|----------|
| 上传文件 | 上传组件 | FileUploader组件 |
| 知识库映射说明 | 纯文本 | 只读说明 |

### 分组4：重排序配置

| 设置项 | 控件类型 | 数据绑定 |
|--------|----------|----------|
| 启用重排序 | 开关 | useReranker, setUseReranker |
| 重排序模型 | 带箭头选择项 | rerankerModel, setRerankerModel |
| Top K | 带箭头选择项 | rerankerTopK, setRerankerTopK |
| 初始检索数量 | 带箭头选择项 | initialRetrievalK, setInitialRetrievalK |

### 分组5：其他设置

| 设置项 | 控件类型 | 数据绑定 |
|--------|----------|----------|
| 自动导入知识库 | 开关 | 需新增状态管理 |
| 系统运行状态指示灯 | 纯文本 | 可整合到分组1 |

---

## 五、实施步骤

### 阶段1：重构 SettingsPage 布局

1. 创建新的 SettingsPage 结构
2. 引入分组组件样式
3. 保持原有状态管理和回调函数不变

### 阶段2：统一组件样式

1. 创建 SettingItem 组件封装行样式
2. 创建 ToggleSwitch 组件封装开关样式
3. 创建 SelectionItem 组件封装带箭头项

### 阶段3：功能验证

1. 验证所有按钮、开关、选择器功能正常
2. 验证上传组件功能正常
3. 验证数据刷新机制正常

---

## 六、技术实现要点

### 6.1 保留不变的部分

| 元素 | 处理方式 |
|------|----------|
| useRAGStatus hook | 完全保留 |
| knowledgeBaseApi | 完全保留 |
| loadModel/unloadModel 回调 | 完全保留 |
| vlmEnabled 状态 | 完全保留 |
| FileUploader 组件 | 直接嵌入 |
| ModelSelector 逻辑 | 可作为选择弹窗触发器 |

### 6.2 需要调整的部分

| 元素 | 调整内容 |
|------|----------|
| SettingsPage 布局 | 三列flex → 单列卡片 |
| EngineControl | 拆分为多个设置项 |
| KnowledgeBasePanel | 拆分为多个分组 |
| 开关样式 | 统一为44x24规格 |
| 选择项 | 统一为值+箭头格式 |

### 6.3 响应式设计

```css
/* 移动端适配 */
@media (max-width: 768px) {
  .settings-content {
    padding: 0 12px;
  }

  .setting-item {
    padding: 0 12px;
    height: 52px;
  }
}
```

---

## 七、预期效果

1. **视觉层次更清晰**：通过分组标题和卡片间距，用户可以快速定位功能
2. **交互一致性**：所有设置项采用统一的左标签右控件布局
3. **更好的可扩展性**：分组结构便于添加新的设置项
4. **深色模式统一**：保留原有深色背景，视觉体验一致

---

## 八、文件修改清单

| 文件 | 修改内容 |
|------|----------|
| src/pages/SettingsPage.tsx | 重构整体布局，按5分组重组 |
| src/components/knowledge/KnowledgeBasePanel.tsx | 拆分卡片为分组样式 |
| src/components/settings/EngineControl.tsx | 拆分嵌套表单为设置项行 |
| src/styles/tokens.css | 新增分组标题等样式变量（可选） |

**注意**：由于需求明确指出不能修改业务逻辑，组件拆分后必须确保：
- 所有 `onChange`、`onClick` 回调与原来完全一致
- 所有 API 调用参数与原来完全一致
- 所有状态初始值与原来完全一致
