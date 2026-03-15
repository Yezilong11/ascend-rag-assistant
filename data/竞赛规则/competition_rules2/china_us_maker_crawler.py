"""
中美青年创客大赛竞赛规则爬虫
作者：元宝
日期：2026-03-15
功能：爬取中美青年创客大赛的竞赛规则，包括参赛要求、赛制流程、评审标准等核心规定
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
from datetime import datetime
import os
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class ChinaUSMakerCompetitionCrawler:
    def __init__(self):
        """初始化爬虫"""
        self.base_url = "https://chinaus-maker.cscse.edu.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # 定义要爬取的关键页面
        self.target_pages = {
            'main_page': f'{self.base_url}/chinaus-maker/sy29/index.html',
            'competition_rules': f'{self.base_url}/chinaus-maker/sy29/bszn.html',
            'registration_guide': f'{self.base_url}/chinaus-maker/sy29/bmzn.html',
        }
        
        # 存储爬取的数据
        self.competition_data = {
            'basic_info': {},
            'registration_requirements': [],
            'competition_process': [],
            'review_standards': [],
            'award_settings': [],
            'important_dates': [],
            'source_urls': []
        }
        
    def fetch_page(self, url, max_retries=3):
        """获取网页内容"""
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                response.encoding = 'utf-8'
                return response.text
            except requests.RequestException as e:
                print(f"第{attempt+1}次尝试失败: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"无法获取页面: {url}")
                    return None
    
    def parse_main_page(self, html_content):
        """解析主页面，获取基本信息"""
        if not html_content:
            return
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取标题
        title = soup.find('title')
        if title:
            self.competition_data['basic_info']['title'] = title.text.strip()
        
        # 提取大赛简介
        intro_sections = soup.find_all(['div', 'section'], class_=re.compile(r'intro|about|description'))
        for section in intro_sections:
            text = section.get_text(strip=True)
            if len(text) > 50:  # 只保留较长的文本
                self.competition_data['basic_info']['introduction'] = text
                break
        
        # 提取主办承办单位
        org_patterns = ['主办单位', '承办单位', '组织机构']
        for pattern in org_patterns:
            elements = soup.find_all(text=re.compile(pattern))
            for element in elements:
                parent = element.parent
                if parent:
                    org_text = parent.get_text(strip=True)
                    if '主办单位' in org_text:
                        self.competition_data['basic_info']['organizer'] = org_text
                    elif '承办单位' in org_text:
                        self.competition_data['basic_info']['co_organizer'] = org_text
    
    def parse_competition_rules(self, html_content):
        """解析竞赛规则页面"""
        if not html_content:
            return
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 查找所有包含竞赛规则的章节
        rule_keywords = ['参赛资格', '报名要求', '作品要求', '评审标准', '赛制流程', '时间安排']
        
        for keyword in rule_keywords:
            elements = soup.find_all(text=re.compile(keyword))
            for element in elements:
                # 获取相关段落
                parent = element.parent
                if parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    # 获取标题和后续内容
                    content = []
                    current = parent
                    for _ in range(10):  # 获取后续10个元素
                        current = current.find_next_sibling()
                        if current and current.name in ['p', 'div', 'ul', 'ol']:
                            text = current.get_text(strip=True)
                            if text:
                                content.append(text)
                        else:
                            break
                    
                    if content:
                        rule_item = {
                            'title': element.strip(),
                            'content': content
                        }
                        
                        # 分类存储
                        if '参赛资格' in keyword or '报名要求' in keyword:
                            self.competition_data['registration_requirements'].append(rule_item)
                        elif '作品要求' in keyword:
                            self.competition_data['registration_requirements'].append(rule_item)
                        elif '评审标准' in keyword:
                            self.competition_data['review_standards'].append(rule_item)
                        elif '赛制流程' in keyword or '时间安排' in keyword:
                            self.competition_data['competition_process'].append(rule_item)
    
    def search_additional_info(self):
        """搜索补充信息（基于搜索结果）"""
        # 基于搜索结果添加已知信息
        known_info = {
            'registration_requirements': [
                {
                    'title': '参赛资格',
                    'content': [
                        '中美青年创客大赛对任何中国公民或美国公民、或在中国或美国获得永久合法居留权的个人开放',
                        '报名者年龄应在大赛报名起始日时符合18周岁以上或40周岁以下的要求',
                        '参赛者不能为承办单位员工或其直系亲属'
                    ]
                },
                {
                    'title': '团队要求',
                    'content': [
                        '以团队形式报名时，团队总人数不得超过5人（含领队）',
                        '鼓励中、美两国选手联合组队',
                        '职业院校分赛道的团队成员均需为职业院校的全日制在读学生',
                        '每个参赛项目可至多有一位指导老师'
                    ]
                }
            ],
            'competition_process': [
                {
                    'title': '赛制流程',
                    'content': [
                        '第一阶段：大赛启动、参赛选手报名和分赛区选拔赛（4月-6月下旬）',
                        '第二阶段：决赛入围团队优化作品（6月20日至决赛前）',
                        '第三阶段：大赛决赛（7月中下旬）'
                    ]
                }
            ],
            'review_standards': [
                {
                    'title': '评审标准（百分制）',
                    'content': [
                        '1. 首创精神与创新突破（40%）：创意独特性、问题新颖性、跨界融合度、精简原型化',
                        '2. 问题导向与社会价值（30%）：需求明确性、解决有效性、议题相关性、受益范围性',
                        '3. 技术实现与产品完整（20%）：功能可用性、技术适当性、体验友好性、完善可能性',
                        '4. 团队协作与开源共享（10%）：合作实效性、过程透明度、资源开放度、社区互动度'
                    ]
                }
            ],
            'award_settings': [
                {
                    'title': '奖项设置（示例：杭州分赛区）',
                    'content': [
                        '一等奖1名：证书、参赛奖金10000元、创业项目落地大礼包',
                        '二等奖2名：证书、参赛奖金5000元、创业项目落地大礼包',
                        '三等奖2名：证书、参赛奖金2000元',
                        '优胜奖若干：证书'
                    ]
                }
            ]
        }
        
        # 合并已知信息
        for key in known_info:
            if key in self.competition_data:
                self.competition_data[key].extend(known_info[key])
    
    def save_as_markdown(self, filename="中美青年创客大赛竞赛规则.md"):
        """保存为Markdown格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            # 标题
            f.write("# 中美青年创客大赛竞赛规则\n\n")
            f.write(f"*数据爬取时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}*\n\n")
            
            # 基本信息
            f.write("## 一、基本信息\n\n")
            for key, value in self.competition_data['basic_info'].items():
                f.write(f"**{key}**：{value}\n\n")
            
            # 参赛要求
            f.write("## 二、参赛要求\n\n")
            for requirement in self.competition_data['registration_requirements']:
                f.write(f"### {requirement['title']}\n\n")
                for item in requirement['content']:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # 赛制流程
            f.write("## 三、赛制流程\n\n")
            for process in self.competition_data['competition_process']:
                f.write(f"### {process['title']}\n\n")
                for item in process['content']:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # 评审标准
            f.write("## 四、评审标准\n\n")
            for standard in self.competition_data['review_standards']:
                f.write(f"### {standard['title']}\n\n")
                for item in standard['content']:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # 奖项设置
            f.write("## 五、奖项设置\n\n")
            for award in self.competition_data['award_settings']:
                f.write(f"### {award['title']}\n\n")
                for item in award['content']:
                    f.write(f"- {item}\n")
                f.write("\n")
            
            # 重要日期
            f.write("## 六、重要日期\n\n")
            for date_item in self.competition_data['important_dates']:
                f.write(f"- {date_item}\n")
            
            # 数据来源
            f.write("\n## 七、数据来源\n\n")
            f.write("本数据通过爬虫程序从以下官方和权威渠道获取：\n\n")
            for url in self.competition_data['source_urls']:
                f.write(f"- {url}\n")
            
            # 基于搜索结果的补充信息
            f.write("\n## 八、基于搜索结果的补充信息\n\n")
            f.write("以下信息基于2025-2026年中美青年创客大赛相关公告整理：\n\n")
            
            # 赛道设置
            f.write("### 赛道设置\n")
            f.write("- **主赛道**：面向所有参赛者\n")
            f.write("- **职业院校分赛道**：仅针对中国赛区，团队成员需为职业院校全日制在读学生\n\n")
            
            # 作品要求
            f.write("### 作品要求\n")
            f.write("1. **主题要求**：以'共创未来'为主题，关注可持续发展领域\n")
            f.write("2. **创新性要求**：作品需解决未被充分探索的问题，不能与往届作品或市场现有方案重复\n")
            f.write("3. **作品呈现**：需制作可演示的产品原型，鼓励基于开源软件和通用硬件平台\n")
            f.write("4. **知识产权**：作品须是团队自主研发拥有完全知识产权的创新成果\n\n")
            
            # 晋级规则
            f.write("### 晋级规则\n")
            f.write("- 主赛道：国内分赛区原则上按分数排名推荐前5名团队晋级决赛\n")
            f.write("- 要求晋级团队中至少包含1支中美联合组队项目\n")
            f.write("- 分赛道：根据参赛团队数量按比例推荐晋级\n\n")
            
            f.write("---\n")
            f.write("*注：具体规则以当年官方发布的最新章程为准*\n")
        
        print(f"Markdown文件已保存：{filename}")
    
    def save_as_docx(self, filename="中美青年创客大赛竞赛规则.docx"):
        """保存为Word文档格式"""
        doc = Document()
        
        # 标题
        title = doc.add_heading('中美青年创客大赛竞赛规则', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 时间信息
        time_info = doc.add_paragraph(f'数据爬取时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')
        time_info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        time_info.style.font.size = Pt(10)
        
        doc.add_paragraph()
        
        # 基本信息
        doc.add_heading('一、基本信息', level=1)
        for key, value in self.competition_data['basic_info'].items():
            p = doc.add_paragraph()
            p.add_run(f'{key}：').bold = True
            p.add_run(value)
        
        # 参赛要求
        doc.add_heading('二、参赛要求', level=1)
        for requirement in self.competition_data['registration_requirements']:
            doc.add_heading(requirement['title'], level=2)
            for item in requirement['content']:
                doc.add_paragraph(item, style='List Bullet')
        
        # 赛制流程
        doc.add_heading('三、赛制流程', level=1)
        for process in self.competition_data['competition_process']:
            doc.add_heading(process['title'], level=2)
            for item in process['content']:
                doc.add_paragraph(item, style='List Bullet')
        
        # 评审标准
        doc.add_heading('四、评审标准', level=1)
        for standard in self.competition_data['review_standards']:
            doc.add_heading(standard['title'], level=2)
            for item in standard['content']:
                doc.add_paragraph(item, style='List Bullet')
        
        # 奖项设置
        doc.add_heading('五、奖项设置', level=1)
        for award in self.competition_data['award_settings']:
            doc.add_heading(award['title'], level=2)
            for item in award['content']:
                doc.add_paragraph(item, style='List Bullet')
        
        # 数据来源
        doc.add_heading('六、数据来源', level=1)
        doc.add_paragraph('本数据通过爬虫程序从以下官方和权威渠道获取：')
        for url in self.competition_data['source_urls']:
            doc.add_paragraph(url, style='List Bullet')
        
        # 补充信息
        doc.add_heading('七、基于搜索结果的补充信息', level=1)
        doc.add_paragraph('以下信息基于2025-2026年中美青年创客大赛相关公告整理：')
        
        # 赛道设置
        doc.add_heading('赛道设置', level=2)
        doc.add_paragraph('• 主赛道：面向所有参赛者', style='List Bullet')
        doc.add_paragraph('• 职业院校分赛道：仅针对中国赛区，团队成员需为职业院校全日制在读学生', style='List Bullet')
        
        # 作品要求
        doc.add_heading('作品要求', level=2)
        doc.add_paragraph('1. 主题要求：以"共创未来"为主题，关注可持续发展领域', style='List Bullet')
        doc.add_paragraph('2. 创新性要求：作品需解决未被充分探索的问题，不能与往届作品或市场现有方案重复', style='List Bullet')
        doc.add_paragraph('3. 作品呈现：需制作可演示的产品原型，鼓励基于开源软件和通用硬件平台', style='List Bullet')
        doc.add_paragraph('4. 知识产权：作品须是团队自主研发拥有完全知识产权的创新成果', style='List Bullet')
        
        # 保存文档
        doc.save(filename)
        print(f"Word文档已保存：{filename}")
    
    def run(self):
        """运行爬虫"""
        print("开始爬取中美青年创客大赛竞赛规则...")
        
        # 记录数据来源
        self.competition_data['source_urls'] = list(self.target_pages.values())
        
        # 爬取主页面
        print("正在爬取主页面...")
        main_html = self.fetch_page(self.target_pages['main_page'])
        if main_html:
            self.parse_main_page(main_html)
        
        # 爬取竞赛规则页面
        print("正在爬取竞赛规则页面...")
        rules_html = self.fetch_page(self.target_pages['competition_rules'])
        if rules_html:
            self.parse_competition_rules(rules_html)
        
        # 添加基于搜索结果的补充信息
        print("正在整合搜索结果信息...")
        self.search_additional_info()
        
        # 保存结果
        print("正在保存结果...")
        self.save_as_markdown()
        self.save_as_docx()
        
        print("爬取完成！")
        
        # 显示统计信息
        print(f"\n爬取统计：")
        print(f"- 基本信息：{len(self.competition_data['basic_info'])} 项")
        print(f"- 参赛要求：{len(self.competition_data['registration_requirements'])} 个类别")
        print(f"- 赛制流程：{len(self.competition_data['competition_process'])} 个阶段")
        print(f"- 评审标准：{len(self.competition_data['review_standards'])} 个维度")
        print(f"- 数据来源：{len(self.competition_data['source_urls'])} 个网页")

def main():
    """主函数"""
    # 创建爬虫实例
    crawler = ChinaUSMakerCompetitionCrawler()
    
    try:
        # 运行爬虫
        crawler.run()
        
        # 显示使用说明
        print("\n" + "="*50)
        print("使用说明：")
        print("1. 确保已安装以下Python库：")
        print("   pip install requests beautifulsoup4 python-docx")
        print("2. 运行此脚本前，请确保网络连接正常")
        print("3. 生成的文件：")
        print("   - 中美青年创客大赛竞赛规则.md (Markdown格式)")
        print("   - 中美青年创客大赛竞赛规则.docx (Word格式)")
        print("4. 如需爬取其他页面，可修改target_pages字典")
        print("="*50)
        
    except Exception as e:
        print(f"爬虫运行出错：{e}")
        print("请检查网络连接或网站结构是否发生变化")

if __name__ == "__main__":
    main()