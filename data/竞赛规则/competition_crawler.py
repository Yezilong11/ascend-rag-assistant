"""
哈尔滨工业大学本科生科技竞赛规则爬虫（修复版）
功能：自动爬取Word文档中所有竞赛的详细规则信息
输出：Markdown格式文档，包含参赛要求、赛制流程、评审标准等
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
import time
from urllib.parse import urljoin, urlparse
from docx import Document
from datetime import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('competition_crawler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CompetitionRuleCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
        self.session = requests.Session()
        self.results = []
        self.output_dir = "competition_rules"
        
        # 创建输出目录
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
        # 定义关键词库用于识别不同板块
        self.keywords = {
            '参赛要求': ['参赛对象', '参赛资格', '报名条件', '组队要求', '参赛人员', '学历要求', '年龄限制', '专业要求', '参赛团队', '参赛学生'],
            '赛制流程': ['赛制', '赛程', '比赛流程', '时间安排', '阶段', '初赛', '复赛', '决赛', '报名', '提交', '日程', '时间'],
            '评审标准': ['评审', '评分', '评分标准', '评分细则', '评价指标', '打分', '奖项设置', '获奖比例', '评审委员会', '评委'],
            '作品要求': ['作品要求', '提交材料', '格式要求', '内容要求', '技术规范', '查重要求', '作品提交', '作品形式'],
            '违规处理': ['违规', '作弊', '学术不端', '纪律', '处罚', '取消资格', '诚信', '侵权']
        }

    def extract_competitions_from_docx(self, docx_path):
        """从Word文档中提取竞赛名称和官网链接（修复版）"""
        try:
            doc = Document(docx_path)
        except Exception as e:
            logger.error(f"无法打开Word文档: {e}")
            return []
            
        competitions = []
        
        # 提取所有段落文本并合并
        full_text = '\n'.join([para.text.strip() for para in doc.paragraphs if para.text.strip()])
        
        # 按行分割处理
        lines = full_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 匹配模式：数字. **竞赛名称**：[URL](URL) 备注
            # 或者：**竞赛名称**：[URL](URL)
            pattern = r'(?:\d+\.\s*)?\*\*([^*]+)\*\*[：:]\s*(.+?)(?:\n|$)'
            match = re.search(pattern, line)
            
            if match:
                name = match.group(1).strip()
                rest = match.group(2).strip()
                
                # 提取所有URL
                urls = re.findall(r'https?://[^\s\)\]\$]+', rest)
                # 清理URL（去除可能的尾随符号）
                urls = [url.rstrip('.,;)]') for url in urls]
                
                # 提取备注（括号内的内容或"注："后的内容）
                notes = ""
                note_match = re.search(r'[（(]([^)]+)[）)]', line)
                if note_match:
                    notes = note_match.group(1)
                if '注：' in line or '注:' in line:
                    notes += " " + re.search(r'注[：:](.+?)(?:\n|$)', line).group(1) if re.search(r'注[：:](.+?)(?:\n|$)', line) else ""
                
                if name and urls:  # 只有有名称和URL才添加
                    competitions.append({
                        'name': name,
                        'urls': urls,
                        'notes': notes.strip()
                    })
                    logger.debug(f"提取到竞赛: {name}, URLs: {urls}")
        
        logger.info(f"从文档中提取了 {len(competitions)} 个竞赛")
        return competitions

    def fetch_page(self, url, retries=3):
        """获取页面内容，带重试机制"""
        # 清理URL
        url = url.strip()
        if not url.startswith('http'):
            return None
            
        for i in range(retries):
            try:
                response = self.session.get(url, headers=self.headers, timeout=15, allow_redirects=True)
                response.encoding = response.apparent_encoding
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"HTTP {response.status_code}: {url}")
            except Exception as e:
                logger.error(f"请求失败 ({i+1}/{retries}): {url}, 错误: {str(e)}")
                time.sleep(2)
        return None

    def extract_rules_from_soup(self, soup, url):
        """
        从BeautifulSoup对象中提取规则信息
        """
        rules = {
            '参赛要求': [],
            '赛制流程': [],
            '评审标准': [],
            '作品要求': [],
            '违规处理': [],
            '其他重要信息': []
        }
        
        # 清理文本函数
        def clean_text(text):
            text = ' '.join(text.split())
            return text.strip()
        
        # 策略1：查找所有段落和列表项
        elements = soup.find_all(['p', 'li', 'div', 'span', 'td', 'h1', 'h2', 'h3', 'h4', 'h5'])
        
        for elem in elements:
            text = clean_text(elem.get_text())
            if len(text) < 10 or len(text) > 300:  # 过滤太短或太长的
                continue
            
            # 检查是否包含关键词
            matched = False
            for category, keywords in self.keywords.items():
                if any(keyword in text for keyword in keywords):
                    if text not in rules[category]:
                        rules[category].append(text)
                    matched = True
                    break
            
            # 如果没匹配到，但包含规则性词汇，放入其他
            if not matched and any(kw in text for kw in ['必须', '应当', '禁止', '不得', '要求', '规定', '注意']):
                if text not in rules['其他重要信息']:
                    rules['其他重要信息'].append(text)
        
        # 策略2：专门提取表格内容
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if cells:
                    row_text = ' | '.join([clean_text(cell.get_text()) for cell in cells if clean_text(cell.get_text())])
                    if 10 < len(row_text) < 200:
                        for category, keywords in self.keywords.items():
                            if any(keyword in row_text for keyword in keywords):
                                if row_text not in rules[category]:
                                    rules[category].append(f"[表格] {row_text}")
                                break
        
        # 去重和限制数量
        for key in rules:
            seen = set()
            unique_items = []
            for item in rules[key]:
                item_key = item[:40]  # 前40字符作为去重键
                if item_key not in seen and len(item) > 10:
                    seen.add(item_key)
                    unique_items.append(item)
            rules[key] = unique_items[:8]  # 每类最多8条
            
        return rules

    def crawl_competition(self, comp_info):
        """爬取单个竞赛的规则信息"""
        name = comp_info['name']
        urls = comp_info['urls']
        notes = comp_info['notes']
        
        logger.info(f"开始爬取: {name}")
        
        result = {
            'name': name,
            'source_urls': urls,
            'notes': notes,
            'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'rules': {},
            'status': 'failed',
            'error': ''
        }
        
        all_rules = {
            '参赛要求': [],
            '赛制流程': [],
            '评审标准': [],
            '作品要求': [],
            '违规处理': [],
            '其他重要信息': []
        }
        
        # 尝试所有提供的URL
        for url in urls:
            # 排除明显不是官网的链接
            if any(x in url for x in ['weixin', 'mp.weixin', 'baike.baidu', 'wenwen.sogou', 'zhihu.com']):
                continue
                
            html = self.fetch_page(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                rules = self.extract_rules_from_soup(soup, url)
                
                # 合并结果
                for key in all_rules:
                    all_rules[key].extend(rules[key])
                
                result['status'] = 'success'
                logger.info(f"成功获取 {name} 的规则信息 from {url}")
                
                # 如果获取到足够信息，不再尝试其他URL
                total_items = sum(len(v) for v in all_rules.values())
                if total_items > 3:
                    break
                    
            time.sleep(1.5)  # 礼貌延迟
        
        # 最终去重
        for key in all_rules:
            seen = set()
            unique = []
            for item in all_rules[key]:
                item_key = item[:35]
                if item_key not in seen:
                    seen.add(item_key)
                    unique.append(item)
            all_rules[key] = unique[:10]
            
        result['rules'] = all_rules
        
        if result['status'] == 'failed':
            result['error'] = '无法访问任何提供的URL或URL无效'
            
        return result

    def generate_markdown(self, result):
        """生成Markdown格式的报告"""
        md_content = f"""# {result['name']}

## 基本信息
- **竞赛名称**: {result['name']}
- **爬取时间**: {result['crawl_time']}
- **数据来源**: {', '.join(result['source_urls']) if result['source_urls'] else '未获取到官网链接'}

"""
        
        if result['notes']:
            md_content += f"""## 备注信息
{result['notes']}

"""
        
        if result['status'] == 'failed':
            md_content += f"""## ⚠️ 爬取状态
**爬取失败**: {result['error']}

### 建议访问的官网链接
"""
            for url in result['source_urls']:
                md_content += f"- [{url}]({url})\n"
            return md_content
        
        # 添加各板块内容
        sections = ['参赛要求', '赛制流程', '评审标准', '作品要求', '违规处理', '其他重要信息']
        
        for section in sections:
            items = result['rules'].get(section, [])
            if items:
                md_content += f"""## {section}

"""
                for i, item in enumerate(items, 1):
                    # 清理markdown特殊字符
                    item_clean = item.replace('|', '\\|').replace('#', '\\#').replace('*', '\\*')
                    md_content += f"{i}. {item_clean}\\n"
                md_content += "\\n"
        
        # 添加原始链接
        md_content += f"""## 参考链接
"""
        for url in result['source_urls']:
            md_content += f"- [官网链接]({url})\\n"
            
        return md_content

    def save_to_markdown(self, result):
        """保存单个竞赛结果到Markdown文件"""
        # 生成合法文件名
        safe_name = re.sub(r'[\\\\/:*?"<>|]', '_', result['name'])
        safe_name = safe_name[:50]  # 限制长度
        filename = os.path.join(self.output_dir, f"{safe_name}.md")
        
        md_content = self.generate_markdown(result)
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            logger.info(f"已保存: {filename}")
            return filename
        except Exception as e:
            logger.error(f"保存文件失败 {filename}: {e}")
            return None

    def generate_summary(self, all_results):
        """生成汇总文档"""
        if not all_results:
            logger.warning("没有结果可汇总")
            return
            
        success_list = [r for r in all_results if r['status'] == 'success']
        failed_list = [r for r in all_results if r['status'] == 'failed']
        
        summary = f"""# 哈尔滨工业大学本科生科技竞赛规则汇总

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 数据来源: 大赛官网（初版）.docx
> 爬取竞赛数: {len(all_results)}

## 统计信息

| 类别 | 数量 |
|------|------|
| 总竞赛数 | {len(all_results)} |
| 成功爬取 | {len(success_list)} |
| 需要手动补充 | {len(failed_list)} |
| 成功率 | {len(success_list)/len(all_results)*100:.1f}% |

## 目录

### ✅ 成功爬取 ({len(success_list)}项)

"""
        for r in success_list:
            safe_name = re.sub(r'[\\\\/:*?"<>|]', '_', r['name'])[:50]
            summary += f"- [{r['name']}](./{safe_name}.md)\\n"
            
        summary += f"""

### ⚠️ 需要手动补充 ({len(failed_list)}项)

"""
        for r in failed_list:
            summary += f"- **{r['name']}**: "
            if r['source_urls']:
                summary += f"[官网链接]({r['source_urls'][0]})\\n"
            else:
                summary += "暂无官网链接\\n"
        
        summary += """

## 使用说明

1. **文件结构**: 每个竞赛独立一个Markdown文件，包含详细的参赛要求、赛制流程、评审标准等
2. **补充完善**: 对于爬取失败的竞赛，建议直接访问官网链接手动整理规则信息
3. **更新维护**: 建议定期重新运行爬虫以获取最新规则

## 注意事项

- 爬取内容仅供参考，请以各竞赛官网最新公布信息为准
- 部分竞赛规则可能随年份调整，报名前请仔细核对当年最新通知
- 涉及资格审查、奖项设置等关键信息，务必以官方文件为准

"""
        
        try:
            with open(os.path.join(self.output_dir, "README.md"), 'w', encoding='utf-8') as f:
                f.write(summary)
            logger.info("已生成汇总文档: README.md")
        except Exception as e:
            logger.error(f"生成汇总文档失败: {e}")

    def run(self, docx_path):
        """主运行流程"""
        logger.info("="*60)
        logger.info("开始爬取竞赛规则")
        logger.info("="*60)
        
        # 1. 从Word提取竞赛列表
        competitions = self.extract_competitions_from_docx(docx_path)
        
        if not competitions:
            logger.error("未能从文档中提取到任何竞赛信息，请检查文档格式")
            return []
        
        # 2. 爬取每个竞赛的规则
        all_results = []
        total = len(competitions)
        
        for i, comp in enumerate(competitions, 1):
            logger.info(f"\\n[{i}/{total}] 处理: {comp['name']}")
            try:
                result = self.crawl_competition(comp)
                all_results.append(result)
                self.save_to_markdown(result)
            except Exception as e:
                logger.error(f"处理 {comp['name']} 时出错: {e}")
                all_results.append({
                    'name': comp['name'],
                    'source_urls': comp['urls'],
                    'notes': comp['notes'],
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'rules': {},
                    'status': 'failed',
                    'error': str(e)
                })
            
            time.sleep(2)  # 避免请求过快
            
        # 3. 生成汇总文档
        self.generate_summary(all_results)
        
        logger.info("\\n" + "="*60)
        logger.info("爬取完成!")
        logger.info(f"结果保存在: {os.path.abspath(self.output_dir)}")
        logger.info(f"总计: {len(all_results)} 个竞赛")
        logger.info(f"成功: {len([r for r in all_results if r['status'] == 'success'])} 个")
        logger.info("="*60)
        
        return all_results


# 主程序入口
if __name__ == "__main__":
    import sys
    
    # 配置文件路径 - 支持命令行参数或自动查找
    if len(sys.argv) > 1:
        DOCX_FILE = sys.argv[1]
    else:
        # 尝试多个可能的路径
        possible_paths = [
            "大赛官网（初版）.docx",
            "./大赛官网（初版）.docx",
            "../大赛官网（初版）.docx",
            "/mnt/kimi/upload/大赛官网（初版）.docx",
            "sample_competitions.docx"
        ]
        
        DOCX_FILE = None
        for path in possible_paths:
            if os.path.exists(path):
                DOCX_FILE = path
                print(f"找到文件: {path}")
                break
        
        if not DOCX_FILE:
            print("错误: 未找到Word文档，请确保文件在以下位置之一:")
            for path in possible_paths[:-1]:
                print(f"  - {path}")
            print("\\n或者通过命令行指定路径: python competition_crawler.py <文件路径>")
            sys.exit(1)
    
    # 运行爬虫
    crawler = CompetitionRuleCrawler()
    results = crawler.run(DOCX_FILE)
    
    print(f"\\n✅ 爬取完成！共处理 {len(results)} 个竞赛")
    print(f"📁 结果保存在: {os.path.abspath(crawler.output_dir)}")
    print("\\n文件结构:")
    print(f"  {crawler.output_dir}/")
    print("    ├── README.md          # 汇总目录")
    print("    ├── 竞赛名称1.md       # 单个竞赛规则")
    print("    └── ...")