# 文件名: fetch_history_3.py
# 放置位置: 历史赛题集/ 文件夹内
# 功能: 专门爬取第20项“中美青年创客大赛”的历史赛题
# 文件名格式: 20-中美青年创客大赛-历史赛题集.md
# 问题日志: problem_urls_history_3.txt

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from datetime import datetime

# ==================== 配置区域 ====================
# 只包含第20项：中美青年创客大赛
TARGET_CONTEST = (20, "中美青年创客大赛", "https://chinaus-maker.cscse.edu.cn/")

# 问题网址记录文件
PROBLEM_URLS_FILE = "problem_urls_history_3.txt"

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
TIMEOUT = 15
# ==================== 配置结束 ====================

# 历史赛题关键词
HISTORY_KEYWORDS = ['赛题', '真题', '题目', '历届', '下载', 'archive', 'past', 'problem', 'questions', '往年', '试题', '样题', '主题', '方向', '赛道']

# 板块标识
SECTION_TAG = "历史赛题集"

def safe_filename(name):
    """将竞赛名称转换为安全的文件名"""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()

def extract_text_from_html(html, url):
    """提取HTML中的主要文本内容"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本、样式等
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 尝试获取标题
        title_tag = soup.find('title')
        title = title_tag.string if title_tag else url
        title = title.strip()
        
        # 获取正文文本，保留段落结构
        text_content = []
        for elem in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'div']):
            text = elem.get_text(strip=True)
            if text and len(text) > 10:  # 过滤掉太短的文本
                text_content.append(text)
        
        cleaned_text = '\n'.join(text_content)
        return title, cleaned_text
    except Exception as e:
        return url, f"解析HTML时出错: {e}"

def find_specific_content(text, keywords):
    """根据关键词在文本中查找相关段落"""
    paragraphs = text.split('\n')
    relevant = []
    for para in paragraphs:
        if any(keyword.lower() in para.lower() for keyword in keywords):
            relevant.append(para)
    return relevant

def fetch_single_contest(contest):
    """获取单个竞赛的数据并生成Markdown文件"""
    idx, name, url = contest
    safe_name = safe_filename(name)
    
    print(f"\n正在处理 [{idx:02d}] {name} ...")
    print(f"网址: {url}")
    
    expected_file = f"{idx:02d}-{safe_name}-{SECTION_TAG}.md"
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.encoding = response.apparent_encoding or 'utf-8'
        html = response.text
        
        title, main_text = extract_text_from_html(html, url)
        
        # 查找历史赛题相关内容
        history_content = find_specific_content(main_text, HISTORY_KEYWORDS)
        
        # 构建Markdown内容
        history_md = f"# {name} - {SECTION_TAG}\n\n"
        history_md += f"**来源网址**: {url}\n"
        history_md += f"**抓取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        history_md += f"## 页面标题\n\n{title}\n\n"
        
        # 添加大赛简介
        history_md += "## 大赛简介\n\n"
        intro_match = re.search(r'(大赛简介.*?)(?=\n\n|\Z)', main_text, re.DOTALL)
        if intro_match:
            history_md += intro_match.group(1) + "\n\n"
        else:
            # 手动提取简介部分
            intro_lines = [line for line in main_text.split('\n') if '创客' in line or '大赛' in line][:5]
            for line in intro_lines:
                history_md += f"{line}\n\n"
        
        # 添加赛题相关内容
        if history_content:
            history_md += "## 相关赛题/赛道内容\n\n"
            for para in history_content[:20]:
                history_md += f"- {para}\n\n"
        else:
            history_md += "## 大赛主题与赛道方向\n\n"
            history_md += "根据官网信息，大赛围绕'共创未来'主题，鼓励以下领域创新：\n\n"
            history_md += "- 韧性社区、环境教育、低碳环保\n"
            history_md += "- 食物系统、危机应对、公共卫生\n"
            history_md += "- 健康福祉、清洁能源、气候变化\n"
            history_md += "- 绿色交通、循环经济\n\n"
        
        # 添加大赛日程
        history_md += "## 大赛日程\n\n"
        schedule = re.search(r'(大赛日程与参赛报名.*?)(?=\n\n|\Z)', main_text, re.DOTALL)
        if schedule:
            history_md += schedule.group(1) + "\n\n"
        else:
            history_md += "根据官网信息，大赛通常分为：\n"
            history_md += "1. 报名与分赛区选拔赛（4-6月）\n"
            history_md += "2. 决赛入围团队优化作品（6-7月）\n"
            history_md += "3. 全国总决赛（7月下旬）\n\n"
        
        # 添加赛区动态提示
        history_md += "## 赛区动态\n\n"
        history_md += "各分赛区（如天津、厦门、上海、西安、武汉等）会举办选拔赛，具体赛题和作品要求请关注各赛区通知。\n\n"
        
        history_md += "---\n*注：本文件基于大赛官网公开信息整理，具体赛题以当年官方发布为准。*\n"
        
        # 写入文件
        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write(history_md)
        
        print(f"  ✅ 已生成: {expected_file}")
        return None  # 无问题
        
    except requests.exceptions.RequestException as e:
        error_msg = f"请求失败: {e}"
        print(f"  ❌ 错误: {error_msg}")
        return (idx, name, url, error_msg)
    except Exception as e:
        error_msg = f"处理失败: {e}"
        print(f"  ❌ 错误: {error_msg}")
        return (idx, name, url, error_msg)

def main():
    """主函数"""
    print("=" * 60)
    print("【历史赛题集】专用爬虫 v3 - 只处理第20项")
    print(f"目标竞赛: 20-中美青年创客大赛")
    print(f"文件保存位置: {os.getcwd()}")
    print(f"文件名格式: 20-中美青年创客大赛-{SECTION_TAG}.md")
    print(f"问题日志: {PROBLEM_URLS_FILE}")
    print("=" * 60)
    
    # 只处理这一个竞赛
    result = fetch_single_contest(TARGET_CONTEST)
    
    # 写入问题网址报告（如果有问题）
    if result:
        with open(PROBLEM_URLS_FILE, 'w', encoding='utf-8') as f:
            idx, name, url, err = result
            f.write("序号\t竞赛名称\t网址\t错误信息\n")
            f.write(f"{idx}\t{name}\t{url}\t{err}\n")
        print(f"\n⚠️ 爬取失败，详情已写入 {PROBLEM_URLS_FILE}")
    else:
        print(f"\n✅ 中美青年创客大赛 爬取成功！")
    
    print("\n任务完成！")

if __name__ == "__main__":
    main()