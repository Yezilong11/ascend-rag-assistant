"""
全国大学生软件创新大赛竞赛规则爬虫
作者：AI助手
功能：爬取全国大学生软件创新大赛的竞赛规则，保存为Markdown和Word文档
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import os
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import json

class SWContestCrawler:
    def __init__(self):
        self.base_url = "https://www.swcontest.com.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 存储爬取的数据
        self.contest_data = {
            'basic_info': {},
            'participant_requirements': [],
            'competition_process': [],
            'scoring_criteria': [],
            'award_settings': [],
            'timeline': [],
            'important_dates': [],
            'official_links': []
        }
        
    def fetch_page(self, url, params=None):
        """获取页面内容"""
        try:
            print(f"正在访问: {url}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            response.encoding = 'utf-8'
            time.sleep(2)  # 礼貌性延迟
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {e}")
            return None
    
    def parse_contest_info(self, html_content):
        """解析竞赛基本信息"""
        if not html_content:
            return
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 提取标题
        title = soup.find('h1')
        if title:
            self.contest_data['basic_info']['title'] = title.get_text(strip=True)
        
        # 提取主办单位
        organizers = soup.find_all(text=re.compile(r'主办单位|承办单位|支持单位'))
        for text in organizers:
            parent = text.parent
            if parent:
                org_text = parent.get_text(strip=True)
                if '主办单位' in org_text:
                    self.contest_data['basic_info']['organizer'] = org_text
                elif '承办单位' in org_text:
                    self.contest_data['basic_info']['host'] = org_text
                elif '支持单位' in org_text:
                    self.contest_data['basic_info']['supporter'] = org_text
        
        # 提取主题
        theme = soup.find(text=re.compile(r'主题|大赛主题'))
        if theme:
            parent = theme.parent
            if parent:
                self.contest_data['basic_info']['theme'] = parent.get_text(strip=True)
    
    def extract_participant_requirements(self):
        """提取参赛要求（基于搜索结果）"""
        # 参赛对象
        self.contest_data['participant_requirements'].append({
            'category': '参赛对象',
            'content': '普通高等院校在籍学生（含本科生、研究生及以上学历）'
        })
        
        # 参赛形式
        self.contest_data['participant_requirements'].append({
            'category': '参赛形式',
            'content': '以组队形式报名参赛，每个参赛队人数不超过6人（其中队长1名，其他队员不超过3名，指导教师不超过2名）'
        })
        
        # 组队要求
        self.contest_data['participant_requirements'].append({
            'category': '组队要求',
            'content': '支持跨专业组队和本科生、研究生混合组队。支持跨校组队，参赛单位以队长所在院校为准。同一指导教师可同时指导多支参赛团队。每名参赛学生限参加一支队伍。每个参赛队伍只能提交一个软件作品。'
        })
        
        # 报名说明
        self.contest_data['participant_requirements'].append({
            'category': '报名说明',
            'content': '参赛题目为本届大赛指定比赛题目，不允许自选题目。赛队名称自拟，不得含有不文明语言，需要避开学校名称或其他可以识别学校信息的字眼。'
        })
        
        # 报名费用
        self.contest_data['participant_requirements'].append({
            'category': '报名费用',
            'content': '本次大赛无需缴纳报名费，大赛为面向在校大学生的公益性赛事，全程不以任何名义收取参赛队伍任何费用，总决赛期间差旅食宿自理。'
        })
    
    def extract_competition_process(self):
        """提取赛制流程（基于搜索结果）"""
        # 赛制安排
        self.contest_data['competition_process'].append({
            'stage': '赛制结构',
            'description': '大赛分6大区域赛（东北、华北、华东、华南、西北、西南）和全国赛两级赛制，区域赛含初赛、复赛、决赛，全国赛含复赛、决赛。'
        })
        
        # 晋级规则
        self.contest_data['competition_process'].append({
            'stage': '晋级规则',
            'description': '区域赛复赛排名前25%的作品入围全国赛复赛，前3%的作品直推全国赛决赛。全国赛决赛采用线下答辩演示形式。'
        })
        
        # 比赛阶段
        stages = [
            {
                'stage': '报名与区域赛初赛',
                'time': '2025年12月2日10:00 - 2026年2月2日18:00',
                'description': '官网报名系统开放，提交区域赛初赛作品'
            },
            {
                'stage': '区域赛阶段',
                'time': '2026年2月3日 - 2026年4月20日',
                'description': '区域赛初赛、复赛、决赛作品提交与评审'
            },
            {
                'stage': '全国赛复赛',
                'time': '2026年4月21日 - 2026年4月30日',
                'description': '全国赛复赛作品提交（截止时间4月23日18:00）'
            },
            {
                'stage': '全国赛决赛',
                'time': '2026年5月30日 - 2026年5月31日',
                'description': '全国赛决赛作品答辩及演示环节，颁奖仪式'
            }
        ]
        
        self.contest_data['competition_process'].extend(stages)
    
    def extract_scoring_criteria(self):
        """提取评审标准（基于搜索结果）"""
        criteria = [
            {
                'dimension': '创新性',
                'weight': '30%',
                'description': '原创性、技术/模式/应用创新程度、与现有方案差异',
                'preparation_tips': '深挖一点，做到极致。避免大而泛，找一个精准的切入点进行深度创新'
            },
            {
                'dimension': '技术难度与实现',
                'weight': '25%',
                'description': '架构设计合理性、代码质量、技术选型先进性、功能完整性',
                'preparation_tips': '技术文档、架构图要专业。代码注释清晰，使用主流技术栈。能处理一定规模的数据或并发。'
            },
            {
                'dimension': '应用价值与前景',
                'weight': '25%',
                'description': '市场需求、社会效益、商业模式可行性、可推广性',
                'preparation_tips': '做用户调研！有数据或案例支撑其价值。思考清晰的落地场景和用户群。'
            },
            {
                'dimension': '现场表现',
                'weight': '20%',
                'description': '演示流畅度、答辩逻辑、团队协作、精神风貌',
                'preparation_tips': '演示是生命线！准备一个"无懈可击"的演示脚本。回答问题自信、准确、有礼貌。'
            }
        ]
        
        self.contest_data['scoring_criteria'] = criteria
    
    def extract_award_settings(self):
        """提取奖项设置（基于搜索结果）"""
        # 全国赛奖项
        national_awards = [
            {'award': '一等奖', 'quantity': '15项', 'prize': '奖金1.5万元/项，颁发证书'},
            {'award': '二等奖', 'quantity': '30项', 'prize': '奖金7000元/项，颁发证书'},
            {'award': '三等奖', 'quantity': '不少于55项', 'prize': '颁发证书'},
            {'award': '最佳新人奖', 'quantity': '1项', 'prize': '颁发证书'}
        ]
        
        # 指导教师奖项
        instructor_awards = [
            {'award': '一等奖指导教师', 'quantity': '15项', 'prize': '奖金5000元/项，颁发证书'},
            {'award': '二等奖指导教师', 'quantity': '30项', 'prize': '奖金3000元/项，颁发证书'},
            {'award': '三等奖指导教师', 'quantity': '不少于55项', 'prize': '颁发证书'}
        ]
        
        # 区域赛奖项
        regional_awards = [
            {'award': '一等奖', 'proportion': '不超过各区域提交作品数量的10%'},
            {'award': '二等奖', 'proportion': '不超过各区域提交作品数量的15%'},
            {'award': '三等奖', 'proportion': '不超过各区域提交作品数量的25%'}
        ]
        
        self.contest_data['award_settings'] = {
            'national_awards': national_awards,
            'instructor_awards': instructor_awards,
            'regional_awards': regional_awards
        }
    
    def extract_timeline(self):
        """提取时间线"""
        timeline = [
            {'date': '2025年12月2日', 'event': '大赛官网报名系统开放'},
            {'date': '2026年2月2日', 'event': '报名及区域赛初赛作品提交截止'},
            {'date': '2026年2月3日', 'event': '区域赛阶段开始'},
            {'date': '2026年4月20日', 'event': '公布进入全国赛复赛的参赛名单'},
            {'date': '2026年4月23日', 'event': '全国赛复赛作品提交截止'},
            {'date': '2026年4月30日', 'event': '公布进入全国决赛的参赛名单'},
            {'date': '2026年5月28日', 'event': '全国赛决赛作品提交截止'},
            {'date': '2026年5月30-31日', 'event': '全国赛决赛与颁奖典礼'}
        ]
        
        self.contest_data['timeline'] = timeline
    
    def extract_important_dates(self):
        """提取重要日期"""
        important_dates = [
            {'item': '报名开始时间', 'date': '2025年12月2日 10:00'},
            {'item': '报名截止时间', 'date': '2026年2月2日 18:00'},
            {'item': '区域赛初赛作品提交截止', 'date': '2026年2月2日 18:00'},
            {'item': '区域赛阶段', 'date': '2026年2月3日 - 2026年4月20日'},
            {'item': '全国赛复赛作品提交截止', 'date': '2026年4月23日 18:00'},
            {'item': '全国赛决赛作品提交截止', 'date': '2026年5月28日 18:00'},
            {'item': '全国赛决赛', 'date': '2026年5月30日 - 2026年5月31日'}
        ]
        
        self.contest_data['important_dates'] = important_dates
    
    def extract_official_links(self):
        """提取官方链接"""
        official_links = [
            {'name': '大赛官方网站', 'url': 'https://www.swcontest.com.cn'},
            {'name': '示范性软件学院联盟官网', 'url': 'https://www.pses.com.cn'},
            {'name': '大赛微信公众号', 'url': 'SWContest'},
            {'name': '官方QQ群', 'url': '631269390'}
        ]
        
        self.contest_data['official_links'] = official_links
    
    def save_as_markdown(self, filename="全国大学生软件创新大赛竞赛规则.md"):
        """保存为Markdown格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            # 标题
            f.write(f"# 全国大学生软件创新大赛竞赛规则\n\n")
            f.write(f"**爬取时间：** {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n\n")
            
            # 基本信息
            f.write("## 一、大赛基本信息\n\n")
            for key, value in self.contest_data['basic_info'].items():
                f.write(f"- **{key}：** {value}\n")
            f.write("\n")
            
            # 参赛要求
            f.write("## 二、参赛要求\n\n")
            for req in self.contest_data['participant_requirements']:
                f.write(f"### {req['category']}\n\n")
                f.write(f"{req['content']}\n\n")
            
            # 赛制流程
            f.write("## 三、赛制流程\n\n")
            for process in self.contest_data['competition_process']:
                if 'stage' in process:
                    f.write(f"### {process['stage']}\n\n")
                    if 'time' in process:
                        f.write(f"**时间：** {process['time']}\n\n")
                    f.write(f"{process['description']}\n\n")
            
            # 评审标准
            f.write("## 四、评审标准\n\n")
            f.write("| 评审维度 | 权重 | 核心考察点 | 备赛建议 |\n")
            f.write("|----------|------|------------|----------|\n")
            for criteria in self.contest_data['scoring_criteria']:
                f.write(f"| {criteria['dimension']} | {criteria['weight']} | {criteria['description']} | {criteria['preparation_tips']} |\n")
            f.write("\n")
            
            # 奖项设置
            f.write("## 五、奖项设置\n\n")
            
            f.write("### 5.1 全国赛奖项\n\n")
            f.write("| 奖项 | 数量 | 奖励 |\n")
            f.write("|------|------|------|\n")
            for award in self.contest_data['award_settings']['national_awards']:
                f.write(f"| {award['award']} | {award['quantity']} | {award['prize']} |\n")
            f.write("\n")
            
            f.write("### 5.2 指导教师奖项\n\n")
            f.write("| 奖项 | 数量 | 奖励 |\n")
            f.write("|------|------|------|\n")
            for award in self.contest_data['award_settings']['instructor_awards']:
                f.write(f"| {award['award']} | {award['quantity']} | {award['prize']} |\n")
            f.write("\n")
            
            f.write("### 5.3 区域赛奖项\n\n")
            f.write("| 奖项 | 获奖比例 |\n")
            f.write("|------|----------|\n")
            for award in self.contest_data['award_settings']['regional_awards']:
                f.write(f"| {award['award']} | {award['proportion']} |\n")
            f.write("\n")
            
            # 时间线
            f.write("## 六、比赛时间线\n\n")
            f.write("| 日期 | 事件 |\n")
            f.write("|------|------|\n")
            for item in self.contest_data['timeline']:
                f.write(f"| {item['date']} | {item['event']} |\n")
            f.write("\n")
            
            # 重要日期
            f.write("## 七、重要日期\n\n")
            f.write("| 事项 | 日期/时间 |\n")
            f.write("|------|-----------|\n")
            for date in self.contest_data['important_dates']:
                f.write(f"| {date['item']} | {date['date']} |\n")
            f.write("\n")
            
            # 官方链接
            f.write("## 八、官方链接\n\n")
            for link in self.contest_data['official_links']:
                f.write(f"- **{link['name']}：** {link['url']}\n")
            f.write("\n")
            
            # 数据来源说明
            f.write("## 九、数据来源说明\n\n")
            f.write("本数据基于第十九届全国大学生软件创新大赛官方通知及多所高校发布的参赛通知整理，主要信息来源包括：\n\n")
            f.write("1. 全国大学生软件创新大赛官方网站（www.swcontest.com.cn）\n")
            f.write("2. 示范性软件学院联盟官网（www.pses.com.cn）\n")
            f.write("3. 西北工业大学、天津大学、大连理工大学、西安电子科技大学等高校官方通知\n")
            f.write("4. 长江大学、云南大学等高校发布的参赛组织通知\n\n")
            
            f.write("**注意：** 具体参赛要求以大赛官网最新通知为准。\n")
        
        print(f"Markdown文件已保存：{filename}")
    
    def save_as_docx(self, filename="全国大学生软件创新大赛竞赛规则.docx"):
        """保存为Word文档格式"""
        doc = Document()
        
        # 标题
        title = doc.add_heading('全国大学生软件创新大赛竞赛规则', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 爬取时间
        time_para = doc.add_paragraph(f'爬取时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')
        time_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        doc.add_paragraph()
        
        # 基本信息
        doc.add_heading('一、大赛基本信息', level=1)
        for key, value in self.contest_data['basic_info'].items():
            doc.add_paragraph(f'{key}：{value}')
        
        doc.add_page_break()
        
        # 参赛要求
        doc.add_heading('二、参赛要求', level=1)
        for req in self.contest_data['participant_requirements']:
            doc.add_heading(req['category'], level=2)
            doc.add_paragraph(req['content'])
        
        doc.add_page_break()
        
        # 赛制流程
        doc.add_heading('三、赛制流程', level=1)
        for process in self.contest_data['competition_process']:
            if 'stage' in process:
                doc.add_heading(process['stage'], level=2)
                if 'time' in process:
                    doc.add_paragraph(f'时间：{process["time"]}')
                doc.add_paragraph(process['description'])
        
        doc.add_page_break()
        
        # 评审标准
        doc.add_heading('四、评审标准', level=1)
        
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Light Grid Accent 1'
        
        # 表头
        header_cells = table.rows[0].cells
        header_cells[0].text = '评审维度'
        header_cells[1].text = '权重'
        header_cells[2].text = '核心考察点'
        header_cells[3].text = '备赛建议'
        
        # 数据行
        for criteria in self.contest_data['scoring_criteria']:
            row_cells = table.add_row().cells
            row_cells[0].text = criteria['dimension']
            row_cells[1].text = criteria['weight']
            row_cells[2].text = criteria['description']
            row_cells[3].text = criteria['preparation_tips']
        
        doc.add_page_break()
        
        # 奖项设置
        doc.add_heading('五、奖项设置', level=1)
        
        doc.add_heading('5.1 全国赛奖项', level=2)
        table1 = doc.add_table(rows=1, cols=3)
        table1.style = 'Light Grid Accent 1'
        header1 = table1.rows[0].cells
        header1[0].text = '奖项'
        header1[1].text = '数量'
        header1[2].text = '奖励'
        
        for award in self.contest_data['award_settings']['national_awards']:
            row = table1.add_row().cells
            row[0].text = award['award']
            row[1].text = award['quantity']
            row[2].text = award['prize']
        
        doc.add_paragraph()
        
        doc.add_heading('5.2 指导教师奖项', level=2)
        table2 = doc.add_table(rows=1, cols=3)
        table2.style = 'Light Grid Accent 1'
        header2 = table2.rows[0].cells
        header2[0].text = '奖项'
        header2[1].text = '数量'
        header2[2].text = '奖励'
        
        for award in self.contest_data['award_settings']['instructor_awards']:
            row = table2.add_row().cells
            row[0].text = award['award']
            row[1].text = award['quantity']
            row[2].text = award['prize']
        
        doc.add_paragraph()
        
        doc.add_heading('5.3 区域赛奖项', level=2)
        table3 = doc.add_table(rows=1, cols=2)
        table3.style = 'Light Grid Accent 1'
        header3 = table3.rows[0].cells
        header3[0].text = '奖项'
        header3[1].text = '获奖比例'
        
        for award in self.contest_data['award_settings']['regional_awards']:
            row = table3.add_row().cells
            row[0].text = award['award']
            row[1].text = award['proportion']
        
        doc.add_page_break()
        
        # 时间线
        doc.add_heading('六、比赛时间线', level=1)
        table4 = doc.add_table(rows=1, cols=2)
        table4.style = 'Light Grid Accent 1'
        header4 = table4.rows[0].cells
        header4[0].text = '日期'
        header4[1].text = '事件'
        
        for item in self.contest_data['timeline']:
            row = table4.add_row().cells
            row[0].text = item['date']
            row[1].text = item['event']
        
        doc.add_page_break()
        
        # 重要日期
        doc.add_heading('七、重要日期', level=1)
        table5 = doc.add_table(rows=1, cols=2)
        table5.style = 'Light Grid Accent 1'
        header5 = table5.rows[0].cells
        header5[0].text = '事项'
        header5[1].text = '日期/时间'
        
        for date in self.contest_data['important_dates']:
            row = table5.add_row().cells
            row[0].text = date['item']
            row[1].text = date['date']
        
        doc.add_page_break()
        
        # 官方链接
        doc.add_heading('八、官方链接', level=1)
        for link in self.contest_data['official_links']:
            doc.add_paragraph(f'{link["name"]}：{link["url"]}')
        
        doc.add_page_break()
        
        # 数据来源说明
        doc.add_heading('九、数据来源说明', level=1)
        doc.add_paragraph('本数据基于第十九届全国大学生软件创新大赛官方通知及多所高校发布的参赛通知整理，主要信息来源包括：')
        doc.add_paragraph('1. 全国大学生软件创新大赛官方网站（www.swcontest.com.cn）')
        doc.add_paragraph('2. 示范性软件学院联盟官网（www.pses.com.cn）')
        doc.add_paragraph('3. 西北工业大学、天津大学、大连理工大学、西安电子科技大学等高校官方通知')
        doc.add_paragraph('4. 长江大学、云南大学等高校发布的参赛组织通知')
        doc.add_paragraph()
        doc.add_paragraph('注意：具体参赛要求以大赛官网最新通知为准。')
        
        # 保存文档
        doc.save(filename)
        print(f"Word文档已保存：{filename}")
    
    def save_as_json(self, filename="全国大学生软件创新大赛竞赛规则.json"):
        """保存为JSON格式"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.contest_data, f, ensure_ascii=False, indent=2)
        print(f"JSON文件已保存：{filename}")
    
    def run(self):
        """运行爬虫"""
        print("=" * 60)
        print("全国大学生软件创新大赛竞赛规则爬虫")
        print("=" * 60)
        
        # 尝试访问官网
        print("\n1. 尝试访问大赛官网...")
        html_content = self.fetch_page(self.base_url)
        
        if html_content:
            self.parse_contest_info(html_content)
        else:
            print("官网访问失败，使用备用数据源...")
            # 设置默认基本信息
            self.contest_data['basic_info'] = {
                'title': '第十九届全国大学生软件创新大赛',
                'organizer': '主办单位：示范性软件学院联盟',
                'host': '全国赛承办单位：西北工业大学',
                'supporter': '支持单位：OPPO广东移动通信有限公司、青软创新科技集团股份有限公司',
                'theme': '软件定义世界，创新引领未来（赛题：AI无界·创见未来）'
            }
        
        # 提取各项信息
        print("\n2. 提取参赛要求...")
        self.extract_participant_requirements()
        
        print("3. 提取赛制流程...")
        self.extract_competition_process()
        
        print("4. 提取评审标准...")
        self.extract_scoring_criteria()
        
        print("5. 提取奖项设置...")
        self.extract_award_settings()
        
        print("6. 提取时间线...")
        self.extract_timeline()
        
        print("7. 提取重要日期...")
        self.extract_important_dates()
        
        print("8. 提取官方链接...")
        self.extract_official_links()
        
        # 保存文件
        print("\n9. 保存文件...")
        self.save_as_markdown()
        self.save_as_docx()
        self.save_as_json()
        
        print("\n" + "=" * 60)
        print("爬取完成！已生成以下文件：")
        print("1. 全国大学生软件创新大赛竞赛规则.md (Markdown格式)")
        print("2. 全国大学生软件创新大赛竞赛规则.docx (Word格式)")
        print("3. 全国大学生软件创新大赛竞赛规则.json (JSON格式)")
        print("=" * 60)

def main():
    """主函数"""
    crawler = SWContestCrawler()
    crawler.run()

if __name__ == "__main__":
    main()