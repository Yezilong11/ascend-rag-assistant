# RSS资讯表格操作列溢出问题修复方案

## 问题描述

表格最右侧操作列中，"导入知识库"按钮文字被截断显示为"导入知"，部分内容溢出到表格容器外部。

## 问题分析

### 当前代码结构

**ArticleList.tsx 第86-103行**：
```tsx
{
  title: '操作',
  key: 'action',
  width: 150,  // 操作列宽度只有150px
  render: (_: unknown, record: Article) => (
    <Space size="small">
      <Button type="link" size="small" icon={<EyeOutlined />} onClick={() => handleViewDetail(record)}>
        查看
      </Button>
      <IngestToKBButton articleId={record.id} size="small" type="link" />
    </Space>
  ),
}
```

### 根本原因

1. **操作列宽度不足**：150px 无法容纳"查看"和"导入知识库"两个按钮
2. **按钮未设置 `white-space: nowrap`**：可能导致文字换行
3. **父容器无横向滚动**：`Table` 组件默认不换行时会截断内容

## 解决方案

### 方案1：添加横向滚动 + 增加操作列宽度（推荐）

**修改 ArticleList.tsx**：

1. 给 Table 外层 div 添加 `overflow-x: auto` 和 `min-width`
2. 将操作列宽度从 150 增加到 220
3. 确保按钮文字不换行

```tsx
<div style={{ overflowX: 'auto', minWidth: 900 }}>
  <Table
    columns={columns}
    // ... 其他props
    style={{ background: 'transparent', minWidth: 900 }}
  />
</div>
```

### 方案2：使用图标 + 缩短文字

将操作列按钮改为图标按钮或缩短文字：

```tsx
// 查看 → 👁️ 或 "查"
// 导入知识库 → 📥 或 "导入"

<Button type="link" size="small" icon={<EyeOutlined />} title="查看文章">
  查
</Button>
<IngestToKBButton articleId={record.id} size="small" type="link" shortText />
```

### 方案3：调整列宽比例 + 固定操作列

让标题列自动填充剩余空间，操作列固定宽度。

---

## 实施步骤

### 步骤1：修改 ArticleList.tsx

1. 在 Table 外层包裹 div，设置 `overflow-x: auto`
2. 增加操作列宽度到 200
3. 确保按钮样式不换行

### 步骤2：可选修改 IngestToKBButton.tsx

添加 `shortText` 属性，支持缩写显示：

```tsx
{shortText ? '导入' : '导入知识库'}
```

---

## 预期效果

- 表格可横向滚动，所有列完整显示
- 操作列两个按钮完整显示，不再截断
- 保持原有功能和交互
