# -*- coding: utf-8 -*-
"""
全国高等院校数智化企业经营沙盘大赛 - 竞赛规则爬虫（修正版）
运行环境：VS Code (Python 3.8+)
功能：爬取参赛要求、赛制流程、评审标准等核心规定，保存为.md和.docx格式
"""

import requests
import re
import time
import os
from bs4 import BeautifulSoup
from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, RGBColor, Inches

# ==================== 配置区域 ====================
# 目标URL列表（均来自高校官方发布，信息可靠）
TARGET_URLS = [
    {
        'url': 'https://pec.xjtu.edu.cn/info/1117/4708.htm',
        'school': '西安交通大学',
        'date': '2025-04-29'
    },
    {
        'url': 'https://sub2.dlust.edu.cn/szjs/detail-5828.html',
        'school': '大连科技学院',
        'date': '2025-09-11'
    },
    {
        'url': 'https://cxcygl.bhu.edu.cn/comp/front/comp/info?id=MTc1MC01MWJjMWE',
        'school': '渤海大学',
        'date': '2025-05-21'
    },
    {
        'url': 'http://jwc.cfec.edu.cn/info/1043/7252.htm',
        'school': '重庆财经学院',
        'date': '2025-04-24'
    },
    {
        'url': 'https://ies.dufe.edu.cn/content_91795.html',
        'school': '东北财经大学',
        'date': '2025-05-19'
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# 保存文件名
MD_FILENAME = "全国高等院校数智化企业经营沙盘大赛_竞赛规则.md"
DOCX_FILENAME = "全国高等院校数智化企业经营沙盘大赛_竞赛规则.docx"
# =================================================

def fetch_html(url):
    """获取网页HTML内容"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.encoding = 'utf-8'  # 大部分高校网站使用utf-8
        if response.status_code == 200:
            return response.text
        else:
            print(f"请求失败 {url}, 状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"请求异常 {url}: {e}")
        return None

def parse_competition_rules(html, school, date, url):
    """
    解析HTML，提取竞赛相关的核心规则
    返回字典格式的结构化数据
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    # 移除script和style标签
    for script in soup(["script", "style"]):
        script.decompose()
    
    # 获取页面文本内容
    text = soup.get_text()
    # 清理多余空白
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    
    # 使用正则表达式提取各个模块
    rules = {
        'school': school,
        'date': date,
        'url': url,  # 现在url已定义
        '参赛要求': '未找到明确参赛要求',
        '竞赛内容': '未找到明确竞赛内容',
        '赛制流程': '未找到明确赛制流程',
        '评审标准': '未找到明确评审标准',
        '奖项设置': '未找到明确奖项设置'
    }
    
    # 1. 提取参赛要求 (关键词: 参赛对象、组队、报名条件)
    pattern_require = re.search(r'(参赛对象[\s\S]{0,200}?[。；]|组队要求[\s\S]{0,200}?[。；]|报名条件[\s\S]{0,200}?[。；])', text)
    if pattern_require:
        rules['参赛要求'] = pattern_require.group(0).replace('\n', ' ')
    else:
        # 备用提取：4名选手、指导老师等关键词
        backup = re.search(r'每支参赛团队由(\d+)名队员.*?(?=[。；])', text)
        if backup:
            rules['参赛要求'] = backup.group(0)
    
    # 2. 提取竞赛内容 (关键词: 竞赛内容、赛项考察、模拟)
    pattern_content = re.search(r'(竞赛内容[\s\S]{0,500}?[。；]|赛项考察[\s\S]{0,500}?[。；]|模拟.*?总监.*?[。；])', text)
    if pattern_content:
        rules['竞赛内容'] = pattern_content.group(0).replace('\n', ' ')
    else:
        # 提取包含"营销总监、财务总监"的句子
        content_sentences = re.findall(r'([^。]*?营销总监[^。]*?财务总监[^。]*?[。])', text)
        if content_sentences:
            rules['竞赛内容'] = content_sentences[0]
    
    # 3. 提取赛制流程 (关键词: 赛程、校赛、省赛、国赛、阶段)
    pattern_process = re.search(r'(赛程[\s\S]{0,300}?[。；]|校赛.*?省赛.*?国赛|第[一二]赛段[\s\S]{0,300}?[。；])', text)
    if pattern_process:
        rules['赛制流程'] = pattern_process.group(0).replace('\n', ' ')
    else:
        # 查找包含"60%"和"路演"的描述（省赛国赛常见比例）
        process = re.search(r'对抗赛段成绩占比为.*?。', text)
        if process:
            rules['赛制流程'] = process.group(0)
    
    # 4. 提取评审标准 (关键词: 评分、评审、成绩、系统自动)
    pattern_score = re.search(r'(评分标准[\s\S]{0,300}?[。；]|评审方式[\s\S]{0,300}?[。；]|系统自动评分[\s\S]{0,200}?[。；])', text)
    if pattern_score:
        rules['评审标准'] = pattern_score.group(0).replace('\n', ' ')
    else:
        # 查找排名规则
        rank = re.search(r'(如总成绩相同.*?[。；])', text)
        if rank:
            rules['评审标准'] = rank.group(0)
    
    # 5. 提取奖项设置 (关键词: 奖项、一等奖、二等奖、证书)
    pattern_award = re.search(r'(奖项设置[\s\S]{0,200}?[。；]|一等奖[\s\S]{0,100}?[。；]|获奖比例[\s\S]{0,100}?[。；])', text)
    if pattern_award:
        rules['奖项设置'] = pattern_award.group(0).replace('\n', ' ')
    
    # 清理多余的换行和空格
    for key in rules:
        if isinstance(rules[key], str):
            rules[key] = re.sub(r'\s+', ' ', rules[key]).strip()
    
    return rules

def save_to_markdown(all_rules, filename):
    """将规则保存为Markdown文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# 全国高等院校数智化企业经营沙盘大赛竞赛规则\n\n")
        f.write(f"> 数据抓取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"> 信息来源: 多所高校官网发布通知\n\n")
        
        for i, rules in enumerate(all_rules, 1):
            f.write(f"## {i}. 信息来源: {rules['school']} (发布时间: {rules['date']})\n\n")
            f.write(f"- **原始链接**: {rules['url']}\n\n")
            f.write(f"### 参赛要求\n{rules['参赛要求']}\n\n")
            f.write(f"### 竞赛内容\n{rules['竞赛内容']}\n\n")
            f.write(f"### 赛制流程\n{rules['赛制流程']}\n\n")
            f.write(f"### 评审标准\n{rules['评审标准']}\n\n")
            f.write(f"### 奖项设置\n{rules['奖项设置']}\n\n")
            f.write("---\n\n")
    
    print(f"[✓] Markdown文件已保存: {filename}")

def save_to_docx(all_rules, filename):
    """将规则保存为Word文档"""
    doc = Document()
    
    # 设置标题样式
    title = doc.add_heading('全国高等院校数智化企业经营沙盘大赛竞赛规则', 0)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    # 添加抓取时间
    p = doc.add_paragraph(f'数据抓取时间: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    p = doc.add_paragraph('信息来源: 多所高校官网发布通知')
    p.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    
    for i, rules in enumerate(all_rules, 1):
        doc.add_heading(f'{i}. 信息来源: {rules["school"]}', level=1)
        doc.add_paragraph(f'发布时间: {rules["date"]}')
        doc.add_paragraph(f'原始链接: {rules["url"]}', style='Intense Quote')
        
        doc.add_heading('参赛要求', level=2)
        doc.add_paragraph(rules['参赛要求'])
        
        doc.add_heading('竞赛内容', level=2)
        doc.add_paragraph(rules['竞赛内容'])
        
        doc.add_heading('赛制流程', level=2)
        doc.add_paragraph(rules['赛制流程'])
        
        doc.add_heading('评审标准', level=2)
        doc.add_paragraph(rules['评审标准'])
        
        doc.add_heading('奖项设置', level=2)
        doc.add_paragraph(rules['奖项设置'])
        
        # 添加分隔线（水平线）
        doc.add_paragraph('_' * 50)
    
    # 保存文档
    doc.save(filename)
    print(f"[✓] Word文档已保存: {filename}")

def main():
    print("="*60)
    print("开始抓取《全国高等院校数智化企业经营沙盘大赛》竞赛规则")
    print("="*60)
    
    all_rules = []
    for target in TARGET_URLS:
        print(f"\n正在处理: {target['school']} - {target['url']}")
        html = fetch_html(target['url'])
        if html:
            # 修正：将url作为参数传入
            rules = parse_competition_rules(html, target['school'], target['date'], target['url'])
            all_rules.append(rules)
            print(f"  √ 解析完成")
        else:
            print(f"  × 抓取失败")
        time.sleep(1)  # 礼貌性延迟
    
    if all_rules:
        # 保存文件
        save_to_markdown(all_rules, MD_FILENAME)
        save_to_docx(all_rules, DOCX_FILENAME)
        print("\n" + "="*60)
        print("所有任务完成！生成的文件如下：")
        print(f"1. {MD_FILENAME}")
        print(f"2. {DOCX_FILENAME}")
        print("="*60)
    else:
        print("\n[!] 未抓取到任何数据，请检查网络或URL有效性。")

if __name__ == "__main__":
    # 检查依赖库是否安装
    try:
        import bs4
        import docx
    except ImportError as e:
        print("缺少必要的库，请安装：")
        print("pip install beautifulsoup4 requests python-docx")
        exit(1)
    
    main()