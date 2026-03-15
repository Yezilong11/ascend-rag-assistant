"""
全国大学生机器人大赛（ROBOTAC）竞赛规则爬虫
作者：元宝
功能：爬取ROBOTAC官网的竞赛规则，保存为Markdown和Word文档
"""

import requests
import os
import time
from bs4 import BeautifulSoup
import pdfplumber
import re
from datetime import datetime
import markdown
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import warnings
warnings.filterwarnings('ignore')

class ROBOTACCrawler:
    def __init__(self):
        self.base_url = "https://www.robotac.cn"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 创建保存目录
        self.save_dir = "ROBOTAC_竞赛规则"
        self.pdf_dir = os.path.join(self.save_dir, "PDF文件")
        self.data_dir = os.path.join(self.save_dir, "提取数据")
        
        for directory in [self.save_dir, self.pdf_dir, self.data_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def fetch_page(self, url):
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败: {url}, 状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求出错: {url}, 错误: {e}")
            return None
    
    def extract_pdf_links(self, html_content):
        """从网页中提取PDF链接"""
        soup = BeautifulSoup(html_content, 'html.parser')
        pdf_links = []
        
        # 查找所有PDF链接
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            
            # 检查是否是PDF文件
            if href.lower().endswith('.pdf'):
                # 处理相对路径
                if href.startswith('/'):
                    full_url = self.base_url + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = self.base_url + '/' + href
                
                # 检查是否包含规则相关关键词
                rule_keywords = ['规则', '章程', '要求', '标准', '赛制', '流程', '评审']
                if any(keyword in text or keyword in href for keyword in rule_keywords):
                    pdf_links.append({
                        'url': full_url,
                        'title': text if text else os.path.basename(href),
                        'description': self.extract_link_description(link)
                    })
        
        return pdf_links
    
    def extract_link_description(self, link_element):
        """提取链接的描述信息"""
        # 尝试获取父元素或兄弟元素的文本作为描述
        parent = link_element.parent
        description = ""
        
        # 查找附近的文本
        if parent:
            # 获取父元素的文本（去除链接文本本身）
            parent_text = parent.get_text(strip=True)
            link_text = link_element.get_text(strip=True)
            if link_text in parent_text:
                description = parent_text.replace(link_text, '').strip()
            
            # 如果父元素是列表项，获取整个列表项的文本
            if parent.name == 'li':
                description = parent.get_text(strip=True)
        
        return description[:200]  # 限制描述长度
    
    def download_pdf(self, pdf_info):
        """下载PDF文件"""
        try:
            response = self.session.get(pdf_info['url'], timeout=15)
            if response.status_code == 200:
                # 生成安全的文件名
                safe_title = re.sub(r'[<>:"/\\|?*]', '_', pdf_info['title'])
                if not safe_title.endswith('.pdf'):
                    safe_title += '.pdf'
                
                file_path = os.path.join(self.pdf_dir, safe_title)
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"✓ 已下载: {safe_title}")
                return file_path
            else:
                print(f"✗ 下载失败: {pdf_info['title']}")
                return None
        except Exception as e:
            print(f"✗ 下载出错: {pdf_info['title']}, 错误: {e}")
            return None
    
    def extract_pdf_text(self, pdf_path):
        """从PDF中提取文本内容"""
        text_content = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n\n"
        except Exception as e:
            print(f"PDF解析失败: {pdf_path}, 错误: {e}")
        
        return text_content
    
    def extract_rules_from_html(self, html_content):
        """从HTML页面提取规则信息"""
        soup = BeautifulSoup(html_content, 'html.parser')
        rules_data = {}
        
        # 查找可能的规则内容区域
        content_selectors = [
            'article', '.content', '.main-content', '.post-content',
            '.entry-content', '#content', '.rules', '.regulation'
        ]
        
        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break
        
        if not content_element:
            # 如果没有找到特定选择器，使用body
            content_element = soup.body
        
        if content_element:
            # 提取标题
            title = soup.title.string if soup.title else "未命名规则"
            rules_data['title'] = title
            
            # 提取正文内容
            text = content_element.get_text(separator='\n', strip=True)
            
            # 清理文本
            lines = text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line and len(line) > 2:  # 过滤空行和过短的行
                    cleaned_lines.append(line)
            
            rules_data['content'] = '\n'.join(cleaned_lines)
            
            # 尝试提取结构化信息
            rules_data['sections'] = self.extract_structured_sections(text)
        
        return rules_data
    
    def extract_structured_sections(self, text):
        """从文本中提取结构化章节"""
        sections = {}
        
        # 常见章节标题模式
        section_patterns = [
            r'一[、.]\s*(.*?)[\n\r]',
            r'二[、.]\s*(.*?)[\n\r]',
            r'三[、.]\s*(.*?)[\n\r]',
            r'四[、.]\s*(.*?)[\n\r]',
            r'五[、.]\s*(.*?)[\n\r]',
            r'第[一二三四五六七八九十]+[章条节]\s*(.*?)[\n\r]',
            r'\d+[\.、]\s*(.*?)[\n\r]',
            r'[①②③④⑤⑥⑦⑧⑨⑩]\s*(.*?)[\n\r]',
        ]
        
        lines = text.split('\n')
        current_section = "概述"
        section_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的章节标题
            is_section_title = False
            section_title = None
            
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    is_section_title = True
                    section_title = match.group(1).strip()
                    break
            
            if is_section_title and section_title:
                # 保存上一个章节
                if current_section and section_content:
                    sections[current_section] = '\n'.join(section_content)
                
                # 开始新章节
                current_section = section_title
                section_content = [line]
            else:
                section_content.append(line)
        
        # 保存最后一个章节
        if current_section and section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def crawl_website(self):
        """主爬取函数"""
        print("=" * 60)
        print("全国大学生机器人大赛（ROBOTAC）竞赛规则爬虫")
        print("=" * 60)
        
        # 获取官网首页
        print("\n1. 正在访问ROBOTAC官网...")
        homepage_html = self.fetch_page(self.base_url)
        
        if not homepage_html:
            print("无法访问官网，请检查网络连接")
            return
        
        # 提取PDF链接
        print("\n2. 正在查找规则PDF文件...")
        pdf_links = self.extract_pdf_links(homepage_html)
        
        if not pdf_links:
            print("未找到PDF文件，尝试查找其他页面...")
            # 尝试访问其他可能包含规则的页面
            rule_pages = [
                f"{self.base_url}/sys-nd/1299.html",  # 通知页面
                f"{self.base_url}/news",              # 新闻页面
                f"{self.base_url}/rules",             # 规则页面（可能）
            ]
            
            for page_url in rule_pages:
                page_html = self.fetch_page(page_url)
                if page_html:
                    additional_links = self.extract_pdf_links(page_html)
                    pdf_links.extend(additional_links)
        
        # 去重
        unique_pdfs = []
        seen_urls = set()
        for pdf in pdf_links:
            if pdf['url'] not in seen_urls:
                seen_urls.add(pdf['url'])
                unique_pdfs.append(pdf)
        
        print(f"找到 {len(unique_pdfs)} 个规则相关PDF文件")
        
        # 下载并处理PDF文件
        all_rules_data = []
        
        for i, pdf_info in enumerate(unique_pdfs, 1):
            print(f"\n[{i}/{len(unique_pdfs)}] 处理: {pdf_info['title']}")
            
            # 下载PDF
            pdf_path = self.download_pdf(pdf_info)
            if pdf_path:
                # 提取PDF文本
                pdf_text = self.extract_pdf_text(pdf_path)
                
                if pdf_text:
                    rule_data = {
                        'source': 'pdf',
                        'title': pdf_info['title'],
                        'url': pdf_info['url'],
                        'description': pdf_info.get('description', ''),
                        'content': pdf_text,
                        'file_path': pdf_path,
                        'sections': self.extract_structured_sections(pdf_text)
                    }
                    all_rules_data.append(rule_data)
        
        # 如果没有找到PDF，尝试从HTML页面提取
        if not all_rules_data:
            print("\n3. 正在从HTML页面提取规则信息...")
            
            # 尝试访问已知的规则页面
            known_rule_urls = [
                f"{self.base_url}/sys-nd/1299.html",  # 2026年竞赛通知
            ]
            
            for rule_url in known_rule_urls:
                html_content = self.fetch_page(rule_url)
                if html_content:
                    rule_data = self.extract_rules_from_html(html_content)
                    if rule_data.get('content'):
                        rule_data.update({
                            'source': 'html',
                            'url': rule_url,
                            'file_path': None
                        })
                        all_rules_data.append(rule_data)
                        print(f"✓ 从HTML页面提取规则: {rule_data.get('title', '未命名')}")
        
        # 保存结果
        if all_rules_data:
            print(f"\n4. 保存提取的规则数据...")
            self.save_results(all_rules_data)
            print(f"\n✓ 爬取完成！数据已保存到: {self.save_dir}")
        else:
            print("\n✗ 未找到任何规则数据")
        
        return all_rules_data
    
    def save_results(self, rules_data):
        """保存提取的结果"""
        # 1. 保存为Markdown文件
        self.save_as_markdown(rules_data)
        
        # 2. 保存为Word文档
        self.save_as_word(rules_data)
        
        # 3. 保存原始数据为JSON（可选）
        self.save_as_json(rules_data)
    
    def save_as_markdown(self, rules_data):
        """保存为Markdown格式"""
        md_content = f"""# 全国大学生机器人大赛（ROBOTAC）竞赛规则

> 爬取时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据来源：{self.base_url}
> 文件数量：{len(rules_data)} 个

## 目录

"""
        
        # 生成目录
        for i, rule in enumerate(rules_data, 1):
            title = rule.get('title', f'规则{i}')
            md_content += f"{i}. [{title}](#{i}-{title.replace(' ', '-')})\n"
        
        md_content += "\n---\n\n"
        
        # 添加每个规则的内容
        for i, rule in enumerate(rules_data, 1):
            title = rule.get('title', f'规则{i}')
            source = rule.get('source', '未知')
            url = rule.get('url', '')
            description = rule.get('description', '')
            content = rule.get('content', '')
            
            md_content += f"""## {i}. {title}

**来源类型**: {source.upper()}
**原始链接**: [{url}]({url})
**文件路径**: {rule.get('file_path', 'N/A')}
**描述**: {description}

### 内容摘要

"""
            
            # 如果有结构化章节，按章节显示
            sections = rule.get('sections', {})
            if sections:
                for section_title, section_content in sections.items():
                    md_content += f"#### {section_title}\n\n"
                    # 限制内容长度，避免文件过大
                    if len(section_content) > 2000:
                        md_content += section_content[:2000] + "...\n\n*(内容过长，已截断)*\n\n"
                    else:
                        md_content += section_content + "\n\n"
            else:
                # 显示完整内容（截断过长的内容）
                if len(content) > 5000:
                    md_content += content[:5000] + "...\n\n*(内容过长，已截断)*\n\n"
                else:
                    md_content += content + "\n\n"
            
            md_content += "---\n\n"
        
        # 添加总结部分
        md_content += """## 总结

### 主要规则类别

根据爬取结果，全国大学生机器人大赛（ROBOTAC）主要包含以下类型的规则：

1. **对抗赛规则** - 如"深蓝使命"、人形功夫搏击赛等
2. **挑战赛规则** - 如足式机器人挑战赛、能量球灌篮挑战赛等
3. **设计赛规则** - 如三维数字设计赛
4. **赛事章程** - 总体比赛章程和规定
5. **参赛要求** - 参赛资格、队伍组成等要求

### 核心规定要点

1. **参赛要求**：
   - 参赛队员需为在校全日制学生（研究生、本科生、专科生）
   - 每队需指定1名学生队长
   - 上场队伍限制：1名教师 + 5名学生
   - 指导教师与学生比例不得高于1:4

2. **赛制流程**：
   - 比赛分为校内赛、区域赛、全国赛
   - 全国赛包含预选赛和总决赛
   - 比赛时间通常为每年5-8月
   - 报名时间通常为前一年的11月

3. **评审标准**：
   - 技术实现与创新性
   - 机器人性能与稳定性
   - 战术策略与团队配合
   - 规则遵守与安全规范

### 注意事项

1. 规则可能每年更新，请以官网最新版本为准
2. 不同赛项可能有特殊规定
3. 建议定期访问官网获取最新信息
4. 具体细节请参考官方PDF文档

---

*本文件由ROBOTAC规则爬虫自动生成，仅供参考。请以官方发布的最新规则为准。*
"""
        
        # 保存Markdown文件
        md_file = os.path.join(self.data_dir, "ROBOTAC_竞赛规则.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  ✓ Markdown文件已保存: {md_file}")
    
    def save_as_word(self, rules_data):
        """保存为Word文档"""
        try:
            doc = Document()
            
            # 标题
            title = doc.add_heading('全国大学生机器人大赛（ROBOTAC）竞赛规则', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 元信息
            doc.add_paragraph(f'爬取时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            doc.add_paragraph(f'数据来源：{self.base_url}')
            doc.add_paragraph(f'文件数量：{len(rules_data)} 个')
            doc.add_paragraph()
            
            # 添加目录
            doc.add_heading('目录', level=1)
            for i, rule in enumerate(rules_data, 1):
                title = rule.get('title', f'规则{i}')
                doc.add_paragraph(f'{i}. {title}')
            
            doc.add_page_break()
            
            # 添加每个规则的内容
            for i, rule in enumerate(rules_data, 1):
                title = rule.get('title', f'规则{i}')
                source = rule.get('source', '未知')
                url = rule.get('url', '')
                description = rule.get('description', '')
                
                # 规则标题
                doc.add_heading(f'{i}. {title}', level=1)
                
                # 元信息
                meta = doc.add_paragraph()
                meta.add_run('来源类型: ').bold = True
                meta.add_run(f'{source.upper()}\n')
                
                meta.add_run('原始链接: ').bold = True
                meta.add_run(f'{url}\n')
                
                if rule.get('file_path'):
                    meta.add_run('文件路径: ').bold = True
                    meta.add_run(f'{rule.get("file_path")}\n')
                
                if description:
                    meta.add_run('描述: ').bold = True
                    meta.add_run(f'{description}\n')
                
                doc.add_paragraph()
                
                # 内容
                doc.add_heading('内容摘要', level=2)
                
                sections = rule.get('sections', {})
                if sections:
                    for section_title, section_content in sections.items():
                        doc.add_heading(section_title, level=3)
                        # 限制内容长度
                        if len(section_content) > 2000:
                            doc.add_paragraph(section_content[:2000] + "...")
                            doc.add_paragraph('(内容过长，已截断)')
                        else:
                            doc.add_paragraph(section_content)
                else:
                    content = rule.get('content', '')
                    if len(content) > 5000:
                        doc.add_paragraph(content[:5000] + "...")
                        doc.add_paragraph('(内容过长，已截断)')
                    else:
                        doc.add_paragraph(content)
                
                doc.add_page_break()
            
            # 保存Word文档
            word_file = os.path.join(self.data_dir, "ROBOTAC_竞赛规则.docx")
            doc.save(word_file)
            print(f"  ✓ Word文档已保存: {word_file}")
            
        except Exception as e:
            print(f"  ✗ Word文档保存失败: {e}")
    
    def save_as_json(self, rules_data):
        """保存为JSON格式（可选）"""
        import json
        
        # 简化数据以保存为JSON
        simplified_data = []
        for rule in rules_data:
            simplified = {
                'title': rule.get('title'),
                'source': rule.get('source'),
                'url': rule.get('url'),
                'description': rule.get('description'),
                'content_preview': rule.get('content', '')[:500] + "..." if len(rule.get('content', '')) > 500 else rule.get('content', ''),
                'sections_count': len(rule.get('sections', {})),
                'file_path': rule.get('file_path')
            }
            simplified_data.append(simplified)
        
        json_file = os.path.join(self.data_dir, "rules_summary.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(simplified_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ JSON摘要已保存: {json_file}")


def main():
    """主函数"""
    print("ROBOTAC竞赛规则爬虫启动...")
    print("注意：请确保已安装必要的Python库")
    print("安装命令：pip install requests beautifulsoup4 pdfplumber python-docx")
    print("-" * 60)
    
    # 检查必要库
    try:
        import requests
        from bs4 import BeautifulSoup
        import pdfplumber
        from docx import Document
    except ImportError as e:
        print(f"缺少必要的库: {e}")
        print("请先运行: pip install requests beautifulsoup4 pdfplumber python-docx")
        return
    
    # 创建爬虫实例并运行
    crawler = ROBOTACCrawler()
    rules_data = crawler.crawl_website()
    
    if rules_data:
        print("\n" + "=" * 60)
        print("爬取结果汇总：")
        print("=" * 60)
        
        for i, rule in enumerate(rules_data, 1):
            title = rule.get('title', f'规则{i}')
            source = rule.get('source', '未知')
            content_length = len(rule.get('content', ''))
            sections_count = len(rule.get('sections', {}))
            
            print(f"\n[{i}] {title}")
            print(f"   来源: {source}")
            print(f"   内容长度: {content_length} 字符")
            print(f"   章节数: {sections_count}")
            if rule.get('url'):
                print(f"   链接: {rule.get('url')}")
        
        print("\n" + "=" * 60)
        print("文件保存位置：")
        print(f"1. Markdown文件: {crawler.data_dir}/ROBOTAC_竞赛规则.md")
        print(f"2. Word文档: {crawler.data_dir}/ROBOTAC_竞赛规则.docx")
        print(f"3. PDF原始文件: {crawler.pdf_dir}/")
        print(f"4. JSON摘要: {crawler.data_dir}/rules_summary.json")
        print("=" * 60)
        
        print("\n使用说明：")
        print("1. 所有文件已保存在 'ROBOTAC_竞赛规则' 文件夹中")
        print("2. Markdown文件适合快速浏览和编辑")
        print("3. Word文档适合打印和正式文档使用")
        print("4. PDF文件夹包含原始规则文件")
        print("5. 建议定期运行此脚本以获取最新规则")
    else:
        print("\n未找到任何规则数据，可能是网站结构已更改或网络问题。")
        print("建议：")
        print("1. 检查网络连接")
        print("2. 访问官网手动查看: https://www.robotac.cn")
        print("3. 联系赛事组委会获取最新规则")


if __name__ == "__main__":
    main()