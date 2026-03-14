# 文件名: fetch_score_2.py
# 放置位置: 评分标准/ 文件夹内
# 功能: 只爬取3个问题竞赛的评分标准（序号12、20、39）
# 文件名格式: 序号-竞赛名称-评分标准.md
# 问题日志: problem_urls_score_2.txt

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from datetime import datetime

# ==================== 配置区域 ====================
# 只包含需要重新爬取的3个问题竞赛
CONTEST_LIST = [
    (12,   "全国大学生机械创新设计大赛",                                              "https://umic.moocollege.com/home/homepage"),
    (20,   "中美青年创客大赛",                                                        "http://www.chinaus-maker.org.cn/"),
    (39,   "全国高等院校数智化企业经营沙盘大赛",                                      "https://www.bizsand.cn"),
]

# 问题网址记录文件（加_2后缀）
PROBLEM_URLS_FILE = "problem_urls_score_2.txt"

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}
TIMEOUT = 15
# ==================== 配置结束 ====================

# 评分标准关键词
SCORE_KEYWORDS = ['评分标准', '评分细则', '评审规则', '打分', '评分', '标准', 'criteria', 'rubric', 'judging', 'scoring', '评分办法', '评审办法']

# 板块标识（用于文件名）
SECTION_TAG = "评分标准"

def safe_filename(name):
    """将竞赛名称转换为安全的文件名"""
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    return name.strip()

def extract_text_from_html(html, url):
    """提取HTML中的主要文本内容"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本、样式等
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # 尝试获取标题
        title = soup.title.string if soup.title else url
        title = title.strip()
        
        # 获取正文文本
        text = soup.get_text(separator='\n', strip=True)
        
        # 简单清理：去除多余空行
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = '\n'.join(lines)
        
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

def fetch_score_data(contest):
    """获取单个竞赛的评分标准数据并生成Markdown文件"""
    idx, name, url = contest
    safe_name = safe_filename(name)
    
    print(f"正在处理 [{idx:02d}] {name} ...")
    print(f"网址: {url}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        response.encoding = response.apparent_encoding or 'utf-8'
        html = response.text
        
        title, main_text = extract_text_from_html(html, url)
        
        # 查找评分标准相关内容
        score_content = find_specific_content(main_text, SCORE_KEYWORDS)
        
        # 构建Markdown内容
        score_md = f"# {name} - {SECTION_TAG}\n\n"
        score_md += f"**来源网址**: {url}\n"
        score_md += f"**抓取时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        score_md += f"## 页面标题\n\n{title}\n\n"
        
        if score_content:
            score_md += "## 相关评分内容\n\n"
            for para in score_content[:30]:
                score_md += f"{para}\n\n"
        else:
            score_md += "> ⚠️ 未在页面中找到明确的评分标准相关内容。以下是页面主要正文摘要，供参考。\n\n"
            score_md += "## 页面正文摘要\n\n"
            summary_lines = main_text.split('\n')[:40]
            for line in summary_lines:
                score_md += f"{line}\n\n"
        
        # 写入文件
        score_file = f"{idx:02d}-{safe_name}-{SECTION_TAG}.md"
        with open(score_file, 'w', encoding='utf-8') as f:
            f.write(score_md)
        
        print(f"  ✅ 已生成: {score_file}")
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
    print("【评分标准】专用爬虫 - 只处理3个问题网站")
    print(f"目标竞赛序号: 12, 20, 39")
    print(f"文件保存位置: {os.getcwd()}")
    print(f"文件名格式: 序号-竞赛名称-{SECTION_TAG}.md")
    print(f"问题日志: {PROBLEM_URLS_FILE}")
    print("=" * 60)
    
    problem_urls = []
    
    for contest in CONTEST_LIST:
        result = fetch_score_data(contest)
        if result:
            problem_urls.append(result)
        time.sleep(1)  # 礼貌性延迟
    
    # 写入问题网址报告
    if problem_urls:
        with open(PROBLEM_URLS_FILE, 'w', encoding='utf-8') as f:
            f.write("序号\t竞赛名称\t网址\t错误信息\n")
            for idx, name, url, err in problem_urls:
                f.write(f"{idx}\t{name}\t{url}\t{err}\n")
        print(f"\n⚠️ 发现 {len(problem_urls)} 个问题网址，详情已写入 {PROBLEM_URLS_FILE}")
    else:
        print(f"\n✅ 全部3个竞赛都爬取成功！")
    
    print("\n任务完成！")
    print(f"本次生成文件数量: {3 - len(problem_urls)} 个")

if __name__ == "__main__":
    main()