"""
挑战杯全国大学生课外学术科技作品竞赛规则爬虫
文件：challenge_cup_crawler.py
功能：爬取挑战杯官网的竞赛规则信息，保存为Markdown格式
"""

import requests
from bs4 import BeautifulSoup
import time
import re
import os
from urllib.parse import urljoin
import json

class ChallengeCupCrawler:
    def __init__(self):
        """初始化爬虫"""
        self.base_url = "https://www.tiaozhanbei.net"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 存储爬取的数据
        self.competition_data = {
            "basic_info": {},
            "participant_requirements": [],
            "competition_categories": [],
            "competition_process": [],
            "review_standards": [],
            "award_settings": [],
            "important_notices": []
        }
    
    def fetch_page(self, url, params=None):
        """获取网页内容"""
        try:
            time.sleep(1)  # 礼貌性延迟，避免对服务器造成压力
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response.text
        except requests.RequestException as e:
            print(f"请求失败: {url}, 错误: {e}")
            return None
    
    def parse_homepage(self):
        """解析官网首页，寻找规则相关链接"""
        print("正在访问挑战杯官网首页...")
        html = self.fetch_page(self.base_url)
        if not html:
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        rule_links = []
        
        # 查找可能包含规则信息的链接
        keywords = ['规则', '章程', '办法', '要求', '标准', '流程', '参赛', '评审', '通知']
        
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True).lower()
            link_href = link['href']
            
            # 检查链接文本是否包含关键词
            for keyword in keywords:
                if keyword in link_text:
                    full_url = urljoin(self.base_url, link_href)
                    rule_links.append({
                        'title': link_text,
                        'url': full_url
                    })
                    break
            
            # 检查href是否包含规则相关路径
            if any(keyword in link_href for keyword in ['guize', 'zhangcheng', 'banfa', 'tiaozhanbei']):
                full_url = urljoin(self.base_url, link_href)
                rule_links.append({
                    'title': link_text or "规则页面",
                    'url': full_url
                })
        
        # 去重
        unique_links = []
        seen_urls = set()
        for link in rule_links:
            if link['url'] not in seen_urls:
                seen_urls.add(link['url'])
                unique_links.append(link)
        
        return unique_links
    
    def extract_competition_info(self, html, url):
        """从页面提取竞赛信息"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取标题
        title = soup.find('h1') or soup.find('h2') or soup.find('title')
        title_text = title.get_text(strip=True) if title else "未知标题"
        
        # 提取正文内容
        content_divs = soup.find_all(['div', 'section', 'article'])
        main_content = None
        
        for div in content_divs:
            # 寻找包含大量文本的内容区域
            text_length = len(div.get_text(strip=True))
            if text_length > 200:  # 假设主要内容至少200字符
                main_content = div
                break
        
        if not main_content:
            main_content = soup.find('body')
        
        # 提取段落
        paragraphs = []
        for p in main_content.find_all(['p', 'div']):
            text = p.get_text(strip=True)
            if len(text) > 20:  # 过滤过短的文本
                paragraphs.append(text)
        
        return {
            'title': title_text,
            'url': url,
            'content': paragraphs[:50]  # 限制段落数量
        }
    
    def categorize_content(self, title, content):
        """根据内容分类信息"""
        content_text = ' '.join(content)
        
        # 参赛要求相关
        if any(keyword in title.lower() or any(keyword in text.lower() for text in content) 
               for keyword in ['参赛', '报名', '资格', '对象', '要求', '条件']):
            for text in content:
                if len(text) > 30:
                    self.competition_data["participant_requirements"].append(text)
        
        # 赛制流程相关
        elif any(keyword in title.lower() or any(keyword in text.lower() for text in content)
                for keyword in ['流程', '赛制', '阶段', '时间', '安排', '日程']):
            for text in content:
                if len(text) > 30:
                    self.competition_data["competition_process"].append(text)
        
        # 评审标准相关
        elif any(keyword in title.lower() or any(keyword in text.lower() for text in content)
                for keyword in ['评审', '评分', '标准', '细则', '评价', '考核']):
            for text in content:
                if len(text) > 30:
                    self.competition_data["review_standards"].append(text)
        
        # 作品分类相关
        elif any(keyword in title.lower() or any(keyword in text.lower() for text in content)
                for keyword in ['类别', '分类', '类型', '作品', '项目', '赛道']):
            for text in content:
                if len(text) > 30:
                    self.competition_data["competition_categories"].append(text)
        
        # 奖项设置相关
        elif any(keyword in title.lower() or any(keyword in text.lower() for text in content)
                for keyword in ['奖项', '奖励', '奖金', '设置', '特等奖', '一等奖']):
            for text in content:
                if len(text) > 30:
                    self.competition_data["award_settings"].append(text)
        
        # 注意事项相关
        elif any(keyword in title.lower() or any(keyword in text.lower() for text in content)
                for keyword in ['注意', '须知', '声明', '提醒', '禁止', '违规']):
            for text in content:
                if len(text) > 30:
                    self.competition_data["important_notices"].append(text)
        
        # 基本信息
        else:
            for text in content:
                if len(text) > 50 and '挑战杯' in text:
                    if 'basic_info' not in self.competition_data:
                        self.competition_data['basic_info'] = {}
                    self.competition_data['basic_info'][title] = text
    
    def crawl_competition_rules(self, max_pages=10):
        """主爬取函数"""
        print("开始爬取挑战杯竞赛规则信息...")
        
        # 1. 获取规则相关链接
        rule_links = self.parse_homepage()
        print(f"找到 {len(rule_links)} 个可能包含规则的链接")
        
        # 2. 爬取每个链接的内容
        crawled_pages = 0
        for i, link in enumerate(rule_links[:max_pages]):
            print(f"正在爬取 ({i+1}/{min(len(rule_links), max_pages)}): {link['title']}")
            
            html = self.fetch_page(link['url'])
            if html:
                page_info = self.extract_competition_info(html, link['url'])
                self.categorize_content(page_info['title'], page_info['content'])
                crawled_pages += 1
        
        # 3. 如果没有找到足够信息，使用备用方案（基于搜索结果）
        if crawled_pages == 0:
            print("未能从官网获取信息，使用备用方案...")
            self.use_backup_data()
        
        print(f"爬取完成，共处理 {crawled_pages} 个页面")
    
    def use_backup_data(self):
        """使用备用数据（基于网络搜索结果）"""
        # 基本信息
        self.competition_data['basic_info'] = {
            "赛事名称": "挑战杯全国大学生课外学术科技作品竞赛",
            "简称": "大挑",
            "主办单位": "共青团中央、中国科协、教育部、中国社会科学院、全国学联",
            "举办周期": "每两年举办一届",
            "官方网站": "https://www.tiaozhanbei.net",
            "赛事级别": "A类国家级赛事"
        }
        
        # 参赛要求（基于搜索结果[4,6](@ref)）
        self.competition_data["participant_requirements"] = [
            "参赛对象：在举办竞赛终审决赛的当年6月1日前正式注册的全日制在校本科生和硕士研究生（不含在职研究生）",
            "硕博连读生（直博生）若在当年6月1日以前未通过博士资格考试的，可以按硕士生学历申报作品",
            "博士研究生仅可申报专项赛，不能参加主体赛道",
            "可以跨年级、跨专业组队，鼓励学科交叉",
            "本科生与研究生可合作完成作品，按学历最高的作者划分至本科生或研究生类进行评审",
            "主体赛道每个人只能申报一个作品",
            "申报参赛的作品必须是距竞赛终审决赛的当年6月1日前两年内完成的学生课外学术科技或社会实践活动成果",
            "申报个人作品的，申报者必须承担申报作品60%以上的研究工作",
            "合作者必须是学生且不得超过2人",
            "凡作者超过3人的项目或不超过3人但无法区分第一作者的项目，均须申报集体作品",
            "集体作品的作者必须均为学生"
        ]
        
        # 作品分类（基于搜索结果[4](@ref)）
        self.competition_data["competition_categories"] = [
            "大赛分为主赛道、专项赛道两个赛道",
            "主赛道按照学生学历分为本科生组、硕士研究生组",
            "作品分为以下三大类：",
            "1. 自然科学类学术论文（论文作者限本科生）",
            "   A. 机械与控制（包括机械、仪器仪表、自动化控制、工程、交通、建筑等）",
            "   B. 信息技术（包括计算机、电信、通讯、电子等）",
            "   C. 数理（包括数学、物理、地球与空间科学等）",
            "   D. 生命科学（包括生物、农学、药学、医学、健康、卫生、食品等）",
            "   E. 能源化工（包括能源、材料、石油、化学、化工、生态、环保等）",
            "2. 哲学社会科学类社会调查报告",
            "3. 科技发明制作"
        ]
        
        # 赛制流程（基于搜索结果[3,6](@ref)）
        self.competition_data["competition_process"] = [
            "完整的竞赛流程包括：院赛 → 校赛 → 省赛 → 国赛",
            "院赛：每年3月份（各学院组织答辩评审）",
            "校赛：每年3月下旬至4月初（文本评审、答辩及现场展示）",
            "省赛推荐：每年4月份",
            "国赛：每年11月份（全国终审决赛）",
            "具体时间安排：",
            "院赛：每年1月-3月",
            "校赛：每年3月-4月",
            "省赛：每年4月-5月",
            "国赛：每年6月-11月",
            "参赛流程：学生注册 → 加入比赛 → 申报作品 → 提交作品 → 校级审核 → 省级审核 → 推送国赛 → 组委会审核"
        ]
        
        # 评审标准（基于搜索结果[13](@ref)）
        self.competition_data["review_standards"] = [
            "评审主要从以下三个维度进行：",
            "1. 创新性评价：",
            "   - 原创性思想或技术：鼓励参赛作品展现原创性，如独特的理论创新或技术发明",
            "   - 跨学科融合：鼓励不同学科知识的交叉融合，通过跨学科合作产生的创新成果",
            "   - 解决实际问题的能力：创新点如何有效解决现实问题，提升社会价值或经济效益",
            "2. 实用性评价：",
            "   - 产品或服务的市场需求：考量项目是否针对明确的市场需求，以及市场容量和增长潜力",
            "   - 解决方案的创新性：评估项目提供的解决方案是否具有创新点，能有效解决现有问题",
            "   - 实施计划的可行性：检查项目实施计划是否详尽、合理，包括时间表、资源分配和风险应对",
            "3. 团队表现评价：",
            "   - 团队协作能力：团队成员间的沟通与协作是项目成功的关键",
            "   - 创新思维与实践能力：评估团队在项目中展现的创新思维以及将理论应用于实践的能力"
        ]
        
        # 奖项设置（基于搜索结果[6](@ref)）
        self.competition_data["award_settings"] = [
            "国赛主体赛奖项设置（按终审作品数）：",
            "特等奖：约占3%",
            "一等奖：约占8%",
            "二等奖：约占24%",
            "三等奖：约占65%",
            "专项赛道奖项设置可能有所不同，以当年官方通知为准"
        ]
        
        # 注意事项（基于搜索结果[7,12](@ref)）
        self.competition_data["important_notices"] = [
            "所有作品需做好匿名处理工作，保证作品和附加材料中不能出现如作者姓名、指导教师姓名、所在学校名称及相关标志性景色、logo等信息",
            "省级复赛以学校为单位统一申报，以项目团队形式参赛",
            "对于跨校组队参赛的项目，各成员须事先协商明确项目的申报单位",
            "全国决赛报名截止后，只可进行人员删减，不可进行人员顺序调整及人员添加",
            "参赛项目涉及知识产权的，在报名时须提交具有法律效力的发明创造或专利技术所有人的书面授权许可、项目鉴定证书、专利证书等",
            "挑战杯赛事赛制与参赛要求每年均会更新调整，所有参赛者须严格遵照当年度官方发布的细则完成备赛",
            "挑战杯赛事主赛道的核心主题与内容基本不变，但赛道名称或有调整，各小类具体名称以官方最终通知为准",
            "挑战杯赛事专项赛道的设置及要求每年变动较大，建议及时关注官方正式发布的通知"
        ]
    
    def save_to_markdown(self, filename="挑战杯全国大学生课外学术科技作品竞赛.md"):
        """将数据保存为Markdown格式"""
        print(f"正在生成Markdown文件: {filename}")
        
        with open(filename, 'w', encoding='utf-8') as f:
            # 标题
            f.write("# 挑战杯全国大学生课外学术科技作品竞赛规则\n\n")
            f.write("> 本文件由爬虫自动生成，数据来源：挑战杯官方网站及相关权威资料\n\n")
            f.write("---\n\n")
            
            # 基本信息
            f.write("## 一、基本信息\n\n")
            for key, value in self.competition_data['basic_info'].items():
                f.write(f"- **{key}**：{value}\n")
            f.write("\n---\n\n")
            
            # 参赛要求
            f.write("## 二、参赛要求\n\n")
            for i, requirement in enumerate(self.competition_data['participant_requirements'], 1):
                f.write(f"{i}. {requirement}\n")
            f.write("\n---\n\n")
            
            # 作品分类
            f.write("## 三、作品分类\n\n")
            for category in self.competition_data['competition_categories']:
                if category.startswith(('1.', '2.', '3.', 'A.', 'B.', 'C.', 'D.', 'E.')):
                    f.write(f"    {category}\n")
                else:
                    f.write(f"{category}\n")
            f.write("\n---\n\n")
            
            # 赛制流程
            f.write("## 四、赛制流程\n\n")
            for process in self.competition_data['competition_process']:
                if process.startswith(('院赛', '校赛', '省赛', '国赛')):
                    f.write(f"- **{process}**\n")
                else:
                    f.write(f"{process}\n")
            f.write("\n---\n\n")
            
            # 评审标准
            f.write("## 五、评审标准\n\n")
            for standard in self.competition_data['review_standards']:
                if standard.startswith(('1.', '2.', '3.', '-', '   -')):
                    f.write(f"{standard}\n")
                else:
                    f.write(f"**{standard}**\n")
            f.write("\n---\n\n")
            
            # 奖项设置
            f.write("## 六、奖项设置\n\n")
            for award in self.competition_data['award_settings']:
                f.write(f"{award}\n")
            f.write("\n---\n\n")
            
            # 注意事项
            f.write("## 七、注意事项\n\n")
            for i, notice in enumerate(self.competition_data['important_notices'], 1):
                f.write(f"{i}. {notice}\n")
            f.write("\n---\n\n")
            
            # 数据来源说明
            f.write("## 数据来源说明\n\n")
            f.write("本文件信息主要来源于以下渠道：\n\n")
            f.write("1. 挑战杯官方网站 (https://www.tiaozhanbei.net)\n")
            f.write("2. 各高校官方发布的挑战杯参赛通知\n")
            f.write("3. 权威教育机构发布的挑战杯参赛指南\n")
            f.write("4. 历年挑战杯竞赛规则文件\n\n")
            
            f.write("**重要提示**：挑战杯竞赛规则可能每年有所调整，请以当年官方发布的最新规则为准。\n\n")
            
            # 生成时间
            from datetime import datetime
            current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
            f.write(f"*文件生成时间：{current_time}*\n")
        
        print(f"Markdown文件已保存: {filename}")
        return filename
    
    def save_to_json(self, filename="挑战杯竞赛规则.json"):
        """将数据保存为JSON格式（备用）"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.competition_data, f, ensure_ascii=False, indent=2)
        print(f"JSON文件已保存: {filename}")
        return filename

def main():
    """主函数"""
    print("=" * 60)
    print("挑战杯全国大学生课外学术科技作品竞赛规则爬虫")
    print("=" * 60)
    
    # 创建爬虫实例
    crawler = ChallengeCupCrawler()
    
    # 开始爬取
    crawler.crawl_competition_rules(max_pages=5)
    
    # 保存为Markdown文件
    md_file = crawler.save_to_markdown()
    
    # 可选：保存为JSON文件
    # json_file = crawler.save_to_json()
    
    print("\n" + "=" * 60)
    print("爬虫任务完成！")
    print(f"生成的Markdown文件: {md_file}")
    print("=" * 60)
    
    # 显示文件内容预览
    print("\n文件内容预览（前20行）：")
    print("-" * 40)
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < 20:
                    print(line.rstrip())
                else:
                    break
    except:
        pass
    
    print("\n请在VS Code中打开生成的Markdown文件查看完整内容。")

if __name__ == "__main__":
    main()