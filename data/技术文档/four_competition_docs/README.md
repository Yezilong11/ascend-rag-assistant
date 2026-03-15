# 4个竞赛技术文档爬取详细报告

> 生成时间: 2026-03-15 12:39:27
> 爬虫版本: FourCompetitionCrawler v1.0

## 📊 执行摘要

| 指标 | 数值 |
|------|------|
| **总竞赛数** | 4 |
| **成功爬取** | 4 |
| **失败** | 0 |
| **总页面数** | 8 |
| **成功页面** | 1 |
| **下载文件数** | 0 |

---


## 1. 中美青年创客大赛

**官网**: [https://chinaus-maker.cscse.edu.cn/](https://chinaus-maker.cscse.edu.cn/)  
**描述**: 教育部主办，以'共创未来'为主题的中美青年交流赛事  
**状态**: ✅ completed  
**页面统计**: 成功 0 / 总计 3  

### 爬取的文档列表


---

## 2. 天作奖国际大学生建筑设计竞赛

**官网**: [https://jzss.cbpt.cnki.net/portal](https://jzss.cbpt.cnki.net/portal)  
**描述**: 《建筑师》杂志主办的国际建筑设计竞赛  
**状态**: ✅ completed  
**页面统计**: 成功 1 / 总计 1  

### 爬取的文档列表

#### 📄 建筑师
- **来源URL**: [https://jzss.cbpt.cnki.net/portal...](https://jzss.cbpt.cnki.net/portal)
- **Markdown**: [markdown\天作奖国际大学生建筑设计竞赛_portal_20260315_123815.md](markdown\天作奖国际大学生建筑设计竞赛_portal_20260315_123815.md)
- **HTML备份**: [raw_html\天作奖国际大学生建筑设计竞赛_portal_20260315_123815.html](raw_html\天作奖国际大学生建筑设计竞赛_portal_20260315_123815.html)


**联系邮箱**: thearchitect1979@cabp.com.cn  
**微信公众号**: thearchitect1979  

---

## 3. 城市设计学生作业国际竞赛

**官网**: [http://www.wupen.org/](http://www.wupen.org/)  
**描述**: WUPENiCity城市设计学生作业国际竞赛，世界规划教育组织主办  
**状态**: ✅ completed  
**页面统计**: 成功 0 / 总计 2  

### 爬取的文档列表


---

## 4. 城市可持续调研报告国际竞赛

**官网**: [http://www.wupen.org/](http://www.wupen.org/)  
**描述**: WUPENiCity城市可持续调研报告国际竞赛，联合国教科文组织iCity平台联合主办  
**状态**: ✅ completed  
**页面统计**: 成功 0 / 总计 2  

### 爬取的文档列表


---

## 📖 使用指南

### 文件结构说明
four_competition_docs/
├── markdown/          # Markdown格式文档（推荐查看）
│   └── *.md          # 每个网页对应的Markdown文件
├── raw_html/          # 原始HTML备份
│   └── *.html        # 完整的网页HTML源码
├── downloads/         # 下载的PDF、DOC等文件
│   └── */            # 按竞赛分类的子文件夹
├── metadata.json      # 详细的元数据（JSON格式）
└── README.md          # 本报告

### 如何查看文档
1. **推荐**: 使用Markdown阅读器打开 `markdown/` 目录下的 `.md` 文件
2. **完整备份**: 查看 `raw_html/` 目录下的 `.html` 文件（保留原始样式）
3. **下载文件**: 查看 `downloads/` 目录下的PDF、Word等附件

### 注意事项
1. 所有文档仅供学习参考，请以官网最新发布为准
2. 部分文件可能需要特定软件打开（如PDF阅读器）
3. 建议定期重新运行爬虫以获取最新通知
4. 如遇链接失效，请访问竞赛官网获取最新信息

---

*报告由 FourCompetitionCrawler 自动生成*
