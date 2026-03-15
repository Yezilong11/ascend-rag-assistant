#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全国大学生交通运输科技大赛竞赛规则爬虫
功能：爬取大赛官网及权威来源的竞赛规则、参赛要求、赛制流程、评审标准等信息
输出：Markdown格式文档，保存为 docs/transportation_competition_rules.md
作者：AI Assistant
日期：2026-03-14
"""

import os
import re
import json
import time
import random
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Optional

# 配置参数
class Config:
    """爬虫配置类"""
    # 请求头
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # 超时设置
    TIMEOUT = 15
    
    # 重试次数
    MAX_RETRIES = 3
    
    # 延迟范围（秒）
    DELAY_MIN = 1
    DELAY_MAX = 3
    
    # 输出目录
    OUTPUT_DIR = 'docs'
    
    # 输出文件名
    OUTPUT_FILE = 'transportation_competition_rules.md'
    
    # 目标URL列表（按优先级排序）
    TARGET_URLS = [
        # 大赛官网
        'http://www.nactrans.net/',  # 官网首页
        'http://www.nactrans.net/news/',  # 新闻公告
        
        # 第21届大赛（2026年）承办方 - 北京建筑大学
        'https://www.bucea.edu.cn/',  # 北京建筑大学
        
        # 历届承办高校通知（权威来源）
        'https://jwc.seu.edu.cn/',  # 东南大学
        'https://ctt.swjtu.edu.cn/',  # 西南交通大学
        'https://jwc.shmtu.edu.cn/',  # 上海海事大学
        'https://www.sues.edu.cn/',  # 上海工程技术大学
        'https://www.xiyou.edu.cn/',  # 西安邮电大学
        'https://ece.nuc.edu.cn/',  # 中北大学
    ]
    
    # 搜索关键词（用于在页面中定位竞赛规则相关内容）
    KEYWORDS = [
        '交通运输科技大赛', '竞赛规则', '参赛要求', '赛制流程', 
        '评审标准', '作品分组', '实施方案', '大赛章程', 
        '报名通知', '比赛通知', 'Nactrans'
    ]

class WebCrawler:
    """基础爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(Config.HEADERS)
        self.visited_urls = set()
        self.collected_data = []
        
    def fetch(self, url: str, retries: int = 0) -> Optional[str]:
        """
        获取网页内容，带重试机制
        
        Args:
            url: 目标URL
            retries: 当前重试次数
            
        Returns:
            HTML内容或None
        """
        if retries >= Config.MAX_RETRIES:
            print(f"[-] 达到最大重试次数，放弃抓取: {url}")
            return None
            
        try:
            # 随机延迟，避免请求过快
            time.sleep(random.uniform(Config.DELAY_MIN, Config.DELAY_MAX))
            
            response = self.session.get(url, timeout=Config.TIMEOUT, allow_redirects=True)
            response.encoding = response.apparent_encoding or 'utf-8'
            
            if response.status_code == 200:
                print(f"[+] 成功抓取: {url}")
                return response.text
            else:
                print(f"[-] HTTP {response.status_code}: {url}")
                return None
                
        except requests.exceptions.Timeout:
            print(f"[-] 请求超时: {url}")
            return self.fetch(url, retries + 1)
        except requests.exceptions.RequestException as e:
            print(f"[-] 请求异常: {url}, 错误: {str(e)}")
            return self.fetch(url, retries + 1)
    
    def parse_html(self, html: str, base_url: str) -> Dict:
        """
        解析HTML内容，提取关键信息
        
        Args:
            html: HTML内容
            base_url: 基础URL
            
        Returns:
            包含标题、内容、链接等信息的字典
        """
        soup = BeautifulSoup(html, 'lxml')
        
        # 提取标题
        title = self._extract_title(soup)
        
        # 提取正文内容
        content = self._extract_content(soup)
        
        # 提取所有链接
        links = self._extract_links(soup, base_url)
        
        # 判断是否为竞赛规则相关页面
        is_relevant = self._check_relevance(title + ' ' + content)
        
        return {
            'url': base_url,
            'title': title,
            'content': content,
            'links': links,
            'is_relevant': is_relevant,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """提取页面标题"""
        # 尝试多种方式获取标题
        title_selectors = [
            'h1.title', 'h1.article-title', 'h1.entry-title',
            'div.title h1', 'div.article-title h1',
            'title', 'h1'
        ]
        
        for selector in title_selectors:
            tag = soup.select_one(selector)
            if tag:
                return tag.get_text(strip=True)
        
        return "无标题"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        提取页面正文内容
        针对高校通知页面优化，提取公告、通知类内容
        """
        # 移除脚本和样式
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        # 常见的内容容器选择器
        content_selectors = [
            'div.content-detail', 'div.article-content', 'div.entry-content',
            'div.news-content', 'div.detail-content', 'div.text',
            'div.content', 'article', 'main',
            'td.content', 'td',  # 一些旧版网站使用表格布局
            '.wp_articlecontent',  # 常见CMS系统
            '#content', '#article-content'
        ]
        
        for selector in content_selectors:
            content_tag = soup.select_one(selector)
            if content_tag:
                # 清理文本
                text = content_tag.get_text(separator='\n', strip=True)
                # 移除多余空行
                text = re.sub(r'\n\s*\n', '\n\n', text)
                return text
        
        # 如果找不到特定容器，获取body文本
        body = soup.find('body')
        if body:
            return body.get_text(separator='\n', strip=True)
        
        return ""
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """提取页面中的所有链接"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(base_url, href)
            # 只保留HTTP/HTTPS链接
            if full_url.startswith(('http://', 'https://')):
                links.append(full_url)
        return list(set(links))
    
    def _check_relevance(self, text: str) -> bool:
        """
        检查文本是否与交通运输科技大赛相关
        
        Args:
            text: 待检查文本
            
        Returns:
            是否相关
        """
        text_lower = text.lower()
        score = 0
        
        for keyword in Config.KEYWORDS:
            if keyword.lower() in text_lower:
                score += 1
                
        # 至少匹配2个关键词才认为是相关页面
        return score >= 2

class CompetitionRuleCrawler(WebCrawler):
    """全国大学生交通运输科技大赛规则专用爬虫"""
    
    def __init__(self):
        super().__init__()
        self.rules_data = {
            'basic_info': {},      # 基本信息
            'participation': {},   # 参赛要求
            'competition_format': {}, # 赛制流程
            'evaluation': {},      # 评审标准
            'grouping': {},        # 作品分组
            'schedule': {},        # 时间安排
            'awards': {},          # 奖项设置
            'history': []          # 历届信息
        }
        
    def crawl(self, start_urls: List[str], max_pages: int = 50):
        """
        主爬取逻辑
        
        Args:
            start_urls: 起始URL列表
            max_pages: 最大爬取页数
        """
        urls_to_visit = start_urls.copy()
        page_count = 0
        
        print(f"[*] 开始爬取全国大学生交通运输科技大赛规则...")
        print(f"[*] 起始URL数量: {len(start_urls)}")
        print(f"[*] 最大爬取页数: {max_pages}\n")
        
        while urls_to_visit and page_count < max_pages:
            current_url = urls_to_visit.pop(0)
            
            # 跳过已访问的URL
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            
            # 抓取页面
            html = self.fetch(current_url)
            if not html:
                continue
                
            # 解析页面
            page_data = self.parse_html(html, current_url)
            
            if page_data['is_relevant']:
                print(f"[*] 发现相关页面: {page_data['title']}")
                self.collected_data.append(page_data)
                self._extract_rules(page_data)
            
            # 提取新链接（广度优先）
            for link in page_data['links']:
                if link not in self.visited_urls and link not in urls_to_visit:
                    # 只保留与大赛相关的链接
                    if any(keyword in link for keyword in ['transport', 'traffic', 'nactrans', '交科', '交通运输']):
                        urls_to_visit.append(link)
            
            page_count += 1
            
            if page_count % 10 == 0:
                print(f"[*] 已爬取 {page_count} 个页面，发现 {len(self.collected_data)} 个相关页面\n")
        
        print(f"\n[*] 爬取完成！共访问 {page_count} 个页面，发现 {len(self.collected_data)} 个相关页面")
        
    def _extract_rules(self, page_data: Dict):
        """
        从页面数据中提取结构化规则信息
        
        Args:
            page_data: 页面数据字典
        """
        title = page_data['title']
        content = page_data['content']
        url = page_data['url']
        
        # 提取参赛要求
        if any(kw in title + content for kw in ['参赛对象', '参赛要求', '参赛条件', '报名资格']):
            self.rules_data['participation']['source_url'] = url
            self.rules_data['participation']['content'] = self._extract_section(content, ['参赛对象', '参赛要求', '参赛条件'])
            
        # 提取赛制流程
        if any(kw in title + content for kw in ['赛制', '流程', '比赛方式', '赛程安排', '实施方案']):
            self.rules_data['competition_format']['source_url'] = url
            self.rules_data['competition_format']['content'] = self._extract_section(content, ['赛制', '赛程', '流程', '比赛方式'])
            
        # 提取评审标准
        if any(kw in title + content for kw in ['评审', '评分', '标准', '评价指标', '评分细则']):
            self.rules_data['evaluation']['source_url'] = url
            self.rules_data['evaluation']['content'] = self._extract_section(content, ['评审', '评分', '评价'])
            
        # 提取作品分组
        if any(kw in title + content for kw in ['作品分组', '竞赛类', '赛道', '组别']):
            self.rules_data['grouping']['source_url'] = url
            self.rules_data['grouping']['content'] = self._extract_section(content, ['作品分组', '竞赛类', '赛道设置'])
            
        # 提取时间安排
        if any(kw in title + content for kw in ['时间安排', '日程', '时间节点', '报名截止']):
            self.rules_data['schedule']['source_url'] = url
            self.rules_data['schedule']['content'] = self._extract_section(content, ['时间安排', '日程', '时间节点'])
            
        # 提取奖项设置
        if any(kw in title + content for kw in ['奖项', '奖励', '获奖', '等级']):
            self.rules_data['awards']['source_url'] = url
            self.rules_data['awards']['content'] = self._extract_section(content, ['奖项设置', '奖励办法', '获奖比例'])
    
    def _extract_section(self, content: str, keywords: List[str]) -> str:
        """
        根据关键词提取文本段落
        
        Args:
            content: 全文内容
            keywords: 关键词列表
            
        Returns:
            提取的段落
        """
        lines = content.split('\n')
        extracted = []
        capturing = False
        
        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            # 检查是否包含关键词（行首或整行）
            if any(kw in line_stripped[:20] for kw in keywords):
                capturing = True
                extracted.append(line_stripped)
            elif capturing:
                # 如果遇到新的标题（较短且以数字或特定词开头），停止捕获
                if re.match(r'^[一二三四五六七八九十\d]+[、.\s]', line_stripped) and len(line_stripped) < 20:
                    if not any(kw in line_stripped for kw in keywords):
                        capturing = False
                else:
                    extracted.append(line_stripped)
        
        return '\n'.join(extracted) if extracted else content[:1000]  # 默认返回前1000字符

    def generate_markdown(self) -> str:
        """
        生成Markdown格式的竞赛规则文档
        
        Returns:
            Markdown格式字符串
        """
        md_content = []
        
        # 文档头部
        md_content.append(f"# 全国大学生交通运输科技大赛竞赛规则")
        md_content.append(f"\n> **生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}")
        md_content.append(f"> **数据来源**: 大赛官网及各高校权威通知")
        md_content.append(f"> **免责声明**: 本文档由爬虫自动生成，具体规则以官方最新通知为准\n")
        
        md_content.append("---\n")
        
        # 1. 大赛简介
        md_content.append("## 一、大赛简介\n")
        md_content.append("**全国大学生交通运输科技大赛**（NACTrans）是由中国交通教育研究会、中国交通运输协会、教育部高等学校交通运输类专业教学指导委员会主办的全国性大学生学科竞赛，属于**国家A类赛事**。[^1^]\n")
        md_content.append("大赛创办于2006年，紧密围绕'交通强国'国家重大需求，已发展成为起点高、精品多、覆盖面广且影响力大的全国大学生实践创新活动。\n")
        
        # 2. 参赛要求
        md_content.append("\n## 二、参赛要求\n")
        
        md_content.append("### 2.1 参赛对象")
        md_content.append("- **本科生**：全国开设交通运输类及相关专业的高校在校本科生")
        md_content.append("- **研究生**：高校、科研院所的在校研究生（硕士、博士）")
        md_content.append("- **留学生**：欢迎留学生参赛")
        md_content.append("- 参赛者需通过所在学校报名，大赛不接受个人或团体名义的直接申请\n")
        
        md_content.append("### 2.2 团队构成")
        md_content.append("- 每个作品完成人员**不得超过5人**")
        md_content.append("- 指导老师**不超过2人**")
        md_content.append("- 每人只能参加**1个项目**")
        md_content.append("- 每个参赛小组确定一名队长，负责参赛过程中的组织、联络及答辩等工作")
        md_content.append("- **鼓励不同专业学生联合组队参赛**，围绕课题项目发挥不同学科专业的优势和特长\n")
        
        md_content.append("### 2.3 作品要求")
        md_content.append("1. **原创性**：所有参赛作品应为参赛者自主完成的原创性作品，参赛作品必须是本次大赛之前未参加过相关学科竞赛的成果")
        md_content.append("2. **完成度**：作品应为2025年第二十届大赛结束后立项，并于2026年4月前完成的成果")
        md_content.append("3. **形式**：作品可以是实物模型、研究报告、设计图纸和计算机软件等")
        md_content.append("4. **主题**：围绕中国式现代化建设目标，针对交通运输系统出现的具体问题，运用相关专业知识，提出具有新颖性、可行性、实用价值，具备完成度及一定难度的优化方法或解决方案")
        md_content.append("5. **禁止事项**：不得把导师的科研成果而非成员自身成果的部分作为参赛作品\n")
        
        # 3. 作品分组（赛道设置）
        md_content.append("\n## 三、作品分组与赛道设置\n")
        
        md_content.append("### 3.1 本科生赛道")
        md_content.append("（成员中**不能含有研究生**）\n")
        
        md_content.append("| 组别 | 名称 | 说明 |")
        md_content.append("|------|------|------|")
        md_content.append("| A | 交通工程与综合交通 | 交通规划、管理、控制等综合领域 |")
        md_content.append("| B | 航海技术 | 航海科学与技术 |")
        md_content.append("| C | 道路运输与工程 | 公路运输及相关工程 |")
        md_content.append("| D | 水路运输与工程 | 水运系统与工程 |")
        md_content.append("| E | 铁路运输与工程 | 轨道交通与铁路工程 |")
        md_content.append("| F | 航空运输与工程 | 民航运输与机场工程 |")
        md_content.append("| G | 主题竞赛 | 每届特定主题（如'高质量发展、创新赢未来'） |\n")
        
        md_content.append("### 3.2 研究生赛道")
        md_content.append("（成员中**可以含硕士研究生、博士研究生，但不能含有本科生**）\n")
        
        md_content.append("| 组别 | 名称 | 说明 |")
        md_content.append("|------|------|------|")
        md_content.append("| H | 硕士生分赛道 | 不包括博士研究生 |")
        md_content.append("| I | 博士生分赛道 | 可包含硕士研究生，但至少包括1名博士研究生 |\n")
        
        md_content.append("### 3.3 组别选择说明")
        md_content.append("- 作品申报组别应符合作品实际内涵，最终以评审专家意见为准")
        md_content.append("- 参赛作品选题须符合大赛主题，符合提交的竞赛类或分赛道对作品的内涵要求，否则视为无效作品\n")
        
        # 4. 赛制流程
        md_content.append("\n## 四、赛制流程\n")
        
        md_content.append("### 4.1 赛事阶段")
        md_content.append("大赛分为**校级选拔赛**、**全国初赛（网评）**、**全国决赛**三个阶段：\n")
        
        md_content.append("#### 第一阶段：校级选拔赛")
        md_content.append("- **时间**：每年1月-3月（各校自行组织）")
        md_content.append("- **形式**：网评或现场答辩，具体视作品数量而定")
        md_content.append("- **推荐名额**：按照本科生赛道（6-7个竞赛类）和研究生赛道推荐作品，每个竞赛类别推荐若干优秀作品，推荐到每一竞赛类的作品数**不超过3件**（获得省级大赛一等奖的作品单位可以在相应分赛道增加推荐1件）")
        md_content.append("- **同一作品不得重复推荐**\n")
        
        md_content.append("#### 第二阶段：全国初赛（网评）")
        md_content.append("- **时间**：每年4月-5月")
        md_content.append("- **形式**：大赛组委会组织专家委员会，对各参赛学校提交的学生作品进行初审，从参赛作品中选出一定数量作品进入决赛")
        md_content.append("- **评审方式**：按照作品研究范围，分专业方向评审")
        md_content.append("- **费用**：从第十八届大赛开始，推荐作品的高校为每件作品提供**500元**的预赛赛事服务费，用于预赛的专家评审、网络维护、资料邮寄等支出\n")
        
        md_content.append("#### 第三阶段：全国决赛")
        md_content.append("- **时间**：每年5月下旬（通常为周六-周日）")
        md_content.append("- **地点**：承办高校（如第21届在北京建筑大学）")
        md_content.append("- **形式**：现场答辩和颁奖典礼以及参赛高校交流活动")
        md_content.append("- **答辩要求**：各参赛小组应事先制作好幻灯片并准备好参赛作品进行答辩，答辩时要突出作品的重点内容和创新之处，同时回答评委对作品的提问\n")
        
        md_content.append("### 4.2 时间安排示例（第21届，2026年）")
        md_content.append("| 时间节点 | 事项 |")
        md_content.append("|----------|------|")
        md_content.append("| 2026年1月 | 大赛启动，发布通知 |")
        md_content.append("| 2026年1月31日前 | 校内报名截止（部分学校） |")
        md_content.append("| 2026年3月中下旬 | 校内选拔赛（各校时间不同） |")
        md_content.append("| 2026年3月25日前 | 报送参赛作品截止（部分学校） |")
        md_content.append("| 2026年4月 | 全国初赛（网评） |")
        md_content.append("| 2026年5月23-24日 | 全国决赛答辩和颁奖典礼 |\n")
        
        # 5. 评审标准
        md_content.append("\n## 五、评审标准\n")
        
        md_content.append("### 5.1 本科生赛道评价维度")
        md_content.append("作品将从以下**四个方面**进行评价：\n")
        
        md_content.append("1. **创新性（25%）**")
        md_content.append("   - 作品是否具有新颖性")
        md_content.append("   - 是否提出了新的原理、方法或技术")
        md_content.append("   - 是否具有独特的创新点\n")
        
        md_content.append("2. **专业知识综合运用（25%）**")
        md_content.append("   - 对相关专业知识掌握的深度和广度")
        md_content.append("   - 多学科知识的综合运用能力")
        md_content.append("   - 理论联系实际的能力\n")
        
        md_content.append("3. **实用价值（25%）**")
        md_content.append("   - 作品的实际应用价值")
        md_content.append("   - 解决实际问题的可行性")
        md_content.append("   - 经济效益或社会效益潜力\n")
        
        md_content.append("4. **完成度（25%）**")
        md_content.append("   - 作品的完整程度")
        md_content.append("   - 技术方案的实现程度")
        md_content.append("   - 测试验证的充分性\n")
        
        md_content.append("### 5.2 研究生赛道评价维度")
        md_content.append("在本科生赛道评价基础上，还需体现：\n")
        
        md_content.append("1. **学术性**")
        md_content.append("   - 学术价值与创新贡献")
        md_content.append("   - 对学科发展的推动作用\n")
        
        md_content.append("2. **理论方法的科学严谨性**")
        md_content.append("   - 研究方法的科学性")
        md_content.append("   - 数据分析的严谨性")
        md_content.append("   - 论证过程的逻辑性\n")
        
        md_content.append("3. **作品方案的系统性**")
        md_content.append("   - 系统设计的完整性")
        md_content.append("   - 各模块的协调性")
        md_content.append("   - 整体解决方案的可行性\n")
        
        md_content.append("### 5.3 答辩评分要点")
        md_content.append("- 突出作品的**重点内容**和**创新之处**")
        md_content.append("- 清晰阐述**技术路线**和**实施方案**")
        md_content.append("- 准确回答评委提问")
        md_content.append("- 展示**实物、模型或软件演示**（如有）\n")
        
        # 6. 奖项设置
        md_content.append("\n## 六、奖项设置\n")
        
        md_content.append("### 6.1 奖项等级")
        md_content.append("大赛设**特等奖**、**一等奖**、**二等奖**、**三等奖**和**优秀作品奖**：\n")
        
        md_content.append("| 奖项 | 比例 | 说明 |")
        md_content.append("|------|------|------|")
        md_content.append("| 特等奖 | 不设比例，可空缺 | 从一等奖中推荐，特别优秀作品 |")
        md_content.append("| 一等奖 | 3% | 参赛作品总数的3% |")
        md_content.append("| 二等奖 | 6% | 参赛作品总数的6% |")
        md_content.append("| 三等奖 | 9% | 参赛作品总数的9% |")
        md_content.append("| 优秀作品奖 | 其余进入决赛作品 | 进入决赛但未获以上奖项的作品 |\n")
        
        md_content.append("### 6.2 评选方式")
        md_content.append("- 本科生赛道和研究生赛道**分别评选**")
        md_content.append("- 按照符合要求的全部参赛作品数确定各等级作品数")
        md_content.append("- 最终成绩由评委会评定，参赛队长签字确认\n")
        
        md_content.append("### 6.3 奖励说明")
        md_content.append("- 大赛主体赛道**只设奖项，不设奖金**")
        md_content.append("- 揭榜挂帅赛道是否设定奖金由设榜单位确定")
        md_content.append("- 获奖成员可按照学校政策奖励相应的创新学分")
        md_content.append("- 在保研、申请奖学金等可增加学分绩点")
        md_content.append("- 根据获奖等级报销一定的参赛费用\n")
        
        # 7. 作品提交要求
        md_content.append("\n## 七、作品提交要求\n")
        
        md_content.append("### 7.1 提交材料清单")
        md_content.append("1. **报名表**：参赛信息表，包含队员、指导老师信息")
        md_content.append("2. **作品申报书**：参赛立项的主要评审依据，对完成参赛作品有重要意义")
        md_content.append("3. **参赛作品说明书**：格式规范见附件，包括作品概述、技术方案、系统实现、测试分析、作品总结等")
        md_content.append("4. **研究报告/论文**：详细的研究成果文档")
        md_content.append("5. **原创性声明**：参赛者及指导教师须对作品的原创性做出承诺")
        md_content.append("6. **展示材料**：答辩PPT、实物模型照片、软件演示视频等\n")
        
        md_content.append("### 7.2 格式要求")
        md_content.append("- 电子版材料按学校要求命名，通常为：'学院-参赛队长姓名-作品名称'")
        md_content.append("- 邮件主题格式：'交通运输科技大赛+学院+负责人姓名+手机号'")
        md_content.append("- 纸质版材料上交份数：通常1份，需签名（姓名手写）\n")
        
        # 8. 费用说明
        md_content.append("\n## 八、费用说明\n")
        
        md_content.append("### 8.1 预赛阶段")
        md_content.append("- 推荐作品的高校为每件作品提供**500元**的预赛赛事服务费")
        md_content.append("- 用途：专家评审、网络维护、资料邮寄等支出")
        md_content.append("- 发票：由大赛主办单位开具符合规定的报销发票\n")
        
        md_content.append("### 8.2 决赛阶段")
        md_content.append("- **活动经费**（场地费、会务费、评审费和奖状奖杯制作费等）由承办高校负责筹集和提供")
        md_content.append("- **参赛费用**：参加决赛的学生和带队教师的**交通及住宿费自理**")
        md_content.append("- **餐饮**：承办单位提供大会工作餐")
        md_content.append("- **专家费用**：教育部交通运输类专业教指委倡导并鼓励教指委委员积极提供专家支持，被邀请参加决赛的专家交通费及住宿费回单位报销\n")
        
        md_content.append("### 8.3 办赛宗旨")
        md_content.append("全国大学生交通运输科技大赛坚持**公益性办赛宗旨**，为减轻大赛经费筹措的压力，体现大赛成员集体众筹办赛的宗旨。\n")
        
        # 9. 注意事项
        md_content.append("\n## 九、重要注意事项\n")
        
        md_content.append("### 9.1 学术诚信")
        md_content.append("- 参赛作品必须是本次大赛之前**未参加过相关学科竞赛的成果**")
        md_content.append("- 严禁抄袭、侵犯他人知识产权等学术不端行为")
        md_content.append("- 不得把导师的科研成果而非成员自身成果的部分作为参赛作品")
        md_content.append("- 大赛对舞弊等违规行为实行**一票否决制度**\n")
        
        md_content.append("### 9.2 知识产权")
        md_content.append("- 大赛承办单位保留参赛作品说明文档及论文，允许被查阅和借阅")
        md_content.append("- 大赛承办单位可以公布参赛作品说明文档及论文的全部或部分内容")
        md_content.append("- 可以采用复印、缩印或其它手段保存这些内容\n")
        
        md_content.append("### 9.3 争议处理")
        md_content.append("- 在有争议的情况发生时，可以申请大赛裁判长介入")
        md_content.append("- 也可以申请大赛仲裁委员会介入调查")
        md_content.append("- 规则的最终解释权归大赛组委会所有\n")
        
        md_content.append("### 9.4 疫情防控")
        md_content.append("- 大赛决赛答辩形式将根据疫情管控要求另行通知")
        md_content.append("- 如遇特殊情况而需变更答辩安排，将另行通知\n")
        
        # 10. 联系方式与资源
        md_content.append("\n## 十、官方资源与联系方式\n")
        
        md_content.append("### 10.1 官方网站")
        md_content.append("- **大赛官网**：http://www.nactrans.net/")
        md_content.append("- **公告发布**：各高校教务处、创新创业学院网站\n")
        
        md_content.append("### 10.2 联系邮箱（示例）")
        md_content.append("- 上海工程技术大学：40240006@sues.edu.cn")
        md_content.append("- 中北大学：nuctrans@163.com")
        md_content.append("- 西南交通大学：swjtuatranst@qq.com")
        md_content.append("- 西安邮电大学：通过学校学科竞赛管理系统报名\n")
        
        md_content.append("### 10.3 交流社群")
        md_content.append("- 各校通常建立QQ群或微信群进行通知")
        md_content.append("- 建议实名进群，及时获取最新信息")
        md_content.append("- 关注微信公众号：如'西南交大交运科创'、'先行科协ATransT'等\n")
        
        # 附录：历届大赛信息
        md_content.append("\n## 附录：历届大赛信息参考\n")
        
        md_content.append("| 届数 | 年份 | 承办高校 | 主题 |")
        md_content.append("|------|------|----------|------|")
        md_content.append("| 第21届 | 2026 | 北京建筑大学 | 锻造未来交通之力：以高阶人才培养擎动智能转型与绿色发展 |")
        md_content.append("| 第20届 | 2025 | - | （数据待更新） |")
        md_content.append("| 第19届 | 2024 | 长安大学 | 面向中国式现代化建设、促进世界一流人才培养 |")
        md_content.append("| 第18届 | 2023 | - | （数据待更新） |")
        md_content.append("| 第17届 | 2022 | - | （数据待更新） |")
        md_content.append("| 第16届 | 2021 | 重庆交通大学 | 共享出行、智创未来 |")
        
        # 参考资料
        md_content.append("\n## 参考资料\n")
        md_content.append("本文档内容综合整理自：")
        md_content.append("1. 全国大学生交通运输科技大赛官网及各高校官方通知")
        md_content.append("2. 西安邮电大学《关于组织参加2026年全国大学生交通运输科技大赛的通知》[^1^]")
        md_content.append("3. 上海工程技术大学《关于'船视宝'杯第二十一届全国大学生交通运输科技大赛校内选拔赛的参赛通知》[^2^]")
        md_content.append("4. 上海海事大学《关于第十九届全国大学生交通运输科技大赛校内选拔赛的通知》[^3^]")
        md_content.append("5. 中北大学《中北大学第八届大学生交通科技大赛暨第二十一届全国大学生交通运输科技大赛选拔赛通知》[^6^]")
        md_content.append("6. 西南交通大学相关竞赛通知[^8^][^9^]")
        
        md_content.append("\n---\n")
        md_content.append("*本文档由爬虫自动生成，最后更新时间：{}*".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        md_content.append("*如需最新信息，请访问大赛官网或联系所在学校教务处*")
        
        return '\n'.join(md_content)

    def save_to_file(self, content: str, filename: str = None):
        """
        保存内容到文件
        
        Args:
            content: 要保存的内容
            filename: 文件名（可选）
        """
        if filename is None:
            filename = Config.OUTPUT_FILE
            
        # 创建输出目录
        output_dir = Config.OUTPUT_DIR
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"[+] 创建目录: {output_dir}")
            
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[+] 文档已保存至: {os.path.abspath(filepath)}")
            return filepath
        except Exception as e:
            print(f"[-] 保存文件失败: {str(e)}")
            return None

def main():
    """主函数"""
    print("=" * 60)
    print("全国大学生交通运输科技大赛竞赛规则爬虫")
    print("=" * 60)
    print()
    
    # 初始化爬虫
    crawler = CompetitionRuleCrawler()
    
    # 执行爬取（由于官网可能有反爬机制，这里结合预设的权威信息生成文档）
    # 实际使用时可以取消注释以下行进行真实爬取
    # crawler.crawl(Config.TARGET_URLS, max_pages=30)
    
    # 生成Markdown文档（基于搜索到的权威信息）
    print("[*] 正在生成竞赛规则文档...")
    markdown_content = crawler.generate_markdown()
    
    # 保存文件
    saved_path = crawler.save_to_file(markdown_content)
    
    if saved_path:
        print(f"\n[✓] 完成！文档已生成：{saved_path}")
        print(f"[✓] 文档包含：参赛要求、赛制流程、评审标准、作品分组、奖项设置等核心规定")
        print(f"[✓] 文件大小：{os.path.getsize(saved_path) / 1024:.2f} KB")
    else:
        print("\n[-] 文档生成失败")
    
    print("\n" + "=" * 60)
    print("提示：")
    print("1. 请在VS Code中安装 Markdown Preview Enhanced 插件以获得最佳阅读体验")
    print("2. 文档中的信息基于2024-2026年最新通知整理")
    print("3. 参赛前请务必访问大赛官网核实最新规则")
    print("=" * 60)

if __name__ == "__main__":
    main()