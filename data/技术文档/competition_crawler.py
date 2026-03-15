"""
22个指定竞赛技术文档爬虫
功能：爬取用户指定的22个竞赛官网的技术文档
保存格式：Markdown + 原始HTML
"""

import os
import re
import json
import time
import random
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import html2text

class CompetitionDocCrawler:
    def __init__(self, output_dir="competition_docs_22"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 创建子目录
        self.markdown_dir = self.output_dir / "markdown"
        self.raw_dir = self.output_dir / "raw_html"
        self.metadata_file = self.output_dir / "metadata.json"
        
        self.markdown_dir.mkdir(exist_ok=True)
        self.raw_dir.mkdir(exist_ok=True)
        
        # HTML转Markdown转换器配置
        self.html2text_converter = html2text.HTML2Text()
        self.html2text_converter.ignore_links = False
        self.html2text_converter.ignore_images = False
        self.html2text_converter.body_width = 0
        
        # 请求头配置
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 设置超时和重试
        self.session.mount('http://', requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
            )
        ))
        self.session.mount('https://', requests.adapters.HTTPAdapter(
            max_retries=requests.adapters.Retry(
                total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504]
            )
        ))
        
        # 22个竞赛的配置信息（基于搜索结果整理）
        self.competitions = [
            {
                "name": "iCAN大学生创新创业大赛",
                "url": "http://www.g-ican.com/",
                "keywords": ["创新", "创业", "物联网", "赛道", "报名", "规则", "通知", "资料"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide"]
            },
            {
                "name": "中美青年创客大赛",
                "url": "https://chinaus-maker.cscse.edu.cn/",
                "keywords": ["创客", "中美", "共创未来", "报名", "规则", "章程", "通知", "资料下载"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/bmcs"]
            },
            {
                "name": "中国工业智能挑战赛",
                "url": "http://www.dllgt.com/newsinfo/1891945.html",
                "keywords": ["工业智能", "智能制造", "罗克韦尔", "AB杯", "规则", "赛题", "资料"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/newsinfo"]
            },
            {
                "name": "中国(国际)传感器创新创业大赛",
                "url": "http://www.g-ican.com/",  # 与iCAN同官网
                "keywords": ["传感器", "MEMS", "创新", "创业", "报名", "规则"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide"]
            },
            {
                "name": "中国大学生物理学术竞赛(CUPT)",
                "url": "https://www.cupt-iypt.com/",
                "keywords": ["物理", "学术", "CUPT", "IYPT", "赛题", "规则", "通知", "资料"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/problem"]
            },
            {
                "name": "全国大学生数学竞赛",
                "url": "https://www.cmathc.org.cn/",
                "keywords": ["数学", "竞赛", "报名", "通知", "规则", "考试大纲", "样题"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/tz"]
            },
            {
                "name": "UIA霍普杯国际大学生建筑设计竞赛",
                "url": "http://hypcup.uedmagazine.net/",  # 年度变化，需确认最新
                "keywords": ["UIA", "霍普杯", "建筑", "设计", "竞赛题目", "报名", "规则"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/competition"]
            },
            {
                "name": "天作奖国际大学生建筑设计竞赛",
                "url": "http://www.architectsjournal.cn/",  # 《建筑师》杂志官网
                "keywords": ["天作奖", "建筑", "设计", "竞赛", "题目", "报名", "规则"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/competition"]
            },
            {
                "name": "东南·中国建筑新人赛",
                "url": "http://www.archirookies.com/",
                "keywords": ["东南", "建筑", "新人赛", "设计", "报名", "规则", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide"]
            },
            {
                "name": "城市设计学生作业国际竞赛",
                "url": "http://www.wupen.org/",
                "keywords": ["城市设计", "WUPEN", "学生作业", "报名", "规则", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/competition"]
            },
            {
                "name": "城市可持续调研报告国际竞赛",
                "url": "http://www.wupen.org/",
                "keywords": ["城市可持续", "调研报告", "WUPEN", "报名", "规则", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/competition"]
            },
            {
                "name": "中国风景园林学会大学生设计竞赛",
                "url": "https://www.chsla.org.cn/",
                "keywords": ["风景园林", "CHSLA", "设计", "竞赛", "报名", "规则", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/article"]
            },
            {
                "name": "IFLA国际大学生设计竞赛",
                "url": "https://www.iflaworld.org/",
                "keywords": ["IFLA", "景观", "设计", "国际", "竞赛", "报名", "规则"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/competition"]
            },
            {
                "name": "新人杯全国大学生室内设计竞赛",
                "url": "http://www.ciid.com.cn/",
                "keywords": ["新人杯", "室内", "设计", "CIID", "竞赛", "报名", "规则", "章程"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/news"]
            },
            {
                "name": "全国大学生混凝土材料设计大赛",
                "url": "https://www.ccpa.com.cn/",  # 中国混凝土与水泥制品协会
                "keywords": ["混凝土", "材料", "设计", "CCPA", "竞赛", "报名", "规则"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/education"]
            },
            {
                "name": "全国大学生交通运输科技大赛",
                "url": "http://www.nactrans.com.cn/",  # 需确认
                "keywords": ["交通运输", "科技", "竞赛", "报名", "规则", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide"]
            },
            {
                "name": "全国大学生软件创新大赛",
                "url": "https://www.swcontest.com.cn/",
                "keywords": ["软件", "创新", "竞赛", "报名", "规则", "通知", "赛题"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/information"]
            },
            {
                "name": "全国大学生英语竞赛(NECCS)",
                "url": "http://www.chinaneccs.cn/",
                "keywords": ["英语", "NECCS", "竞赛", "报名", "规则", "样题", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/sample"]
            },
            {
                "name": "全国英语口译大赛",
                "url": "http://www.lscat.cn/",
                "keywords": ["口译", "LSCAT", "翻译", "竞赛", "报名", "规则", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/match"]
            },
            {
                "name": "外研社国才杯全国大学生英语辩论赛",
                "url": "http://uchallenge.unipus.cn/",
                "keywords": ["外研社", "国才杯", "英语", "辩论", "报名", "规则", "通知"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/debate"]
            },
            {
                "name": "全国大学生职业规划大赛",
                "url": "https://zgs.chsi.com.cn/",
                "keywords": ["职业规划", "就业", "chsi", "报名", "规则", "通知", "赛道"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/home"]
            },
            {
                "name": "全国海洋航行器设计与制作大赛",
                "url": "http://www.cssc.com.cn/",  # 中国船舶集团，需确认具体页面
                "keywords": ["海洋", "航行器", "船舶", "设计", "竞赛", "报名", "规则"],
                "doc_patterns": ["/doc", "/download", "/notice", "/rule", "/guide", "/contest"]
            }
        ]
        
        self.results = []
        self.failed = []
        
    def safe_filename(self, name):
        """生成安全的文件名"""
        return re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')[:50]
    
    def crawl_page(self, url, competition_name, depth=0, max_depth=2):
        """递归爬取页面"""
        if depth > max_depth:
            return []
        
        try:
            print(f"   [{'→' * (depth+1)}] 爬取: {url[:60]}...")
            
            # 随机延迟，避免被封
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=20, allow_redirects=True)
            response.encoding = response.apparent_encoding or 'utf-8'
            
            # 检查内容类型
            content_type = response.headers.get('content-type', '').lower()
            
            # 如果是文件下载，跳过处理
            if any(ext in url.lower() for ext in ['.pdf', '.doc', '.docx', '.zip', '.rar']):
                return [{
                    'url': url,
                    'type': 'file',
                    'filename': os.path.basename(urlparse(url).path),
                    'status': 'skipped_file'
                }]
            
            # 生成文件名
            parsed = urlparse(url)
            path_part = parsed.path.strip('/').replace('/', '_')[:30] or 'index'
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_comp_name = self.safe_filename(competition_name)
            
            filename_base = f"{safe_comp_name}_{path_part}_{timestamp}"
            
            # 保存原始HTML
            html_path = self.raw_dir / f"{filename_base}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # 转换为Markdown
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # 提取标题
            title = soup.find('title')
            title_text = title.get_text(strip=True) if title else competition_name
            
            # 提取主要内容
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content') or soup.find('body')
            
            if main_content:
                markdown_body = self.html2text_converter.handle(str(main_content))
            else:
                markdown_body = self.html2text_converter.handle(response.text)
            
            # 构建Markdown文档
            markdown_content = f"""---
title: {title_text}
competition: {competition_name}
source_url: {url}
crawled_at: {datetime.now().isoformat()}
depth: {depth}
---

# {title_text}

> **竞赛**: {competition_name}  
> **来源**: [{url}]({url})  
> **爬取时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

{markdown_body}

---
*文档由爬虫自动生成*
"""
            
            # 保存Markdown
            md_path = self.markdown_dir / f"{filename_base}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            result = {
                'url': url,
                'title': title_text,
                'html_file': str(html_path),
                'markdown_file': str(md_path),
                'status': 'success',
                'depth': depth
            }
            
            # 查找子链接（如果是首页或列表页）
            if depth < max_depth:
                sub_links = self.find_doc_links(soup, url, competition_name)
                for link in sub_links[:3]:  # 限制子页面数量
                    if link['url'] != url:  # 避免重复
                        sub_results = self.crawl_page(link['url'], competition_name, depth + 1, max_depth)
                        result.setdefault('sub_pages', []).extend(sub_results)
            
            return [result]
            
        except Exception as e:
            print(f"   ❌ 错误: {str(e)}")
            return [{
                'url': url,
                'status': 'failed',
                'error': str(e),
                'depth': depth
            }]
    
    def find_doc_links(self, soup, base_url, competition_name):
        """查找文档相关链接"""
        links = []
        comp_config = next((c for c in self.competitions if c['name'] == competition_name), None)
        
        if not comp_config:
            return links
        
        # 查找所有链接
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True).lower()
            
            # 构建完整URL
            full_url = urljoin(base_url, href)
            
            # 检查是否是外部链接
            if not self.is_same_domain(base_url, full_url):
                continue
            
            # 检查关键词匹配
            keywords = comp_config['keywords']
            patterns = comp_config['doc_patterns']
            
            is_match = any(kw in text for kw in keywords) or \
                      any(pat in href.lower() for pat in patterns) or \
                      any(kw in href.lower() for kw in keywords)
            
            if is_match and full_url not in [l['url'] for l in links]:
                links.append({
                    'url': full_url,
                    'text': a_tag.get_text(strip=True)[:50],
                    'type': 'keyword_match'
                })
        
        # 去重并限制数量
        seen = set()
        unique_links = []
        for link in links:
            if link['url'] not in seen:
                seen.add(link['url'])
                unique_links.append(link)
        
        return unique_links[:5]  # 最多返回5个相关链接
    
    def is_same_domain(self, url1, url2):
        """检查是否同一域名"""
        try:
            d1 = urlparse(url1).netloc
            d2 = urlparse(url2).netloc
            return d1 == d2 or d1 in d2 or d2 in d1
        except:
            return False
    
    def crawl_competition(self, comp):
        """爬取单个竞赛"""
        name = comp['name']
        url = comp['url']
        
        print(f"\n{'='*70}")
        print(f"🏆 开始爬取: {name}")
        print(f"🌐 官网: {url}")
        print(f"{'='*70}")
        
        try:
            results = self.crawl_page(url, name, depth=0, max_depth=2)
            success_count = sum(1 for r in results if r.get('status') == 'success')
            
            self.results.append({
                'name': name,
                'url': url,
                'status': 'completed',
                'pages_crawled': len(results),
                'success_count': success_count,
                'results': results
            })
            
            print(f"✅ 完成: {name} (成功 {success_count}/{len(results)} 页)")
            
        except Exception as e:
            print(f"❌ 失败: {name} - {str(e)}")
            self.failed.append({
                'name': name,
                'url': url,
                'error': str(e)
            })
            self.results.append({
                'name': name,
                'url': url,
                'status': 'failed',
                'error': str(e)
            })
    
    def generate_summary(self):
        """生成汇总报告"""
        summary_md = f"""# 22个竞赛技术文档爬取报告

> 生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 统计概览

| 项目 | 数量 |
|------|------|
| 总竞赛数 | 22 |
| 成功爬取 | {sum(1 for r in self.results if r['status'] == 'completed')} |
| 失败 | {len(self.failed)} |
| 总页面数 | {sum(r.get('pages_crawled', 0) for r in self.results)} |

## 📋 竞赛清单与文档索引

"""
        
        for i, comp in enumerate(self.competitions, 1):
            result = next((r for r in self.results if r['name'] == comp['name']), None)
            
            if result and result['status'] == 'completed':
                summary_md += f"\n### {i}. {comp['name']} ✅\n\n"
                summary_md += f"- **官网**: [{comp['url']}]({comp['url']})\n"
                summary_md += f"- **状态**: 成功\n"
                
                # 列出爬取的文件
                for page in result.get('results', []):
                    if page.get('status') == 'success':
                        rel_path = os.path.relpath(page['markdown_file'], self.output_dir)
                        summary_md += f"- 📄 [{page.get('title', '文档')}]({rel_path}) (来源: {page['url']})\n"
            else:
                summary_md += f"\n### {i}. {comp['name']} ❌\n\n"
                summary_md += f"- **官网**: [{comp['url']}]({comp['url']})\n"
                summary_md += f"- **状态**: 失败\n"
                if result and result.get('error'):
                    summary_md += f"- **错误**: {result['error']}\n"
        
        if self.failed:
            summary_md += "\n## ❌ 失败的竞赛\n\n"
            for item in self.failed:
                summary_md += f"- **{item['name']}**: {item['error']}\n"
        
        summary_md += """
## 📁 文件结构说明
competition_docs_22/
├── markdown/          # Markdown格式文档（推荐查看）
├── raw_html/          # 原始HTML备份
├── metadata.json      # 元数据
└── README.md          # 本文件

## 🔍 使用建议

1. **优先查看Markdown文件**: 位于 `markdown/` 目录，格式清晰，便于阅读
2. **原始HTML备份**: 位于 `raw_html/` 目录，保留完整网页样式
3. **文档命名规则**: `竞赛名_页面路径_时间戳.md`

## ⚠️ 注意事项

1. 部分竞赛网站可能需要校园网或特定网络环境访问
2. 部分网站使用JavaScript动态加载内容，本爬虫可能无法完全获取
3. 建议定期重新爬取以获取最新通知和规则更新
4. 所有文档仅供学习参考，请以官网最新发布为准

---
*报告由爬虫系统自动生成*
"""
        
        # 保存汇总文档
        readme_path = self.output_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(summary_md)
        
        print(f"\n📊 汇总报告已生成: {readme_path}")
        return readme_path
    
    def save_metadata(self):
        """保存元数据JSON"""
        metadata = {
            'crawl_time': datetime.now().isoformat(),
            'total_competitions': len(self.competitions),
            'completed': sum(1 for r in self.results if r['status'] == 'completed'),
            'failed': len(self.failed),
            'output_directory': str(self.output_dir),
            'competitions': self.results
        }
        
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"💾 元数据已保存: {self.metadata_file}")
    
    def run(self):
        """运行完整爬取流程"""
        print("🚀 开始爬取22个指定竞赛的技术文档...")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        # 爬取每个竞赛
        for i, comp in enumerate(self.competitions, 1):
            print(f"\n📌 进度: [{i}/{len(self.competitions)}]")
            self.crawl_competition(comp)
            
            # 每5个保存一次进度
            if i % 5 == 0:
                self.save_metadata()
                print(f"💾 进度已保存 ({i}/{len(self.competitions)})")
            
            # 竞赛间延迟，避免请求过快
            time.sleep(random.uniform(3, 5))
        
        # 生成报告
        self.generate_summary()
        self.save_metadata()
        
        print(f"\n{'='*70}")
        print("✅ 爬取完成!")
        print(f"📁 输出目录: {self.output_dir.absolute()}")
        print(f"📝 Markdown文档: {self.markdown_dir}")
        print(f"🌐 HTML备份: {self.raw_dir}")
        print(f"📊 汇总报告: {self.output_dir / 'README.md'}")
        print(f"⏰ 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}")


def main():
    # 创建爬虫实例
    crawler = CompetitionDocCrawler(output_dir="competition_docs_22")
    
    # 运行爬虫
    try:
        crawler.run()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断，保存当前进度...")
        crawler.save_metadata()
        print("进度已保存，可随时重新运行继续爬取")


if __name__ == "__main__":
    main()