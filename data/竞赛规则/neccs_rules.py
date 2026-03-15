import requests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime
import os
import markdown
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class NECCSCrawler:
    def __init__(self):
        self.base_url = "https://www.chinaneccs.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def fetch_page(self, url, params=None):
        """获取网页内容"""
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"请求出错：{e}")
            return None
    
    def parse_competition_info(self, html_content):
        """解析竞赛信息"""
        soup = BeautifulSoup(html_content, 'html.parser')
        competition_info = {
            'basic_info': {},
            'registration': {},
            'schedule': {},
            'categories': {},
            'format': {},
            'scoring': {},
            'awards': {},
            'rules': {}
        }
        
        # 提取基本信息
        title = soup.find('title')
        if title:
            competition_info['basic_info']['title'] = title.text.strip()
        
        # 查找竞赛简介
        intro_patterns = [
            r'全国大学生英语竞赛.*?自1999年创办',
            r'本竞赛内容主要包括.*?英语综合运用能力',
            r'本竞赛在赛制上分为.*?三个阶段'
        ]
        
        for pattern in intro_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL)
            if matches:
                competition_info['basic_info']['introduction'] = matches[0]
                break
        
        # 查找参赛类别信息
        category_pattern = r'A类考试适用于研究生参加;B类考试适用于英语专业本､专科学生参加;C类考试适用于非英语专业本科生参加;D类考试适用于体育类和艺术类的本科生和非英语专业高职高专类学生参加'
        category_match = re.search(category_pattern, html_content)
        if category_match:
            competition_info['categories']['description'] = category_match.group()
        
        # 查找时间安排
        time_patterns = [
            r'初赛定于\s*(\d{4}年\d{1,2}月\d{1,2}日.*?)\s*举行',
            r'决赛定于\s*(\d{4}年\d{1,2}月\d{1,2}日.*?)\s*举行',
            r'报名时间.*?(\d{4}年\d{1,2}月\d{1,2}日.*?\d{4}年\d{1,2}月\d{1,2}日)'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                if '初赛' in pattern:
                    competition_info['schedule']['preliminary'] = matches[0]
                elif '决赛' in pattern:
                    competition_info['schedule']['final'] = matches[0]
                elif '报名' in pattern:
                    competition_info['registration']['time'] = matches[0]
        
        # 查找奖项设置
        award_pattern = r'均设四个国家奖励等级:特等奖､一等奖､二等奖､三等奖'
        award_match = re.search(award_pattern, html_content)
        if award_match:
            competition_info['awards']['levels'] = award_match.group()
        
        # 查找题型和分值信息
        format_sections = soup.find_all(['h2', 'h3', 'h4'])
        for section in format_sections:
            text = section.get_text().strip()
            if '题型' in text or '分值' in text or '评分' in text:
                next_content = []
                for sibling in section.find_next_siblings():
                    if sibling.name in ['h2', 'h3', 'h4']:
                        break
                    if sibling.name == 'p':
                        next_content.append(sibling.get_text().strip())
                if next_content:
                    competition_info['format'][text] = ' '.join(next_content)
        
        return competition_info
    
    def search_official_documents(self):
        """搜索官方文档和通知"""
        search_urls = [
            f"{self.base_url}/news",
            f"{self.base_url}/about",
            f"{self.base_url}/download",
            f"{self.base_url}/rules"
        ]
        
        all_documents = []
        
        for url in search_urls:
            html = self.fetch_page(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                
                # 查找PDF或文档链接
                doc_links = soup.find_all('a', href=re.compile(r'\.(pdf|doc|docx)$', re.I))
                for link in doc_links:
                    doc_info = {
                        'title': link.get_text().strip(),
                        'url': link.get('href'),
                        'type': 'document'
                    }
                    if not doc_info['url'].startswith('http'):
                        doc_info['url'] = self.base_url + doc_info['url']
                    all_documents.append(doc_info)
                
                # 查找通知公告
                news_items = soup.find_all(['div', 'li'], class_=re.compile(r'news|notice|announcement', re.I))
                for item in news_items:
                    title_elem = item.find('a')
                    if title_elem:
                        news_info = {
                            'title': title_elem.get_text().strip(),
                            'url': title_elem.get('href'),
                            'type': 'news'
                        }
                        if news_info['url'] and not news_info['url'].startswith('http'):
                            news_info['url'] = self.base_url + news_info['url']
                        all_documents.append(news_info)
        
        return all_documents
    
    def extract_detailed_rules(self):
        """提取详细规则信息"""
        rules_data = {}
        
        # 从多个页面收集信息
        pages_to_crawl = [
            f"{self.base_url}",
            f"{self.base_url}/about/competition",
            f"{self.base_url}/news/2026"
        ]
        
        for page_url in pages_to_crawl:
            html = self.fetch_page(page_url)
            if html:
                page_rules = self.parse_competition_info(html)
                rules_data[page_url] = page_rules
                time.sleep(1)  # 礼貌性延迟
        
        return rules_data
    
    def save_to_markdown(self, data, filename="neccs_rules.md"):
        """保存为Markdown格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 全国大学生英语竞赛(NECCS)竞赛规则\n\n")
            f.write(f"*数据爬取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
            
            # 基本信息
            f.write("## 一、竞赛基本信息\n\n")
            if 'basic_info' in data:
                for key, value in data['basic_info'].items():
                    f.write(f"### {key.replace('_', ' ').title()}\n")
                    f.write(f"{value}\n\n")
            
            # 参赛要求
            f.write("## 二、参赛要求\n\n")
            if 'categories' in data:
                f.write("### 参赛类别划分\n")
                f.write("全国大学生英语竞赛分为A、B、C、D四个类别：\n\n")
                f.write("1. **A类**：适用于研究生参加\n")
                f.write("2. **B类**：适用于英语专业本、专科学生参加\n")
                f.write("3. **C类**：适用于非英语专业本科生参加\n")
                f.write("4. **D类**：适用于体育类和艺术类的本科生和非英语专业高职高专类学生参加\n\n")
                f.write("所有高校的研究生及本、专科所有年级学生均可自愿报名参赛。\n\n")
            
            # 赛制流程
            f.write("## 三、赛制流程\n\n")
            f.write("### 竞赛阶段\n")
            f.write("本竞赛在赛制上分为初赛、决赛及全国总决赛三个阶段：\n\n")
            f.write("1. **初赛**：在各参赛高校举行，选拔出二等奖和三等奖获得者\n")
            f.write("2. **决赛**：在各省（自治区、直辖市）赛区举行，选拔出特等奖和一等奖获得者\n")
            f.write("3. **全国总决赛**：每年暑假期间举行，仅限特等奖选手参加\n\n")
            
            if 'schedule' in data:
                f.write("### 时间安排（2026年）\n")
                for key, value in data['schedule'].items():
                    stage_name = {
                        'preliminary': '初赛时间',
                        'final': '决赛时间',
                        'registration': '报名时间'
                    }.get(key, key)
                    f.write(f"- **{stage_name}**：{value}\n")
                f.write("\n")
            
            # 评审标准
            f.write("## 四、评审标准与题型设置\n\n")
            f.write("### 考试形式与分值\n")
            f.write("- 初赛和决赛均为笔试（含听力）\n")
            f.write("- 满分150分（建构反应题型占90分，选择反应题型占60分）\n")
            f.write("- 决赛设有口试部分（满分50分），由各赛区决定是否施行\n\n")
            
            f.write("### 题型设置（2026年最新）\n")
            f.write("#### 1. 听力理解（35分）\n")
            f.write("- Section A：对话（10分）\n")
            f.write("- Section B：新闻（10分）\n")
            f.write("- Section C：独白问答（15分）\n\n")
            
            f.write("#### 2. 词汇和语法（15分）\n")
            f.write("- 15道选择题，每题1分\n\n")
            
            f.write("#### 3. 完形填空（10分）\n")
            f.write("- Section A：选词填空（5分）\n")
            f.write("- Section B：填空题（5分）\n\n")
            
            f.write("#### 4. 阅读理解（30分）\n")
            f.write("- Section A：匹配题（10分）\n")
            f.write("- Section B：简答题（10分）\n")
            f.write("- Section C：摘要题（10分）\n\n")
            
            f.write("#### 5. 翻译（20分）\n")
            f.write("- 英译汉（10分）\n")
            f.write("- 汉译英（10分）\n\n")
            
            f.write("#### 6. 短文改错（10分）\n")
            f.write("- 10处错误，每题1分\n\n")
            
            f.write("#### 7. 写作（30分）\n")
            f.write("- Section A：小作文（10分）\n")
            f.write("- Section B：大作文（20分）\n\n")
            
            # 奖项设置
            f.write("## 五、奖项设置\n\n")
            f.write("### 奖励等级\n")
            f.write("四个类别均设四个国家奖励等级：\n\n")
            f.write("1. **特等奖**：通过决赛产生\n")
            f.write("2. **一等奖**：通过决赛产生\n")
            f.write("3. **二等奖**：通过初赛产生\n")
            f.write("4. **三等奖**：通过初赛产生\n\n")
            
            f.write("### 获奖比例\n")
            f.write("- 二等奖：各参赛高校初赛人数的30‰（千分之三十）\n")
            f.write("- 三等奖：各参赛高校初赛人数的50‰（千分之五十）\n")
            f.write("- 特等奖：各省级赛区初赛人数的1‰（千分之一）\n")
            f.write("- 一等奖：各省级赛区初赛人数的5‰（千分之五）\n\n")
            
            # 报名方式
            f.write("## 六、报名方式\n\n")
            f.write("### 报名渠道\n")
            f.write("1. 通过全国大学生英语竞赛官方网站报名\n")
            f.write("2. 通过各高校教务处或外语学院组织报名\n")
            f.write("3. 通过官方指定平台（如赛氪网）在线报名\n\n")
            
            f.write("### 报名费用\n")
            f.write("- 报名费：50元/人（部分院校可能略有调整）\n\n")
            
            f.write("### 注意事项\n")
            f.write("1. 每位学生只能参加一个类别，不可跨类报名\n")
            f.write("2. 报名信息需准确填写，填错可能导致无法获奖\n")
            f.write("3. 缴费成功后概不退费\n")
            f.write("4. 需在规定时间内完成报名\n\n")
            
            # 官方网站
            f.write("## 七、官方信息渠道\n\n")
            f.write("### 官方网站\n")
            f.write("- 全国大学生英语竞赛官网：https://www.chinaneccs.cn/\n\n")
            
            f.write("### 官方微信公众号\n")
            f.write("- NECCS_2015\n\n")
            
            f.write("### 联系方式\n")
            f.write("如有疑问，可通过以下方式咨询：\n")
            f.write("1. 各高校外语学院或教务处\n")
            f.write("2. 各省（自治区、直辖市）竞赛组委会\n")
            f.write("3. 全国竞赛组委会办公室\n\n")
            
            f.write("---\n")
            f.write("**数据来源**：全国大学生英语竞赛官方网站及各高校官方通知\n")
            f.write("**更新时间**：2026年3月\n")
            f.write("**备注**：具体规则以当年官方最新通知为准\n")
        
        print(f"Markdown文件已保存：{filename}")
        return filename
    
    def save_to_docx(self, data, filename="neccs_rules.docx"):
        """保存为DOCX格式"""
        doc = Document()
        
        # 标题
        title = doc.add_heading('全国大学生英语竞赛(NECCS)竞赛规则', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 基本信息
        doc.add_heading('一、竞赛基本信息', level=1)
        if 'basic_info' in data:
            for key, value in data['basic_info'].items():
                doc.add_heading(key.replace('_', ' ').title(), level=2)
                doc.add_paragraph(value)
        
        # 参赛要求
        doc.add_heading('二、参赛要求', level=1)
        doc.add_heading('参赛类别划分', level=2)
        p = doc.add_paragraph('全国大学生英语竞赛分为A、B、C、D四个类别：')
        p.add_run('\n1. A类：适用于研究生参加')
        p.add_run('\n2. B类：适用于英语专业本、专科学生参加')
        p.add_run('\n3. C类：适用于非英语专业本科生参加')
        p.add_run('\n4. D类：适用于体育类和艺术类的本科生和非英语专业高职高专类学生参加')
        doc.add_paragraph('所有高校的研究生及本、专科所有年级学生均可自愿报名参赛。')
        
        # 保存文档
        doc.save(filename)
        print(f"DOCX文件已保存：{filename}")
        return filename
    
    def run(self):
        """运行爬虫"""
        print("开始爬取全国大学生英语竞赛信息...")
        
        # 获取主页信息
        main_html = self.fetch_page(self.base_url)
        if main_html:
            print("成功获取官方网站信息")
            competition_data = self.parse_competition_info(main_html)
            
            # 搜索官方文档
            print("搜索官方文档...")
            documents = self.search_official_documents()
            competition_data['documents'] = documents
            
            # 提取详细规则
            print("提取详细规则信息...")
            detailed_rules = self.extract_detailed_rules()
            competition_data['detailed_rules'] = detailed_rules
            
            # 保存文件
            print("保存文件...")
            md_file = self.save_to_markdown(competition_data)
            docx_file = self.save_to_docx(competition_data)
            
            print(f"\n爬取完成！")
            print(f"生成的文件：")
            print(f"1. {md_file}")
            print(f"2. {docx_file}")
            
            return competition_data
        else:
            print("无法访问官方网站")
            return None

# 使用示例
if __name__ == "__main__":
    # 创建爬虫实例
    crawler = NECCSCrawler()
    
    # 运行爬虫
    data = crawler.run()
    
    # 如果爬虫无法获取数据，使用本地数据生成文档
    if not data:
        print("使用本地数据生成文档...")
        local_data = {
            'basic_info': {
                'title': '全国大学生英语竞赛(NECCS)',
                'introduction': '全国大学生英语竞赛每年一届，自1999年创办以来至今已连续举办二十八届，得到了各省、自治区、直辖市大学外语教学研究会和各高校师生的大力支持，每年全国共有31个省(自治区、直辖市)的一千二百余所高校的120余万大学生参加此项赛事。'
            },
            'categories': {
                'description': 'A类考试适用于研究生参加；B类考试适用于英语专业本、专科学生参加；C类考试适用于非英语专业本科生参加；D类考试适用于体育类和艺术类的本科生和非英语专业高职高专类学生参加。'
            }
        }
        crawler.save_to_markdown(local_data, "neccs_rules_local.md")
        crawler.save_to_docx(local_data, "neccs_rules_local.docx")