"""
中国工业智能挑战赛竞赛规则爬虫
抓取内容：参赛要求、赛制流程、评审标准等核心规定
输出格式：Markdown (.md) 和 文本文件 (.txt)
运行环境：VS Code (Python 3.6+)
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
from typing import List, Dict
import time

# ==================== 配置区域 ====================
# 目标URL列表（均来自官方或权威渠道）
TARGET_URLS = [
    {
        "url": "https://www.caa.org.cn/Content/248.html",  # 中国自动化学会官网
        "name": "主办方介绍",
        "priority": 1
    },
    {
        "url": "https://siee.hitwh.edu.cn/2025/0415/c1677a194416/page.htm",  # 哈工大威海（2025通知）
        "name": "参赛通知",
        "priority": 2
    },
    {
        "url": "https://hitee.hit.edu.cn/2024/0829/c17101a351790/page.htm",  # 哈工大电气学院（2025选拔）
        "name": "校内选拔",
        "priority": 2
    },
    {
        "url": "https://blog.csdn.net/m0_47916880/article/details/141531005",  # 参赛经验（含详细评审标准）
        "name": "评审细节",
        "priority": 3
    }
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

OUTPUT_DIR = "中国工业智能挑战赛_竞赛规则"
REQUEST_DELAY = 1  # 请求间隔（秒），避免被封

# ==================== 爬虫核心类 ====================
class CompetitionSpider:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.all_content = []
        
    def fetch_page(self, url: str) -> str:
        """获取网页内容"""
        try:
            print(f"  正在获取: {url}")
            time.sleep(REQUEST_DELAY)  # 礼貌延迟
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'  # 强制UTF-8
            if response.status_code == 200:
                return response.text
            else:
                print(f"  ! 请求失败，状态码: {response.status_code}")
                return ""
        except Exception as e:
            print(f"  ! 请求异常: {e}")
            return ""
    
    def parse_caa_page(self, html: str, source_name: str) -> Dict:
        """解析中国自动化学会官网页面"""
        soup = BeautifulSoup(html, 'html.parser')
        content = {
            "title": "中国工业智能挑战赛 - 官方介绍",
            "source": source_name,
            "url": TARGET_URLS[0]["url"],
            "sections": []
        }
        
        # 找到主要内容区域
        main_content = soup.find('div', class_='content') or soup.find('div', class_='article-content') or soup.find('body')
        if not main_content:
            main_content = soup
        
        text = main_content.get_text(separator='\n', strip=True)
        
        # 提取关键段落（参赛要求、赛制、评审）
        sections = {
            "简介": "",
            "参赛要求": "",
            "赛制流程": "",
            "评审标准": "",
            "其他信息": ""
        }
        
        # 简单的段落分类（基于关键词）
        paragraphs = text.split('\n')
        for para in paragraphs:
            para = para.strip()
            if len(para) < 10:
                continue
                
            lower_para = para.lower()
            if any(k in lower_para for k in ['参赛', '对象', '学生', '队员', '报名']):
                sections["参赛要求"] += para + "\n\n"
            elif any(k in lower_para for k in ['初赛', '决赛', '赛制', '流程', '阶段', '时间']):
                sections["赛制流程"] += para + "\n\n"
            elif any(k in lower_para for k in ['评审', '评分', '标准', '打分', '评判']):
                sections["评审标准"] += para + "\n\n"
            elif any(k in lower_para for k in ['宗旨', '目的', '背景', '简介']):
                sections["简介"] += para + "\n\n"
            else:
                sections["其他信息"] += para + "\n\n"
        
        for key, value in sections.items():
            if value.strip():
                content["sections"].append({"heading": key, "content": value.strip()})
        
        return content
    
    def parse_university_page(self, html: str, url: str, source_name: str) -> Dict:
        """解析高校通知页面"""
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "无标题"
        
        content = {
            "title": title,
            "source": source_name,
            "url": url,
            "sections": []
        }
        
        # 尝试多种常见的内容区域选择器
        content_area = (
            soup.find('div', class_='content') or 
            soup.find('div', class_='article-content') or 
            soup.find('div', class_='post-content') or
            soup.find('div', id='content') or
            soup.find('div', class_='entry-content') or
            soup.find('div', class_='main-content') or
            soup.find('div', {'style': 'font-size: 16px;'}) or
            soup.find('div', class_='v_news_content')
        )
        
        if not content_area:
            # 回退：获取body
            content_area = soup.find('body')
        
        if content_area:
            # 移除脚本、样式
            for script in content_area.find_all(['script', 'style']):
                script.decompose()
            
            # 获取所有文本段落
            paragraphs = content_area.find_all(['p', 'div', 'h2', 'h3', 'li'])
            current_section = "概述"
            section_text = []
            
            for elem in paragraphs:
                text = elem.get_text(strip=True)
                if not text or len(text) < 5:
                    continue
                
                # 检测是否为标题
                if elem.name in ['h2', 'h3'] or re.search(r'[一二三四五六七八九十]、|\d+\.', text[:10]):
                    if section_text:
                        content["sections"].append({
                            "heading": current_section,
                            "content": '\n'.join(section_text).strip()
                        })
                        section_text = []
                    current_section = text[:50]  # 取前50字作为标题
                else:
                    section_text.append(text)
            
            # 添加最后一部分
            if section_text:
                content["sections"].append({
                    "heading": current_section,
                    "content": '\n'.join(section_text).strip()
                })
        
        return content
    
    def parse_blog_page(self, html: str, url: str, source_name: str) -> Dict:
        """解析博客经验贴（包含评审标准）"""
        soup = BeautifulSoup(html, 'html.parser')
        title_tag = soup.find('h1') or soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else "经验参考"
        
        content = {
            "title": title,
            "source": source_name,
            "url": url,
            "sections": []
        }
        
        # CSDN博客正文通常在article或div#content_views
        article = soup.find('article') or soup.find('div', id='content_views') or soup.find('div', class_='blog-content-box')
        if article:
            # 提取所有标题和内容
            current_heading = "概述"
            current_content = []
            
            for elem in article.find_all(['h2', 'h3', 'h4', 'p', 'pre', 'div']):
                if elem.name in ['h2', 'h3', 'h4']:
                    if current_content:
                        content["sections"].append({
                            "heading": current_heading,
                            "content": '\n'.join(current_content).strip()
                        })
                    current_heading = elem.get_text(strip=True)
                    current_content = []
                elif elem.name == 'p' and elem.find('strong'):
                    # 可能是隐含标题
                    strong = elem.find('strong')
                    if strong:
                        if current_content:
                            content["sections"].append({
                                "heading": current_heading,
                                "content": '\n'.join(current_content).strip()
                            })
                        current_heading = strong.get_text(strip=True)
                        # 移除strong标签后的文本
                        strong.extract()
                        remaining = elem.get_text(strip=True)
                        if remaining:
                            current_content.append(remaining)
                else:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5:
                        current_content.append(text)
            
            # 最后一部分
            if current_content:
                content["sections"].append({
                    "heading": current_heading,
                    "content": '\n'.join(current_content).strip()
                })
        
        return content
    
    def crawl_all(self):
        """执行所有页面的爬取"""
        for target in TARGET_URLS:
            print(f"\n▶ 正在处理: {target['name']}")
            html = self.fetch_page(target["url"])
            if not html:
                continue
            
            # 根据URL或名称选择合适的解析器
            if "caa.org.cn" in target["url"]:
                parsed = self.parse_caa_page(html, target["name"])
            elif "blog.csdn.net" in target["url"]:
                parsed = self.parse_blog_page(html, target["url"], target["name"])
            else:
                parsed = self.parse_university_page(html, target["url"], target["name"])
            
            self.all_content.append(parsed)
            print(f"  ✓ 已提取 {len(parsed['sections'])} 个章节")

# ==================== 输出生成器 ====================
class OutputGenerator:
    @staticmethod
    def generate_markdown(all_content: List[Dict]) -> str:
        """生成Markdown格式文档"""
        lines = []
        
        # 文档头
        lines.append("# 中国工业智能挑战赛竞赛规则\n")
        lines.append(f"> 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        lines.append("> 信息来源：中国自动化学会、高校官网、参赛经验\n")
        lines.append("\n---\n")
        
        for idx, source in enumerate(all_content, 1):
            lines.append(f"## {idx}. {source['title']}\n")
            lines.append(f"- **来源**：{source['source']}\n")
            lines.append(f"- **原始链接**：{source['url']}\n")
            lines.append("\n")
            
            for section in source['sections']:
                lines.append(f"### {section['heading']}\n")
                lines.append(f"{section['content']}\n")
                lines.append("\n")
            
            lines.append("---\n")
        
        # 添加附录：关键信息汇总
        lines.append("\n## 附录：核心规则速览\n")
        
        # 汇总参赛要求
        reqs = []
        for s in all_content:
            for sec in s['sections']:
                if '参赛' in sec['heading'] or '对象' in sec['heading']:
                    reqs.append(sec['content'][:200] + "...")
        if reqs:
            lines.append("### 参赛要求摘要\n")
            lines.extend(reqs)
            lines.append("\n")
        
        return '\n'.join(lines)
    
    @staticmethod
    def generate_text(all_content: List[Dict]) -> str:
        """生成纯文本格式"""
        lines = []
        lines.append("=" * 60)
        lines.append("中国工业智能挑战赛竞赛规则".center(50))
        lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60 + "\n")
        
        for source in all_content:
            lines.append(f"\n【{source['title']}】")
            lines.append(f"来源：{source['source']}")
            lines.append(f"链接：{source['url']}")
            lines.append("-" * 40)
            
            for section in source['sections']:
                lines.append(f"\n■ {section['heading']}")
                lines.append(section['content'])
            lines.append("\n" + "=" * 60)
        
        return '\n'.join(lines)

# ==================== 主程序 ====================
def main():
    print("=" * 60)
    print("中国工业智能挑战赛规则爬虫")
    print("=" * 60)
    
    # 创建输出目录
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"已创建目录: {OUTPUT_DIR}")
    
    # 初始化爬虫并执行
    spider = CompetitionSpider()
    spider.crawl_all()
    
    if not spider.all_content:
        print("\n❌ 未能获取任何内容，请检查网络或URL可用性。")
        return
    
    # 生成Markdown
    md_content = OutputGenerator.generate_markdown(spider.all_content)
    md_file = os.path.join(OUTPUT_DIR, f"竞赛规则_{datetime.now().strftime('%Y%m%d')}.md")
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"\n✅ Markdown文件已保存: {md_file}")
    
    # 生成TXT
    txt_content = OutputGenerator.generate_text(spider.all_content)
    txt_file = os.path.join(OUTPUT_DIR, f"竞赛规则_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    print(f"✅ 文本文件已保存: {txt_file}")
    
    print("\n✨ 爬取完成！")

if __name__ == "__main__":
    main()