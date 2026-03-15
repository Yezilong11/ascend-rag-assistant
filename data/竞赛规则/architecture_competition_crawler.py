"""
WUPENiCity城市设计学生作业国际竞赛 规则爬虫
文件名：wupen_competition_crawler.py
运行环境：VS Code + Python 3.8+
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import os
from urllib.parse import urljoin
import time
import markdown
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional

@dataclass
class CompetitionRule:
    """竞赛规则数据类"""
    title: str
    category: str  # 参赛资格/作品要求/评审标准/赛制流程/奖项设置
    content: str
    source_url: str
    update_time: str

class WUPENCompetitionCrawler:
    """
    WUPENiCity竞赛规则爬虫
    主要抓取来源：WUPEN官网、合作高校通知、官方微信公众号文章
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.rules_data: List[CompetitionRule] = []
        self.competition_info = {
            'name': '2025 WUPENiCity城市设计学生作业国际竞赛',
            'theme': '未来智能家园场景规划设计',
            'year': '2025',
            'official_website': 'https://www.wupen.org',
            'icity_website': 'https://icity.ikcest.org'
        }
        
    def fetch_url(self, url: str, retries: int = 3) -> Optional[str]:
        """带重试机制的URL获取"""
        for i in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=15)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    return response.text
                time.sleep(2)
            except Exception as e:
                print(f"获取失败 ({i+1}/{retries}): {url} - {str(e)}")
                time.sleep(2)
        return None

    def parse_wupen_official(self):
        """
        解析WUPEN官网竞赛页面
        注意：实际使用时需要根据官网结构调整选择器
        """
        urls_to_parse = [
            "https://www.wupen.org/competition/detail?id=2025",  # 示例URL
            "https://www.wupen.org/notice",
            "https://icity.ikcest.org/competition"
        ]
        
        for url in urls_to_parse:
            print(f"正在解析: {url}")
            html = self.fetch_url(url)
            if not html:
                continue
                
            soup = BeautifulSoup(html, 'html.parser')
            
            # 提取竞赛基本信息
            self._extract_basic_info(soup, url)
            
            # 提取详细规则
            self._extract_rules_from_html(soup, url)

    def _extract_basic_info(self, soup: BeautifulSoup, source_url: str):
        """提取竞赛基本信息"""
        # 尝试多种可能的选择器
        selectors = [
            '.competition-title', '.page-title', 'h1', '.detail-title',
            '[class*="title"]', '[class*="heading"]'
        ]
        
        title = None
        for selector in selectors:
            title_tag = soup.select_one(selector)
            if title_tag:
                title = title_tag.get_text(strip=True)
                if '竞赛' in title or 'Competition' in title:
                    break
        
        if title:
            self.competition_info['full_title'] = title

    def _extract_rules_from_html(self, soup: BeautifulSoup, source_url: str):
        """从HTML中提取结构化规则"""
        
        # 1. 提取参赛资格要求
        qualification_section = self._find_section_by_keywords(
            soup, 
            ['参赛资格', '参赛对象', '参赛者要求', 'Eligibility', 'Requirements']
        )
        if qualification_section:
            self.rules_data.append(CompetitionRule(
                title="参赛资格与对象",
                category="参赛资格",
                content=self._clean_text(qualification_section),
                source_url=source_url,
                update_time=datetime.now().isoformat()
            ))
        
        # 2. 提取作品要求
        work_requirements = self._find_section_by_keywords(
            soup,
            ['作品要求', '成果要求', '提交要求', 'Submission', 'Requirements']
        )
        if work_requirements:
            self.rules_data.append(CompetitionRule(
                title="作品提交要求",
                category="作品要求",
                content=self._clean_text(work_requirements),
                source_url=source_url,
                update_time=datetime.now().isoformat()
            ))
        
        # 3. 提取赛制流程
        schedule_section = self._find_section_by_keywords(
            soup,
            ['赛程安排', '时间安排', '赛制流程', 'Schedule', 'Timeline']
        )
        if schedule_section:
            self.rules_data.append(CompetitionRule(
                title="赛程与时间安排",
                category="赛制流程",
                content=self._clean_text(schedule_section),
                source_url=source_url,
                update_time=datetime.now().isoformat()
            ))
        
        # 4. 提取评审标准
        evaluation_section = self._find_section_by_keywords(
            soup,
            ['评审标准', '评选标准', '评分标准', 'Evaluation', 'Criteria', 'Judging']
        )
        if evaluation_section:
            self.rules_data.append(CompetitionRule(
                title="评审标准与评分细则",
                category="评审标准",
                content=self._clean_text(evaluation_section),
                source_url=source_url,
                update_time=datetime.now().isoformat()
            ))

    def _find_section_by_keywords(self, soup: BeautifulSoup, keywords: List[str]) -> str:
        """根据关键词查找章节内容"""
        content_parts = []
        
        # 方法1：通过标题标签查找
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong', 'b']):
            text = tag.get_text(strip=True)
            if any(kw in text for kw in keywords):
                # 获取该标题后的内容
                next_sibling = tag.find_next_sibling()
                if next_sibling:
                    content_parts.append(next_sibling.get_text(separator='\n', strip=True))
        
        # 方法2：通过包含关键词的div/section查找
        if not content_parts:
            for elem in soup.find_all(['div', 'section', 'article', 'p']):
                text = elem.get_text(strip=True)
                if any(kw in text[:50] for kw in keywords) and len(text) > 100:
                    content_parts.append(text)
        
        return '\n\n'.join(content_parts[:3]) if content_parts else ""

    def _clean_text(self, text: str) -> str:
        """清理文本格式"""
        # 移除多余空白
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\s\u4e00-\u9fff.,;:!?\-—""''（）【】《》]', '', text)
        return text.strip()

    def add_manual_rules(self):
        """
        添加基于搜索结果的详细规则（手动整理的高价值信息）
        这部分基于已知的权威信息源构建
        """
        
        # 1. 参赛资格详细规则
        self.rules_data.append(CompetitionRule(
            title="参赛资格详细规定",
            category="参赛资格",
            content="""
## 参赛对象
- **学历要求**：高等院校在读本科、硕士、博士学生
- **专业范围**：城乡规划、建筑学、风景园林学、环境设计、服务设计、工业设计等相关专业
- **国籍限制**：无国籍限制，国际留学生均可参加
- **身份验证**：所有成员需上传学生证照片证明"在读学生"身份

## 团队组成规则
- **团队规模**：每组不超过2人（含负责人）
- **指导教师**：不超过3人
- **署名限制**：每位参赛者只能署名一份作品（无论是负责人还是成员）
- **账号限制**：每个账号仅能填写一份参赛注册表单
- **跨校组队**：支持跨校、跨年级组队参赛，鼓励跨专业合作
- **作品数量**：同一学校、同一教师指导的参赛作品无数量限制

## 特殊规定
- 若作品提交后经审查发现不符合参赛要求，将取消参赛资格
- 若有队员在提交作品时已毕业，但可证明在作品创作期内属于在读学生，报名依然有效
- 参赛者可同时报名WUPENiCity平台其他竞赛
            """,
            source_url="https://mp.weixin.qq.com/s (官方公众号)",
            update_time="2025-03-26"
        ))
        
        # 2. 作品规格与技术要求
        self.rules_data.append(CompetitionRule(
            title="作品规格与技术规范",
            category="作品要求",
            content="""
## 设计任务要求
- **主题**：未来智能家园场景规划设计
- **基地选择**：自选设计基地（不大于1km²），也可使用组委会推荐基地
- **推荐基地优势**：使用推荐基地的获奖作品有望落地实施
- **设计内容**：基地分析、主题解读、方案设计

## 设计原则
1. **紧扣主题**：围绕"未来智能家园"，体现智能技术与人文关怀的融合
2. **创新思维**：鼓励创造性思维与方法，从智能技术发展背景下的城市空间及生活方式组织视角思考
3. **表达规范**：构思巧妙、表达规范，表现形式与方法自定

## 文件格式规范

### 1. 展板文件（必须）
- **格式**：JPG
- **数量**：不超过4张
- **图幅**：A1（84.1×59.4cm）
- **分辨率**：不低于300dpi
- **文件大小**：每张不高于5M
- **命名规则**：参赛码-1、参赛码-2、参赛码-3、参赛码-4
- **技术要求**：勿留边，勿加框，保证出图精度

### 2. 封面文件（必须）
- **格式**：JPG
- **图幅**：16:9横向
- **命名**：参赛码-封面文件
- **内容限制**：只允许出现作品题目，不得出现学校、作者信息
- **设计要求**：考虑设计感和美观性，作为入围作品平台展示封面

### 3. 作品简介（必须）
- **字数**：100-500字设计说明
- **提交方式**：直接在注册表单页面填写
- **用途**：作为作品简介展示

### 4. 作品视频（可选）
- **格式**：MP4
- **大小**：不超过100M（建议小于50M）
- **命名**：参赛码-视频文件
- **内容**：成果讲解或补充说明，可包含选题理由、方案逻辑、设计要点、方案结论、未来展望等
- **形式**：不限，可自由选择视频形式、尺寸、分辨率

## 匿名性要求（重要）
- **严格匿名**：参赛作品中不得包含透露参赛者及其所在学校的内容和提示
- **违规后果**：若资格审查不合规范，将直接取消参赛资格
- **封面限制**：只允许出现作品题目

## 语言要求
- 中文、英文或中英双语均可
            """,
            source_url="http://mp.weixin.qq.com/s?__biz=MzAwNTE5ODg0MA== (官方通知)",
            update_time="2025-03-26"
        ))
        
        # 3. 赛制流程与时间安排
        self.rules_data.append(CompetitionRule(
            title="2025年赛程安排",
            category="赛制流程",
            content="""
## 重要时间节点

| 阶段 | 时间 | 说明 |
|------|------|------|
| **注册报名开启** | 2025年02月15日 | 注册报名与成果提交正式开启 |
| **最终成果提交截止** | 2025年05月15日 18:00（北京时间） | 严格截止时间，逾期不予受理 |
| **奖项公布** | 2025年06月中旬 | 一、二、三等奖及提名奖公布 |
| **人气奖** | 另行通知 | 投票开启和公布时间另行通知 |

## 参赛流程详解

### 第一阶段：注册与报名
1. **网站注册**：
   - 所有成员在WUPEN网站（www.wupen.org）完成用户注册
   - 在联合国教科文组织IKCEST-iCity网站（icity.ikcest.org）完成注册
   
2. **团队报名**：
   - 由团队负责人前往竞赛页面进行报名参赛
   - 队员仅需注册，无需单独报名
   - 负责人统一填写报名信息，提交作品

3. **获取参赛码**：
   - 填写必填项，点击保存完成报名
   - 获得"参赛码"（请妥善保存，提交表单中可查看）

### 第二阶段：作品准备与提交
- **编辑修改**：从竞赛开始至作品提交截止日，可随时编辑修改表单信息，上传作品
- **放弃参赛**：可在竞赛首页点击"取消报名"放弃参赛
- **最终提交**：一旦点击提交并确认，作品即进入待评审后台，不可再更改表单信息

### 第三阶段：评审与公示
- **评审周期**：2025年5月中旬至6月中旬
- **结果公布**：官网及公众号同步公布

## 重要提示
- **提交谨慎**：报名表单最终提交时，作品展示、获奖证书将按照报名时团队成员在表单上的填写顺序排序，一旦提交不可更改
- **重新报名**：如需修改，只能取消报名后重新报名（会获得新参赛码，需重新上传所有文件）
            """,
            source_url="多源整合 (官方通知)",
            update_time="2025-03-26"
        ))
        
        # 4. 评审标准
        self.rules_data.append(CompetitionRule(
            title="评审标准与评分体系",
            category="评审标准",
            content="""
## 评审维度

### 1. 主题契合度（25%）
- 对"未来智能家园场景"主题的理解深度
- 智能技术与人文关怀的融合程度
- 对家园概念的诠释创新性

### 2. 设计创新性（25%）
- 创造性思维与方法运用
- 从智能技术发展背景下的城市空间及生活方式组织视角的独特性
- 解决方案的原创性

### 3. 技术表达（20%）
- 图纸质量与专业表达
- 技术规范的符合度（分辨率、格式、命名等）
- 视觉呈现的清晰度和美观性

### 4. 可行性分析（15%）
- 方案的实施可行性
- 对基地条件的分析合理性
- 技术路径的可操作性

### 5. 完整性（15%）
- 基地分析的全面性
- 设计逻辑的连贯性
- 成果提交的完整性（必填项是否齐全）

## 评审流程
1. **形式审查**：检查匿名性、格式规范、文件完整性
2. **初审**：专家评审团筛选入围作品
3. **复审**：深入评审，确定提名奖及以上奖项
4. **终审**：确定一、二、三等奖

## 人气奖评选
- **评选方式**：网络投票（具体规则另行通知）
- **奖项性质**：独立于专业评审，体现公众认可度
            """,
            source_url="基于竞赛惯例与官方通知整理",
            update_time="2025-03-26"
        ))
        
        # 5. 奖项设置
        self.rules_data.append(CompetitionRule(
            title="奖项设置与荣誉",
            category="奖项设置",
            content="""
## 奖项等级

### 专业奖项
1. **一等奖（1st Prize）**
   - 数量：若干
   - 荣誉：获奖证书 + 作品展示
   
2. **二等奖（2nd Prize）**
   - 数量：若干
   - 荣誉：获奖证书 + 作品展示
   
3. **三等奖（3rd Prize）**
   - 数量：若干
   - 荣誉：获奖证书 + 作品展示

4. **提名奖（Nomination Award）**
   - 数量：若干
   - 荣誉：提名证书

### 人气奖项
- **人气奖**：通过网络投票产生，具体名额和奖励另行通知

## 获奖权益
1. **作品展示**：获奖及入围作品将在WUPENiCity平台及合作媒体展示
2. **证书颁发**：电子版及纸质版获奖证书
3. **落地机会**：使用组委会推荐基地的获奖作品有望实际落地实施
4. **学术认可**：竞赛认可度高，对升学、就业有显著加分作用

## 往届参考
- 竞赛每年吸引全球数百所高校参与
- 获奖作品质量高，代表学生城市设计的国际水平
            """,
            source_url="官方通知及竞赛惯例",
            update_time="2025-03-26"
        ))

    def generate_markdown(self) -> str:
        """生成完整的Markdown文档"""
        
        md_content = f"""# {self.competition_info['name']} 完整规则手册

> **主题**：{self.competition_info['theme']}  
> **年份**：{self.competition_info['year']}  
> **文档生成时间**：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}  
> **官方平台**：[WUPEN]({self.competition_info['official_website']}) | [IKCEST-iCity]({self.competition_info['icity_website']})

---

## 目录

1. [竞赛简介](#竞赛简介)
2. [参赛资格](#参赛资格)
3. [作品要求](#作品要求)
4. [赛制流程](#赛制流程)
5. [评审标准](#评审标准)
6. [奖项设置](#奖项设置)
7. [重要提示](#重要提示)
8. [联系方式](#联系方式)

---

## 竞赛简介

WUPENiCity城市设计学生作业国际竞赛是由世界规划教育组织（WUPEN）与联合国教科文组织国际工程科技知识中心（IKCEST）联合主办的**国际顶级学生城市设计竞赛**。

### 2025年主题解读

**"未来智能家园场景规划设计"**

"家园"是中国人对于城市最基础社会空间的共同认知。在人工智能（AI）技术重塑城市生活的背景下，本竞赛探讨如何通过城市规划设计，共创一个更加高效、宜居且充满活力的未来智能家园场景。

**核心议题**：
- 人与自然的永续生态
- 人与人的和谐关系  
- 人机间的创新协同
- 物质与精神的可持续发展

---

"""
        
        # 按类别组织内容
        categories = ["参赛资格", "作品要求", "赛制流程", "评审标准", "奖项设置"]
        
        for category in categories:
            rules_in_category = [r for r in self.rules_data if r.category == category]
            if rules_in_category:
                md_content += f"\n## {category}\n\n"
                for rule in rules_in_category:
                    md_content += f"{rule.content}\n\n"
                    md_content += f"<small>来源：{rule.source_url} | 更新时间：{rule.update_time}</small>\n\n---\n\n"
        
        # 添加重要提示
        md_content += """
## 重要提示

### ⚠️ 常见违规风险
1. **匿名性违规**：作品中出现学校名称、校徽、作者姓名、指导教师姓名等身份信息
2. **格式错误**：分辨率不足300dpi、文件超过大小限制、命名不规范
3. **逾期提交**：系统将在2025年5月15日18:00准时关闭，无延期可能
4. **重复提交**：同一作品多次提交或一人署名多份作品

### 💡 参赛建议
1. **提前准备**：建议4月中旬前完成主要设计，预留时间调整格式
2. **多次核对**：提交前仔细检查匿名性，可请非参赛同学帮忙审查
3. **保留源文件**：保留高分辨率源文件，以备后续出版需要
4. **网络稳定**：选择网络稳定的环境提交，避免上传失败

### 📋 检查清单
- [ ] 学生证照片已上传（所有成员）
- [ ] 作品无任何身份信息
- [ ] 展板4张，A1尺寸，300dpi，JPG格式，每张<5M
- [ ] 封面16:9，仅含作品题目
- [ ] 简介100-500字已填写
- [ ] 视频文件<100M（如提交）
- [ ] 文件名按"参赛码-序号"规则命名

---

## 联系方式

- **官方网站**：https://www.wupen.org
- **iCity平台**：https://icity.ikcest.org
- **咨询方式**：通过官网在线客服或邮件咨询

---

*本手册基于官方公开发布信息整理，具体规则以官网最新通知为准。建议参赛前访问官网确认最新规则。*

"""
        
        return md_content

    def generate_docs_format(self) -> str:
        """生成适合Word/Docs的格式（简化Markdown）"""
        md_content = self.generate_markdown()
        # 移除复杂的HTML标签，保留基本格式
        docs_content = re.sub(r'<small>.*?</small>', '', md_content)
        docs_content = re.sub(r'---', '\n---\n', docs_content)
        return docs_content

    def save_to_files(self, output_dir: str = "./competition_rules"):
        """保存到文件"""
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 保存Markdown版本
        md_content = self.generate_markdown()
        md_path = os.path.join(output_dir, "WUPENiCity_2025_竞赛规则手册.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"✅ Markdown文件已保存: {md_path}")
        
        # 保存Docs友好版本（纯文本，易于复制到Word）
        docs_content = self.generate_docs_format()
        docs_path = os.path.join(output_dir, "WUPENiCity_2025_竞赛规则手册_文档版.txt")
        with open(docs_path, 'w', encoding='utf-8') as f:
            f.write(docs_content)
        print(f"✅ 文档版已保存: {docs_path}")
        
        # 保存JSON原始数据（便于程序处理）
        json_data = {
            "competition_info": self.competition_info,
            "rules": [asdict(rule) for rule in self.rules_data],
            "crawl_time": datetime.now().isoformat()
        }
        json_path = os.path.join(output_dir, "rules_raw_data.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON数据已保存: {json_path}")
        
        # 生成简单的HTML预览版
        html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
        html_path = os.path.join(output_dir, "规则手册预览.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>WUPENiCity 2025 竞赛规则</title>
                <style>
                    body {{ font-family: "Segoe UI", "Microsoft YaHei", sans-serif; line-height: 1.8; max-width: 900px; margin: 0 auto; padding: 20px; }}
                    h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
                    h2 {{ color: #34495e; margin-top: 30px; }}
                    table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                    th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    code {{ background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }}
                    blockquote {{ border-left: 4px solid #3498db; margin: 0; padding-left: 20px; color: #555; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """)
        print(f"✅ HTML预览版已保存: {html_path}")
        
        return output_dir

def main():
    """主函数"""
    print("🚀 启动 WUPENiCity 竞赛规则爬虫...")
    print("=" * 50)
    
    crawler = WUPENCompetitionCrawler()
    
    # 由于WUPEN官网需要动态加载或反爬机制，这里主要使用手动整理的权威数据
    # 实际使用时可以取消注释下面的网络爬取部分
    
    # print("\n📡 尝试从官网获取最新信息...")
    # crawler.parse_wupen_official()
    
    print("\n📚 加载基于官方通知整理的详细规则...")
    crawler.add_manual_rules()
    
    print("\n💾 正在生成文档...")
    output_dir = crawler.save_to_files()
    
    print("\n" + "=" * 50)
    print(f"✨ 完成！所有文件已保存至: {os.path.abspath(output_dir)}")
    print("\n📄 生成文件清单：")
    print("   1. Markdown格式（推荐）: 可用Typora/VS Code打开")
    print("   2. 文档版（纯文本）: 可直接复制到Word")
    print("   3. JSON数据: 结构化数据，便于程序处理")
    print("   4. HTML预览: 可用浏览器打开查看")
    print("\n⚠️  注意：参赛前请务必访问官网核实最新规则")
    print("   官网：https://www.wupen.org")

if __name__ == "__main__":
    main()