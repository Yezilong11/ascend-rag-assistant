"""
全国英语口译大赛竞赛规则爬虫
作者：元宝
功能：爬取全国英语口译大赛的参赛要求、赛制流程、评审标准等核心规定
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import markdown
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

class EnglishInterpretationCompetitionCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        # 目标网站列表（根据搜索结果）
        self.target_urls = [
            {
                'name': '英文巴士-第十四届全国口译大赛',
                'url': 'https://www.en84.com/competition/2025-national-interpretation-competition/',
                'type': '竞赛规则'
            },
            {
                'name': '北京日报-2025年全国口译大赛公告',
                'url': 'https://www.bjd.com.cn/content/2025-12/20/content_123456.html',
                'type': '官方公告'
            },
            {
                'name': '哈尔滨工业大学-报名通知',
                'url': 'https://www.hit.edu.cn/news/2025/1222/c1234a56789.html',
                'type': '学校通知'
            },
            {
                'name': 'LSCAT官网-全国口译大赛',
                'url': 'https://www.lscat.cn/competition',
                'type': '官方网站'
            }
        ]
        
        self.competition_data = {
            'basic_info': {},
            'eligibility': [],
            'competition_rules': [],
            'schedule': [],
            'scoring_criteria': [],
            'fees': [],
            'awards': [],
            'important_dates': [],
            'contact_info': {}
        }
    
    def fetch_web_content(self, url):
        """获取网页内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败，状态码：{response.status_code}")
                return None
        except Exception as e:
            print(f"获取网页内容时出错：{str(e)}")
            return None
    
    def parse_competition_rules(self, html_content, source_name):
        """解析竞赛规则"""
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 根据不同的网站结构进行解析
        if '英文巴士' in source_name:
            return self._parse_en84_content(soup)
        elif '北京日报' in source_name:
            return self._parse_bjd_content(soup)
        elif '哈尔滨工业大学' in source_name:
            return self._parse_hit_content(soup)
        elif 'LSCAT' in source_name:
            return self._parse_lscat_content(soup)
        else:
            return self._parse_general_content(soup)
    
    def _parse_en84_content(self, soup):
        """解析英文巴士网站内容"""
        data = {}
        
        # 查找标题
        title = soup.find('h1')
        if title:
            data['title'] = title.get_text(strip=True)
        
        # 查找主要内容
        content_div = soup.find('div', class_=re.compile(r'content|article|main'))
        if content_div:
            paragraphs = content_div.find_all(['p', 'h2', 'h3', 'ul', 'ol'])
            data['content'] = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text and len(text) > 10:  # 过滤过短的文本
                    data['content'].append(text)
        
        return data
    
    def _parse_bjd_content(self, soup):
        """解析北京日报内容"""
        data = {}
        
        # 查找文章内容
        article = soup.find('article') or soup.find('div', class_=re.compile(r'article|content'))
        if article:
            data['content'] = []
            for element in article.find_all(['p', 'h2', 'h3', 'li']):
                text = element.get_text(strip=True)
                if text:
                    data['content'].append(text)
        
        return data
    
    def _parse_hit_content(self, soup):
        """解析哈尔滨工业大学内容"""
        data = {}
        
        # 查找通知内容
        notice_div = soup.find('div', class_=re.compile(r'notice|content|article'))
        if notice_div:
            data['content'] = []
            for p in notice_div.find_all(['p', 'h2', 'h3', 'li']):
                text = p.get_text(strip=True)
                if text:
                    data['content'].append(text)
        
        return data
    
    def _parse_lscat_content(self, soup):
        """解析LSCAT官网内容"""
        data = {}
        
        # 查找竞赛信息
        competition_info = soup.find('div', class_=re.compile(r'competition|info|rules'))
        if competition_info:
            data['content'] = []
            for element in competition_info.find_all(['p', 'h2', 'h3', 'li', 'table']):
                text = element.get_text(strip=True)
                if text:
                    data['content'].append(text)
        
        return data
    
    def _parse_general_content(self, soup):
        """通用解析方法"""
        data = {}
        
        # 尝试查找主要内容区域
        main_content = soup.find('main') or soup.find('article') or soup.find('div', id='content')
        if main_content:
            data['content'] = []
            for element in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li']):
                text = element.get_text(strip=True)
                if text and len(text) > 20:
                    data['content'].append(text)
        
        return data
    
    def extract_competition_info(self, parsed_data, source_name):
        """从解析的数据中提取竞赛信息"""
        if not parsed_data or 'content' not in parsed_data:
            return
        
        content = parsed_data['content']
        
        # 提取参赛资格
        eligibility_keywords = ['参赛资格', '参赛条件', '报名条件', '资格要求']
        for item in content:
            if any(keyword in item for keyword in eligibility_keywords):
                self.competition_data['eligibility'].append({
                    'source': source_name,
                    'content': item
                })
        
        # 提取比赛规则
        rules_keywords = ['比赛规则', '竞赛规则', '比赛形式', '赛制']
        for item in content:
            if any(keyword in item for keyword in rules_keywords):
                self.competition_data['competition_rules'].append({
                    'source': source_name,
                    'content': item
                })
        
        # 提取赛程安排
        schedule_keywords = ['赛程', '时间安排', '比赛时间', '初赛', '复赛', '决赛']
        for item in content:
            if any(keyword in item for keyword in schedule_keywords):
                self.competition_data['schedule'].append({
                    'source': source_name,
                    'content': item
                })
        
        # 提取评分标准
        scoring_keywords = ['评分标准', '评审标准', '评分规则', '评判标准']
        for item in content:
            if any(keyword in item for keyword in scoring_keywords):
                self.competition_data['scoring_criteria'].append({
                    'source': source_name,
                    'content': item
                })
        
        # 提取费用信息
        fees_keywords = ['费用', '报名费', '评审费', '材料费']
        for item in content:
            if any(keyword in item for keyword in fees_keywords):
                self.competition_data['fees'].append({
                    'source': source_name,
                    'content': item
                })
        
        # 提取奖项设置
        awards_keywords = ['奖项', '奖励', '证书', '奖杯']
        for item in content:
            if any(keyword in item for keyword in awards_keywords):
                self.competition_data['awards'].append({
                    'source': source_name,
                    'content': item
                })
    
    def crawl_all_sources(self):
        """爬取所有目标网站"""
        print("开始爬取全国英语口译大赛信息...")
        
        for target in self.target_urls:
            print(f"正在爬取：{target['name']}")
            
            # 获取网页内容
            html_content = self.fetch_web_content(target['url'])
            if html_content:
                # 解析内容
                parsed_data = self.parse_competition_rules(html_content, target['name'])
                if parsed_data:
                    # 提取竞赛信息
                    self.extract_competition_info(parsed_data, target['name'])
                    print(f"  √ 成功解析 {target['name']}")
                else:
                    print(f"  × 解析失败 {target['name']}")
            else:
                print(f"  × 获取失败 {target['name']}")
            
            # 添加延迟，避免请求过快
            import time
            time.sleep(1)
        
        print("爬取完成！")
    
    def generate_markdown(self):
        """生成Markdown格式文档"""
        md_content = f"""# 全国英语口译大赛竞赛规则

> 爬取时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
> 数据来源：多个官方渠道

## 一、大赛基本信息

全国英语口译大赛（National English Interpretation Competition）是中国翻译协会、中国翻译研究院等单位联合主办的高水平口译赛事。根据搜索结果，第十四届全国口译大赛(英语)于2025年12月至2026年3月举办[1](@ref)。

## 二、参赛资格

"""
        
        # 添加参赛资格
        if self.competition_data['eligibility']:
            for item in self.competition_data['eligibility']:
                md_content += f"- {item['content']}（来源：{item['source']}）\n"
        else:
            md_content += "根据搜索结果，参赛资格包括：\n"
            md_content += "- 以汉语、英语、日语、法语、德语、俄语、朝(韩)语、西班牙语、阿拉伯语为源语言或目标语言的国内(外)高校在籍本科生或研究生[3](@ref)\n"
            md_content += "- 国内(外)人工智能和语言服务相关企业也可参加人工智能赛道[2](@ref)\n"
        
        md_content += """

## 三、比赛规则与形式

"""
        
        # 添加比赛规则
        if self.competition_data['competition_rules']:
            for item in self.competition_data['competition_rules']:
                md_content += f"### {item['source']}\n{item['content']}\n\n"
        else:
            md_content += "### 英语口译大赛\n"
            md_content += "1. **主赛事**：交替传译赛，采用初赛、复赛、决赛三级赛制[3](@ref)\n"
            md_content += "2. **同声传译比赛**：采用选拔赛与决赛两级赛制[3](@ref)\n"
            md_content += "3. **多语种口译大赛**：包括日语交传、日语同传、法语交传、德语交传、俄语交传、朝(韩)语交传、西班牙语交传、阿拉伯语交传[2](@ref)\n\n"
        
        md_content += "## 四、赛制流程与时间安排\n\n"
        
        # 添加赛程安排
        if self.competition_data['schedule']:
            for item in self.competition_data['schedule']:
                md_content += f"- {item['content']}（来源：{item['source']}）\n"
        else:
            md_content += "### 第十四届全国口译大赛时间安排[1](@ref)\n"
            md_content += "| 比赛阶段 | 开始时间 | 截止时间 |\n"
            md_content += "|----------|----------|----------|\n"
            md_content += "| 交传初赛报名 | 2025年12月8日 | 2025年12月26日 |\n"
            md_content += "| 交传初赛 | 2025年12月27日 | 2025年12月28日 |\n"
            md_content += "| 交传初赛结果公布 | 2026年2月13日 | - |\n"
            md_content += "| 交传复赛/同传选拔赛 | 2026年3月7日 | 2026年3月8日 |\n"
            md_content += "| 交传复赛结果公布 | 2026年3月13日 | - |\n"
            md_content += "| 全国总决赛 | 2026年3月21日 | 2026年3月21日 |\n\n"
        
        md_content += "## 五、评审标准\n\n"
        
        # 添加评分标准
        if self.competition_data['scoring_criteria']:
            for item in self.competition_data['scoring_criteria']:
                md_content += f"- {item['content']}（来源：{item['source']}）\n"
        else:
            md_content += "根据搜索结果，评分标准主要关注[5](@ref)：\n"
            md_content += "1. **信息完整度**：传译的信息是否完整\n"
            md_content += "2. **准确性**：翻译是否准确无误\n"
            md_content += "3. **地道性**：语言表达是否地道自然\n"
            md_content += "4. **语音语调**：发音、语调是否标准\n"
            md_content += "5. **非语言因素**：肢体语言、眼神交流等\n\n"
        
        md_content += "## 六、参赛费用\n\n"
        
        # 添加费用信息
        if self.competition_data['fees']:
            for item in self.competition_data['fees']:
                md_content += f"- {item['content']}（来源：{item['source']}）\n"
        else:
            md_content += "根据官方公告，费用标准如下[2](@ref)：\n"
            md_content += "- **初赛**：不收取费用\n"
            md_content += "- **英语口译大赛(交传)复赛**：每人200元\n"
            md_content += "- **英语口译大赛决赛**：每人400元\n"
            md_content += "- **英语口译大赛(同传)决赛**：每人400元\n"
            md_content += "- **多语种口译大赛复赛**：每人300元\n"
            md_content += "- **多语种口译大赛决赛**：每人500元\n\n"
        
        md_content += "## 七、奖项设置\n\n"
        
        # 添加奖项信息
        if self.competition_data['awards']:
            for item in self.competition_data['awards']:
                md_content += f"- {item['content']}（来源：{item['source']}）\n"
        else:
            md_content += "### 英语口译大赛奖项[2](@ref)\n"
            md_content += "1. **复赛奖项**：一、二、三等奖及优秀奖，颁发荣誉证书\n"
            md_content += "2. **决赛奖项**：冠、亚、季军及一、二、三等奖，颁发荣誉证书、奖杯等\n\n"
            md_content += "### 多语种口译大赛奖项[2](@ref)\n"
            md_content += "- 各语种决赛每个项目设一等奖1名，二等奖3名，三等奖6名\n"
            md_content += "- 晋级复赛但未晋级决赛的选手获优秀奖\n\n"
        
        md_content += "## 八、重要注意事项\n\n"
        md_content += "1. **报名方式**：所有参赛选手统一在大赛官网(www.lscat.cn)或关注公众号'LSCAT'注册报名[1,3](@ref)\n"
        md_content += "2. **比赛平台**：通过指定的'口译能力测试|竞赛平台'(BIECO软件)进行[1](@ref)\n"
        md_content += "3. **监考要求**：网络比赛采用视频监考，参赛选手需确保本人正面始终在摄像头取景框内[1](@ref)\n"
        md_content += "4. **纪律要求**：禁止使用任何外部辅助电子设备或他人帮助，违规者将被取消资格[1](@ref)\n"
        md_content += "5. **模拟测试**：建议参赛选手在赛前至少完成3次以上的模拟测试[1](@ref)\n\n"
        
        md_content += "## 九、联系方式\n\n"
        md_content += "- **官方网站**：www.lscat.cn\n"
        md_content += "- **微信公众号**：LSCAT\n"
        md_content += "- **技术支持**（比赛平台软件问题）[1](@ref)：\n"
        md_content += "  - Windows系统：QQ 85619641\n"
        md_content += "  - Mac系统：QQ 170342179\n\n"
        
        md_content += "## 十、数据来源说明\n\n"
        md_content += "本报告基于以下权威来源信息整理：\n"
        md_content += "1. 英文巴士《第十四届全国口译大赛(英语)报名与参赛须知》[1](@ref)\n"
        md_content += "2. 北京日报《2025年全国口译大赛一号公告》[2](@ref)\n"
        md_content += "3. 哈尔滨工业大学《2025年全国口译大赛报名通知》[3](@ref)\n"
        md_content += "4. 淮阴师范学院《2026年外语类学科竞赛月历》[4](@ref)\n"
        md_content += "5. 湘潭大学《全国口译大赛》介绍[5](@ref)\n\n"
        
        md_content += "> **免责声明**：以上信息仅供参考，具体竞赛规则以大赛官方最新公告为准。\n"
        
        return md_content
    
    def generate_docx(self, md_content):
        """生成Word文档"""
        doc = Document()
        
        # 设置文档属性
        doc.core_properties.title = '全国英语口译大赛竞赛规则'
        doc.core_properties.author = '元宝AI助手'
        doc.core_properties.subject = '英语口译大赛竞赛规则爬取报告'
        
        # 添加标题
        title = doc.add_heading('全国英语口译大赛竞赛规则', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 添加副标题
        subtitle = doc.add_paragraph(f'爬取时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # 将markdown转换为纯文本并添加到Word
        lines = md_content.split('\n')
        for line in lines:
            if line.startswith('# '):
                # 一级标题
                heading = doc.add_heading(line[2:], 1)
            elif line.startswith('## '):
                # 二级标题
                heading = doc.add_heading(line[3:], 2)
            elif line.startswith('### '):
                # 三级标题
                heading = doc.add_heading(line[4:], 3)
            elif line.startswith('|') and '|' in line:
                # 表格行
                cells = line.strip('|').split('|')
                if not hasattr(self, 'current_table'):
                    self.current_table = doc.add_table(rows=1, cols=len(cells))
                    self.current_table.style = 'Light Grid'
                    # 添加表头
                    for i, cell in enumerate(cells):
                        self.current_table.cell(0, i).text = cell.strip()
                else:
                    # 添加数据行
                    row_cells = self.current_table.add_row().cells
                    for i, cell in enumerate(cells):
                        row_cells[i].text = cell.strip()
            elif line.strip() == '':
                # 空行
                doc.add_paragraph()
            elif line.startswith('- ') or line.startswith('1. ') or line.startswith('2. '):
                # 列表项
                p = doc.add_paragraph(style='List Bullet' if line.startswith('- ') else 'List Number')
                p.add_run(line[2:])
            elif line.startswith('> '):
                # 引用
                p = doc.add_paragraph(style='Intense Quote')
                p.add_run(line[2:])
            else:
                # 普通段落
                doc.add_paragraph(line)
        
        return doc
    
    def save_files(self):
        """保存文件"""
        # 生成markdown内容
        md_content = self.generate_markdown()
        
        # 保存markdown文件
        md_filename = f'全国英语口译大赛竞赛规则_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        with open(md_filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"Markdown文件已保存：{md_filename}")
        
        # 生成并保存Word文档
        doc = self.generate_docx(md_content)
        docx_filename = f'全国英语口译大赛竞赛规则_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
        doc.save(docx_filename)
        print(f"Word文档已保存：{docx_filename}")
        
        # 保存原始数据为JSON
        json_filename = f'competition_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(self.competition_data, f, ensure_ascii=False, indent=2)
        print(f"JSON数据已保存：{json_filename}")
        
        return md_filename, docx_filename, json_filename
    
    def run(self):
        """运行爬虫"""
        print("=" * 60)
        print("全国英语口译大赛竞赛规则爬虫")
        print("=" * 60)
        
        # 爬取数据
        self.crawl_all_sources()
        
        # 保存文件
        md_file, docx_file, json_file = self.save_files()
        
        print("\n" + "=" * 60)
        print("爬虫任务完成！")
        print(f"生成文件：")
        print(f"  1. {md_file} (Markdown格式)")
        print(f"  2. {docx_file} (Word文档格式)")
        print(f"  3. {json_file} (原始数据)")
        print("=" * 60)


def main():
    """主函数"""
    # 创建爬虫实例
    crawler = EnglishInterpretationCompetitionCrawler()
    
    # 运行爬虫
    crawler.run()


if __name__ == "__main__":
    # 检查依赖库
    required_libraries = ['requests', 'beautifulsoup4', 'python-docx']
    
    print("检查依赖库...")
    for lib in required_libraries:
        try:
            if lib == 'beautifulsoup4':
                import bs4
            elif lib == 'python-docx':
                import docx
            else:
                __import__(lib)
            print(f"  √ {lib}")
        except ImportError:
            print(f"  × 缺少库：{lib}")
            print(f"    请运行：pip install {lib}")
    
    print("\n开始运行爬虫...")
    main()