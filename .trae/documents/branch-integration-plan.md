# 分支集成计划：feature/multimodal → feature/front_back

## 一、当前状态分析

| 项目 | 信息 |
|------|------|
| 当前分支 | feature/front_back |
| 源分支 | origin/feature/multimodal |
| 工作区状态 | 干净，无未提交的更改 |

## 二、前端技术栈分析

### 2.1 当前分支 (feature/front_back) 的前端结构

| 目录 | 技术栈 | 说明 |
|------|--------|------|
| `frontend/` | React 19 + Vite + Ant Design 6 + Zustand 5 + @xyflow/react | **新框架（主推）** |
| `frontend-demo/` | React 18 + Vite + Ant Design 5 + TailwindCSS + Zustand 4 | 旧框架（保留） |

### 2.2 multimodal 分支的结构

| 目录 | 变更情况 |
|------|----------|
| `frontend/` | **不存在** - multimodal 分支没有这个目录 |
| `frontend-demo/` | 有修改 - 添加了技能树相关组件 |
| `app.py` | 有修改 - 后端逻辑变更 |
| `config/config.yaml` | 有修改 - 配置文件更新 |

### 2.3 关键结论 ✅

**你的新框架（frontend/）完全不会被影响！**

因为 `origin/feature/multimodal` 分支根本没有 `frontend/` 目录，合并时 Git 不会修改这个目录。

## 三、合并策略

### 策略选择： Three-Way Merge（标准合并）

由于两个分支修改的是**不同的目录**：
- multimodal 修改 `frontend-demo/`、`app.py`、`config/config.yaml`
- 当前分支修改 `frontend/`

因此**冲突概率很低**，合并应该是相对平滑的。

## 四、详细执行步骤

### 步骤 1：创建备份分支（安全措施）
```bash
git branch backup/front_back-pre-multimodal-merge
```

### 步骤 2：确保本地分支与远程同步
```bash
git fetch origin
git checkout feature/front_back
git pull origin feature/front_back
```

### 步骤 3：拉取 multimodal 分支
```bash
git fetch origin feature/multimodal
```

### 步骤 4：确认变更范围（代码审查）
```bash
# 查看整体变更统计
git diff origin/feature/front_back..origin/feature/multimodal --stat | Select-String -NotMatch -Pattern "node_modules|__pycache__|chroma_db"

# 查看后端变更
git diff origin/feature/front_back..origin/feature/multimodal --stat -- app.py config/

# 查看前端变更（注意：只影响 frontend-demo/，不影响 frontend/）
git diff origin/feature/front_back..origin/feature/multimodal --stat -- frontend-demo/
```

### 步骤 5：执行合并
```bash
git merge origin/feature/multimodal
```

### 步骤 6：处理冲突（如有）
```bash
# 查看冲突文件
git diff --name-only --diff-filter=U

# 重点关注 frontend-demo/ 目录的冲突
git diff --name-only --diff-filter=U -- frontend-demo/

# 解决冲突后
git add <resolved-file>
git commit
```

### 步骤 7：验证合并结果
```bash
# 检查工作区状态
git status

# 确认 frontend/ 目录未被修改
git diff --stat -- frontend/

# 确认 frontend-demo/ 目录的合并结果
git diff --stat -- frontend-demo/
```

### 步骤 8：构建测试
```bash
# 后端测试
python -m pytest tests/  # 或你的测试命令

# 前端新框架构建测试
cd frontend
npm run build

# 前端旧框架构建测试
cd frontend-demo
npm run build
```

### 步骤 9：推送结果
```bash
git push origin feature/front_back
```

## 五、保护新框架的检查清单

合并后，请验证以下内容：

- [ ] `frontend/` 目录**完全未被修改**
- [ ] `frontend/package.json` 保持不变（React 19, Ant Design 6, Zustand 5）
- [ ] `frontend/src/components/` 目录结构完整
- [ ] `frontend/src/stores/` 目录完整
- [ ] `frontend/` 构建成功

## 六、multimodal 分支带来的是什么？

### 6.1 后端变更 (app.py, config/)
- 需要审查 API 接口变更
- 检查配置变更是否影响现有功能

### 6.2 前端变更 (frontend-demo/)
- 添加了技能树相关组件：
  - `SkillNodeCard.tsx`
  - `SkillTreeCard.tsx`
  - `ChatInput.tsx`, `ChatMessage.tsx`, `ChatWindow.tsx`
  - `FileUploader.tsx`
  - 各页面组件 (`ChatPage.tsx`, `KnowledgeBasePage.tsx`, `SkillTreePage.tsx` 等)
- 这些是**增量添加**，不会影响 `frontend/` 的技能树实现

## 七、潜在冲突点

虽然 `frontend/` 不会被影响，但以下位置可能出现冲突：

| 文件/目录 | 冲突可能性 | 处理方式 |
|-----------|------------|----------|
| `app.py` | 中 | 手动审查合并 |
| `config/config.yaml` | 低 | 手动审查合并 |
| `frontend-demo/` | 中 | 两个版本合并，可能需要选择 |
| `package-lock.json` | 高 | 使用 `--ancestor` 策略解决 |

## 八、回滚方案

如合并后出现问题：
```bash
# 方法1：重置到备份分支
git reset --hard backup/front_back-pre-multimodal-merge

# 方法2：如果已推送
git revert -m 1 <merge-commit-hash>
```

## 九、最终确认

合并完成后，请确认：
1. ✅ `frontend/` 新框架完全未被动过
2. ✅ `frontend-demo/` 正常合并
3. ✅ 后端 `app.py` 和 `config/` 正常
4. ✅ 所有测试通过
5. ✅ 构建成功
