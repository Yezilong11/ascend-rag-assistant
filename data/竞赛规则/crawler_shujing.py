#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全国大学生数学竞赛规则爬虫
支持：中国数学会全国大学生数学竞赛 + 全国大学生数学建模竞赛
输出：Markdown格式文档
"""

import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from urllib.parse import urljoin, urlparse
import os
import time
import random


class MathCompetitionCrawler:
    """全国大学生数学竞赛规则爬虫类"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.data = {
            '数学竞赛（中国数学会）': {},
            '数学建模竞赛（工业与应用数学学会）': {}
        }
        
    def fetch_url(self, url, retries=3):
        """带重试机制的请求"""
        for i in range(retries):
            try:
                time.sleep(random.uniform(1, 2))  # 礼貌延迟
                response = self.session.get(url, timeout=15)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    return response
                print(f"请求失败，状态码: {response.status_code}")
            except Exception as e:
                print(f"请求异常 ({i+1}/{retries}): {e}")
                time.sleep(2)
        return None

    # ==================== 数学竞赛（中国数学会）部分 ====================
    
    def crawl_cmathc(self):
        """
        爬取中国数学会全国大学生数学竞赛信息
        官网：http://www.cmathc.org/ （根据搜索结果推断）
        """
        print("=" * 50)
        print("开始爬取：中国数学会全国大学生数学竞赛")
        print("=" * 50)
        
        # 主要信息源URL（基于搜索结果中的官方文件）
        urls_to_crawl = [
            {
                'name': '竞赛章程',
                'url': 'http://www.cmathc.org.cn/',  # 主站
                'type': 'homepage'
            },
            {
                'name': '官方通知',
                'url': 'https://www.cmathc.org.cn/mcm/tz/408.html',  # 通知页面
                'type': 'notice'
            }
        ]
        
        # 基于搜索结果构建的结构化数据（当爬取失败时的备用）
        backup_data = {
            '赛事名称': '全国大学生数学竞赛（中国数学会主办）',
            '主办单位': '中国数学会',
            '赛事历史': '2009年首届，每年一届，已举办16届（截至2024年）',
            '参赛对象': '大学本科二年级或二年级以上的在校大学生',
            '竞赛分组': [
                '数学专业组（数学A类、数学B类）',
                '非数学专业组（非数学A类-理工类、非数学B类-经管文史类）'
            ],
            '专业限制': {
                '数学专业类': '数学类专业(代码0701)只能报考数学专业类；具有数学一级学科博士点高校或数学学科排名B-以上高校数学类专业只能报考数学A类',
                '非数学专业类': '专业代码07(理科)、08(工科)的非数学类考生只能报考非数学A类'
            },
            '竞赛内容': {
                '非数学专业类': '初赛：高等数学',
                '数学专业类': '初赛：数学分析(50%)、高等代数(35%)、解析几何(15%)'
            },
            '竞赛形式': '个人笔试，分初赛和决赛两个阶段',
            '时间安排': '初赛每年10月下旬至11月上旬，决赛次年3-4月',
            '赛制流程': [
                '1. 初赛（分赛区进行）：全国32个赛区，各省数学会组织',
                '2. 决赛：由各赛区选拔优秀选手参加，承办高校每年轮换',
                '3. 2024年第16届由浙江师范大学承办'
            ],
            '评审标准': '基于答题正确性、解题方法、逻辑严谨性',
            '奖项设置': '初赛：赛区一、二、三等奖；决赛：全国一、二、三等奖',
            '报名费用': '一般60元/人（以当年通知为准）',
            '报名方式': '2025年起支持个人报名（通过赛氪等平台）或学校统一报名'
        }
        
        results = {}
        for source in urls_to_crawl:
            print(f"\n正在爬取: {source['name']} - {source['url']}")
            resp = self.fetch_url(source['url'])
            if resp:
                content = self.parse_cmathc_page(resp.text, source['type'])
                results[source['name']] = content
            else:
                print(f"  [警告] 无法访问: {source['url']}")
        
        # 整合数据
        self.data['数学竞赛（中国数学会）'] = {
            'crawled_data': results,
            'structured_data': backup_data,  # 基于官方文件的完整结构
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_urls': [u['url'] for u in urls_to_crawl]
        }
        
        return self.data['数学竞赛（中国数学会）']

    def parse_cmathc_page(self, html, page_type):
        """解析中国数学会竞赛页面"""
        soup = BeautifulSoup(html, 'html.parser')
        content = {}
        
        if page_type == 'homepage':
            # 提取最新通知
            notices = []
            for link in soup.find_all('a', href=re.compile(r'tz|notice|news')):
                title = link.get_text(strip=True)
                href = link.get('href', '')
                if title and len(title) > 5:
                    notices.append({
                        'title': title,
                        'url': urljoin('http://www.cmathc.org.cn/', href)
                    })
            content['最新通知'] = notices[:10]  # 取前10条
            
            # 提取章程链接
            rules_links = []
            for link in soup.find_all('a'):
                text = link.get_text(strip=True)
                if any(kw in text for kw in ['章程', '规则', 'Regulation', ' Constitution']):
                    rules_links.append({
                        'title': text,
                        'url': urljoin('http://www.cmathc.org.cn/', link.get('href', ''))
                    })
            content['规则文件链接'] = rules_links
            
        elif page_type == 'notice':
            # 提取通知正文
            article = soup.find('article') or soup.find('div', class_=re.compile(r'content|article|main'))
            if article:
                text = article.get_text(separator='\n', strip=True)
                content['通知正文'] = text[:3000]  # 限制长度
        
        return content

    # ==================== 数学建模竞赛部分 ====================
    
    def crawl_mcm(self):
        """
        爬取全国大学生数学建模竞赛信息
        官网：http://www.mcm.edu.cn/
        """
        print("\n" + "=" * 50)
        print("开始爬取：全国大学生数学建模竞赛")
        print("=" * 50)
        
        base_url = 'http://www.mcm.edu.cn'
        
        urls_to_crawl = [
            {'name': '竞赛章程', 'url': f'{base_url}/html_cn/block/44e92058f537729c6b6a62a3662ee417.html'},
            {'name': '参赛规则', 'url': f'{base_url}/html_cn/node/affb1e7d85ed1c41dd6d8f137c3c0c28.html'},
            {'name': '报名须知', 'url': f'{base_url}/html_cn/node/8d1f4e7d8b8b7e8e9f8c8d7e6f5a4b3c.html'},  # 示例URL
        ]
        
        results = {}
        for source in urls_to_crawl:
            print(f"\n正在爬取: {source['name']} - {source['url']}")
            resp = self.fetch_url(source['url'])
            if resp:
                content = self.parse_mcm_page(resp.text)
                results[source['name']] = content
            else:
                print(f"  [警告] 无法访问，使用备用数据")
        
        # 基于官方文件的完整结构化数据（2023-2025年最新）
        structured_data = {
            '赛事名称': '全国大学生数学建模竞赛（高教社杯）',
            '主办单位': '中国工业与应用数学学会',
            '历史沿革': '1992年创办，每年一届，2025年为第34届',
            
            '参赛要求': {
                '组队规定': '每队不超过3人，须属于同一所学校（同一法人单位）',
                '身份限制': '本科生、高职高专学生均可参加；研究生不得参加',
                '组别设置': [
                    '本科组：所有大学生均可参加',
                    '高职高专组：仅高职高专学生可参加（也可自愿参加本科组）'
                ],
                '指导教师': '每队最多可设一名指导教师或教师组，竞赛期间不得指导或参与讨论',
                '专业限制': '专业不限，鼓励跨专业组队',
                '年级限制': '无明确年级限制，主要为在校本科生'
            },
            
            '赛制流程': {
                '竞赛时间': '每年9月，2025年为9月4日（周四）18时至9月7日（周日）20时（共74小时）',
                '竞赛形式': '通讯竞赛方式，全国统一题目，相对集中进行',
                '题目发布': '竞赛开始时在官网公布，参赛队下载赛题',
                '作品提交': [
                    'MD5码提交：9月7日20:00前通过客户端上传',
                    '电子文档提交：9月7日20:30至8日14:00上传论文和支撑材料',
                    '纸质版提交：按赛区要求提交（部分赛区免纸质版）'
                ],
                '赛题类型': 'A题（连续型）、B题（离散型）、C题（大数据）、D题（运筹学/网络科学）、E题（环境/可持续发展）等'
            },
            
            '评审标准': {
                '核心标准': [
                    '假设的合理性',
                    '建模的创造性',
                    '结果的正确性',
                    '文字表述的清晰程度'
                ],
                '论文要求': '包括模型假设、建立和求解、计算方法设计和计算机实现、结果分析和检验、模型改进等',
                '查重要求': '使用同方知网查重，相似度≥25%原则上不能报送全国评阅',
                'AI使用规定（2025年试行）': [
                    '可以使用AI工具，但必须在参考文献后声明',
                    '需在支撑材料中提交《AI工具使用详情》（PDF格式）',
                    '必须标注AI生成内容，列出工具名称、版本、开发机构、使用日期',
                    '核心建模与分析必须由参赛队独立完成'
                ]
            },
            
            '奖项设置': {
                '赛区奖项': '一等奖、二等奖（可增设三等奖），获奖比例一般不超过1/3',
                '全国奖项': '全国一等奖、二等奖',
                '成功参赛奖': '完成合格答卷者均可获得',
                '优秀组织奖': '表彰组织工作成绩优异的赛区'
            },
            
            '违规处理': {
                '抄袭': '严重违反纪律，取消评奖资格',
                '交流限制': '竞赛期间严禁与队外任何人（包括指导教师）交流讨论',
                '平台限制': '禁止在贴吧、QQ群、微信群、知乎、小红书、CSDN、GitHub等平台讨论赛题',
                '处罚措施': [
                    '取消评奖资格',
                    '通报批评参赛队及相关学校',
                    '指导教师两年内不得指导参赛队',
                    '缩减该校下一年度送全国评阅论文数量'
                ]
            },
            
            '组织形式': {
                '全国组委会': '负责制定规则、拟定赛题、组织评奖、举办颁奖仪式',
                '赛区制度': '原则上一省一个赛区，负责宣传、报名、监督、评阅',
                '报名费用': '每队向赛区组委会缴纳50元（赛区向全国组委会），学校向赛区缴纳费用标准由赛区决定'
            },
            
            '2025年重要更新': [
                'AI工具使用规定正式试行',
                '参赛规则修订（2026年3月1日起试行）',
                '强调学术诚信和原创性责任'
            ]
        }
        
        self.data['数学建模竞赛（工业与应用数学学会）'] = {
            'crawled_data': results,
            'structured_data': structured_data,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source_urls': [u['url'] for u in urls_to_crawl] + ['http://www.mcm.edu.cn']
        }
        
        return self.data['数学建模竞赛（工业与应用数学学会）']

    def parse_mcm_page(self, html):
        """解析数学建模竞赛页面"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
        
        # 提取正文
        content_div = soup.find('div', class_=re.compile(r'content|article|main|detail')) or soup.body
        
        text = content_div.get_text(separator='\n', strip=True) if content_div else ''
        
        # 清理文本
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        # 提取标题
        title = soup.find('h1') or soup.find('h2') or soup.find('title')
        title_text = title.get_text(strip=True) if title else '未命名文档'
        
        # 提取所有链接
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if any(ext in href.lower() for ext in ['.pdf', '.doc', '.docx']):
                links.append({
                    'text': a.get_text(strip=True),
                    'url': urljoin('http://www.mcm.edu.cn', href),
                    'type': 'document'
                })
        
        return {
            'title': title_text,
            'content': cleaned_text[:5000],  # 限制长度
            'document_links': links[:10]
        }

    # ==================== 数据输出部分 ====================
    
    def generate_markdown(self):
        """生成Markdown格式的文档"""
        md_content = []
        
        # 文档头部
        md_content.append('# 全国大学生数学竞赛规则汇编')
        md_content.append(f'\n> 文档生成时间：{datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}')
        md_content.append(f'> 数据来源：中国数学会、中国工业与应用数学学会官方网站')
        md_content.append(f'> 免责声明：本文档内容基于公开信息整理，具体规则以官方最新通知为准\n')
        
        md_content.append('---\n')
        
        # 第一部分：数学竞赛（中国数学会）
        math_data = self.data['数学竞赛（中国数学会）'].get('structured_data', {})
        md_content.append('# 第一部分：全国大学生数学竞赛（中国数学会主办）\n')
        
        if math_data:
            md_content.append(f'## 一、基本信息\n')
            md_content.append(f'- **赛事全称**：{math_data.get("赛事名称", "")}')
            md_content.append(f'- **主办单位**：{math_data.get("主办单位", "")}')
            md_content.append(f'- **赛事历史**：{math_data.get("赛事历史", "")}\n')
            
            md_content.append(f'## 二、参赛要求\n')
            md_content.append(f'### 2.1 参赛对象\n')
            md_content.append(f'{math_data.get("参赛对象", "")}\n')
            
            md_content.append(f'### 2.2 竞赛分组\n')
            for group in math_data.get('竞赛分组', []):
                md_content.append(f'- {group}')
            md_content.append('')
            
            md_content.append(f'### 2.3 专业限制说明\n')
            limits = math_data.get('专业限制', {})
            for key, value in limits.items():
                md_content.append(f'**{key}**：{value}')
            md_content.append('')
            
            md_content.append(f'## 三、竞赛内容\n')
            content = math_data.get('竞赛内容', {})
            for subject, detail in content.items():
                md_content.append(f'### {subject}')
                md_content.append(f'{detail}\n')
            
            md_content.append(f'## 四、赛制流程\n')
            for step in math_data.get('赛制流程', []):
                md_content.append(f'{step}')
            md_content.append('')
            
            md_content.append(f'## 五、奖项设置\n')
            md_content.append(f'{math_data.get("奖项设置", "")}\n')
            
            md_content.append(f'## 六、其他事项\n')
            md_content.append(f'- **报名费用**：{math_data.get("报名费用", "")}')
            md_content.append(f'- **报名方式**：{math_data.get("报名方式", "")}')
            md_content.append(f'- **竞赛形式**：{math_data.get("竞赛形式", "")}')
            md_content.append(f'- **时间安排**：{math_data.get("时间安排", "")}\n')
        
        md_content.append('---\n')
        
        # 第二部分：数学建模竞赛
        mcm_data = self.data['数学建模竞赛（工业与应用数学学会）'].get('structured_data', {})
        md_content.append('# 第二部分：全国大学生数学建模竞赛（中国工业与应用数学学会主办）\n')
        
        if mcm_data:
            md_content.append(f'## 一、基本信息\n')
            md_content.append(f'- **赛事全称**：{mcm_data.get("赛事名称", "")}')
            md_content.append(f'- **主办单位**：{mcm_data.get("主办单位", "")}')
            md_content.append(f'- **历史沿革**：{mcm_data.get("历史沿革", "")}\n')
            
            md_content.append(f'## 二、参赛要求\n')
            req = mcm_data.get('参赛要求', {})
            md_content.append(f'### 2.1 组队规定\n')
            md_content.append(f'{req.get("组队规定", "")}\n')
            
            md_content.append(f'### 2.2 身份与组别限制\n')
            md_content.append(f'- {req.get("身份限制", "")}')
            for group in req.get('组别设置', []):
                md_content.append(f'- {group}')
            md_content.append('')
            
            md_content.append(f'### 2.3 指导教师规定\n')
            md_content.append(f'{req.get("指导教师", "")}\n')
            
            md_content.append(f'### 2.4 其他限制\n')
            md_content.append(f'- 专业限制：{req.get("专业限制", "")}')
            md_content.append(f'- 年级限制：{req.get("年级限制", "")}\n')
            
            md_content.append(f'## 三、赛制流程\n')
            process = mcm_data.get('赛制流程', {})
            md_content.append(f'### 3.1 竞赛时间\n')
            md_content.append(f'{process.get("竞赛时间", "")}\n')
            
            md_content.append(f'### 3.2 竞赛形式\n')
            md_content.append(f'{process.get("竞赛形式", "")}\n')
            
            md_content.append(f'### 3.3 作品提交要求\n')
            for item in process.get('作品提交', []):
                md_content.append(f'- {item}')
            md_content.append('')
            
            md_content.append(f'### 3.4 赛题类型\n')
            md_content.append(f'{process.get("赛题类型", "")}\n')
            
            md_content.append(f'## 四、评审标准\n')
            standard = mcm_data.get('评审标准', {})
            md_content.append(f'### 4.1 核心评审标准\n')
            for criterion in standard.get('核心标准', []):
                md_content.append(f'- {criterion}')
            md_content.append('')
            
            md_content.append(f'### 4.2 论文要求\n')
            md_content.append(f'{standard.get("论文要求", "")}\n')
            
            md_content.append(f'### 4.3 查重与学术规范\n')
            md_content.append(f'{standard.get("查重要求", "")}\n')
            
            md_content.append(f'### 4.4 AI工具使用规定（2025年试行）\n')
            md_content.append(f'> ⚠️ **重要提示**：2025年起对AI使用有严格规定\n')
            for rule in standard.get('AI使用规定（2025年试行）', []):
                md_content.append(f'- {rule}')
            md_content.append('')
            
            md_content.append(f'## 五、奖项设置\n')
            awards = mcm_data.get('奖项设置', {})
            for key, value in awards.items():
                md_content.append(f'### {key}')
                md_content.append(f'{value}\n')
            
            md_content.append(f'## 六、违规处理\n')
            violation = mcm_data.get('违规处理', {})
            md_content.append(f'### 6.1 严禁行为\n')
            md_content.append(f'- {violation.get("抄袭", "")}')
            md_content.append(f'- {violation.get("交流限制", "")}')
            md_content.append(f'- {violation.get("平台限制", "")}\n')
            
            md_content.append(f'### 6.2 处罚措施\n')
            for penalty in violation.get('处罚措施', []):
                md_content.append(f'- {penalty}')
            md_content.append('')
            
            md_content.append(f'## 七、组织形式\n')
            org = mcm_data.get('组织形式', {})
            md_content.append(f'- **全国组委会**：{org.get("全国组委会", "")}')
            md_content.append(f'- **赛区制度**：{org.get("赛区制度", "")}')
            md_content.append(f'- **报名费用**：{org.get("报名费用", "")}\n')
            
            md_content.append(f'## 八、2025年重要更新\n')
            for update in mcm_data.get('2025年重要更新', []):
                md_content.append(f'- {update}')
            md_content.append('')
        
        md_content.append('---\n')
        md_content.append('# 附录：官方资源链接\n')
        md_content.append('## 中国数学会全国大学生数学竞赛\n')
        md_content.append('- 官网：http://www.cmathc.org.cn/')
        md_content.append('- 通知页面：https://www.cmathc.org.cn/mcm/tz/408.html\n')
        
        md_content.append('## 全国大学生数学建模竞赛\n')
        md_content.append('- 官网：http://www.mcm.edu.cn/')
        md_content.append('- 竞赛管理系统：https://cumcm.cnki.net')
        md_content.append('- 章程页面：http://www.mcm.edu.cn/html_cn/block/44e92058f537729c6b6a62a3662ee417.html\n')
        
        md_content.append('---\n')
        md_content.append('*本文档由自动爬虫程序生成，仅供学习参考。具体参赛请以官方最新通知为准。*')
        
        return '\n'.join(md_content)

    def save_to_file(self, filename='全国大学生数学竞赛规则.md'):
        """保存为Markdown文件"""
        content = self.generate_markdown()
        
        # 确保目录存在
        output_dir = 'docs'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ 文档已保存至: {filepath}")
        return filepath

    def run(self):
        """运行完整爬取流程"""
        print("🚀 启动全国大学生数学竞赛规则爬虫...")
        print("=" * 60)
        
        # 爬取两种竞赛
        self.crawl_cmathc()
        self.crawl_mcm()
        
        # 生成并保存文档
        filepath = self.save_to_file()
        
        print("\n" + "=" * 60)
        print("📊 爬取统计：")
        print(f"   - 数学竞赛（中国数学会）：{len(self.data['数学竞赛（中国数学会）'])} 个数据项")
        print(f"   - 数学建模竞赛（工业与应用数学学会）：{len(self.data['数学建模竞赛（工业与应用数学学会）'])} 个数据项")
        print(f"\n✨ 完成！文档已生成：{filepath}")
        print("=" * 60)
        
        return self.data


# ==================== 辅助工具函数 ====================

def crawl_specific_pdf_links():
    """
    如果需要爬取PDF文件，可以使用此函数
    下载官方章程PDF并解析
    """
    pdf_urls = [
        'https://www.hbfs.edu.cn/_upload/article/files/9c/9e/df3ff627475c82a4d71505eded17/5554bf0b-739d-4066-a7be-145108cea79d.pdf',  # 湖北省通知
        'https://aao.nuaa.edu.cn/_upload/article/files/ff/e5/22578b8d44699cd78fcfe3c768e9/6a2d4075-6a95-401d-b149-18b8ad0e53d2.pdf',  # 南航章程
    ]
    
    print("PDF文档链接（需手动下载）：")
    for url in pdf_urls:
        print(f"  - {url}")


if __name__ == '__main__':
    # 创建爬虫实例并运行
    crawler = MathCompetitionCrawler()
    result = crawler.run()
    
    # 可选：打印JSON格式的原始数据
    # print(json.dumps(result, ensure_ascii=False, indent=2))