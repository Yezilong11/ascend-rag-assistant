# 文件名: fetch_score.py
# 放置位置: 评分标准/ 文件夹内
# 功能: 爬取64个竞赛的评分标准，生成64个Markdown文件到当前文件夹
# 文件名格式: 序号-竞赛名称-评分标准.md

import requests
from bs4 import BeautifulSoup
import os
import time
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime

# ==================== 配置区域 ====================
# 竞赛数据列表: 序号, 竞赛名称, 网址
CONTEST_LIST = [
    (1,    "中国国际大学生创新大赛",                                                 "https://cy.ncss.cn/"),
    (2,    "“挑战杯”全国大学生课外学术科技作品竞赛",                                  "http://www.tiaozhanbei.net/"),
    (3,    "“挑战杯”中国大学生创业计划大赛",                                          "http://www.chuangqingchun.net/"),
    (4,    "全国大学生创新年会",                                                      "http://gjcxcy.bjtu.edu.cn/"),
    (5,    "全国航空航天模型锦标赛",                                                  "https://www.sport.gov.cn/hgzx/"),
    (6,    "全国周培源大学生力学竞赛",                                                "http://zpy.cstam.org.cn/"),
    (7,    "全国大学生集成电路创新创业大赛",                                          "http://univ.ciciec.com/"),
    (8,    "iCAN大学生创新创业大赛",                                                  "http://www.g-ican.com/"),
    (9,    "全国大学生物联网设计竞赛",                                                "https://iot.sjtu.edu.cn/"),
    (10,   "全国大学生嵌入式芯片与系统设计竞赛",                                      "http://www.socchina.net/"),
    (11,   "“大唐杯”全国大学生新一代信息通信技术大赛",                                 "https://dtcup.dtxiaotangren.com"),
    (12,   "全国大学生机械创新设计大赛",                                              "http://umic.ckcest.cn/"),
    (13,   "中国大学生工程实践与创新能力大赛",                                        "http://www.gcxl.edu.cn/"),
    (14,   "全国大学生机器人大赛",                                                    "https://www.robomaster.com/"),
    (15,   "全国大学生先进成图技术与产品信息建模创新大赛",                            "http://www.chengtudasai.com/"),
    (16,   "全国三维数字化创新设计大赛",                                              "https://3dds.3ddl.net/"),
    (17,   "中国大学生机械工程创新创意大赛",                                          "http://www.gczbds.org"),
    (18,   "中国高校智能机器人创意大赛",                                              "http://www.robotcontest.cn/"),
    (19,   "国际大学生智能农业装备创新大赛",                                          "http://uiaec.ujs.edu.cn"),
    (20,   "中美青年创客大赛",                                                        "https://chinaus-maker.cscse.edu.cn/"),
    (21,   "全国大学生金相技能大赛",                                                  "https://www.jxds.tech/"),
    (22,   "全国大学生节能减排社会实践与科技竞赛",                                    "http://www.jienengjianpai.org/"),
    (23,   "全国大学生电子设计竞赛",                                                  "http://www.nuedcchina.com/"),
    (24,   "全国大学生智能汽车竞赛",                                                  "http://www.eepw.com.cn/event/action/freescale_car2012/"),
    (25,   "中国工业智能挑战赛",                                                      "http://www.dllgt.com/"),
    (26,   "“西门子杯”中国智能制造挑战赛",                                             "https://siemenscup-cimc.org.cn"),
    (27,   "全国高校BIM毕业设计创新大赛",                                             "https://gxbsxs.glodonedu.com/"),
    (28,   "中国(国际)传感器创新创业大赛",                                            "http://contest.cis.org.cn/"),
    (29,   "全国大学生光电设计竞赛",                                                  "http://gd.p.moocollege.com/"),
    (30,   "全国大学生化工设计竞赛",                                                  "http://iche.zju.edu.cn/"),
    (31,   "全国大学生化学实验创新设计大赛",                                          "https://cid.nju.edu.cn/"),
    (32,   "中国大学生物理学术竞赛",                                                  "https://www.cupt-iypt.com/"),
    (33,   "全国大学生物理实验竞赛",                                                  "http://wlsycx.moocollege.com/"),
    (34,   "全国大学生数学竞赛",                                                      "https://www.cmathc.org.cn/"),
    (35,   "全国大学生数学建模竞赛",                                                  "http://www.mcm.edu.cn/"),
    (36,   "美国大学生数学建模竞赛",                                                  "https://www.comap.com/contests/mcm-icm"),
    (37,   "全国大学生统计建模大赛",                                                  "http://tjjmds.ai-learning.net/"),
    (38,   "全国大学生生命科学竞赛（CULSC）",                                         "https://www.culsc.cn/"),
    (39,   "全国高等院校数智化企业经营沙盘大赛",                                      "http://spbk.seentao.com"),
    (40,   "全国大学生市场调查与分析大赛",                                            "http://www.china-cssc.org/"),
    (41,   "全国大学生电子商务“创新、创意及创业”挑战赛",                               "http://www.3chuang.net/"),
    (42,   "全国大学生物流设计大赛",                                                  "http://www.clpp.org.cn/"),
    (43,   "中国大学生服务外包创新创业大赛",                                          "http://www.fwwb.org.cn/"),
    (44,   "全国大学生结构设计竞赛",                                                  "http://www.structurecontest.com/"),
    (45,   "全国大学生建筑类竞赛",                                                    "https://www.uedmagazine.net/"),
    (46,   "全国大学生广告艺术大赛",                                                  "https://www.sun-ada.net/"),
    (47,   "中国大学生计算机设计大赛",                                                "http://jsjds.blcu.edu.cn/"),
    (48,   "全国大学生混凝土材料设计大赛",                                            "https://bksy.bjtu.edu.cn/"),
    (49,   "全国大学生交通运输科技大赛",                                              "http://www.nactrans.com.cn/"),
    (50,   "国际大学生程序设计竞赛（ICPC）",                                          "https://icpc.global/"),
    (51,   "全国大学生信息安全竞赛",                                                  "http://www.ciscn.cn/"),
    (52,   "全国大学生软件创新大赛",                                                  "https://www.swcontest.com.cn/"),
    (53,   "中国高校计算机大赛",                                                      "http://www.c4best.cn/"),
    (54,   "中国机器人及人工智能大赛",                                                "https://developer.apollo.auto/"),
    (55,   "全国大学生计算机系统能力大赛",                                            "https://compiler.educg.net/"),
    (56,   "全球校园人工智能算法精英大赛",                                            "https://developer.huawei.com/consumer/cn/activity/digixActivity/digixdetail/101655281685926449"),
    (57,   "全国大学生英语竞赛",                                                      "https://www.chinaneccs.cn/"),
    (58,   "全国英语口译大赛",                                                        "https://www.lscat.cn/"),
    (59,   "“外研社·国才杯”“理解当代中国”全国大学生外语能力大赛",                     "http://uchallenge.unipus.cn/"),
    (60,   "“外研社·国才杯”全国大学生英语辩论赛",                                     "http://uchallenge.unipus.cn/"),
    (61,   "“21世纪杯”全国英语演讲比赛",                                              "https://contest.i21st.cn/"),
    (62,   "全国大学生职业规划大赛",                                                  "https://zgs.chsi.com.cn/home"),
    (63,   "中国大学生方程式系列赛事",                                                "http://www.formulastudent.com.cn/"),
    (64,   "全国海洋航行器设计与制作大赛",                                            "http://www.mycmvc.cn/"),
]

# 问题网址记录文件
PROBLEM_URLS_FILE = "problem_urls_score.txt"

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
            for para in score_content[:30]:  # 限制数量
                score_md += f"{para}\n\n"
        else:
            score_md += "> ⚠️ 未在页面中找到明确的评分标准相关内容。以下是页面主要正文摘要，供参考。\n\n"
            score_md += "## 页面正文摘要\n\n"
            summary_lines = main_text.split('\n')[:40]
            for line in summary_lines:
                score_md += f"{line}\n\n"
        
        # 写入文件（文件名包含板块标识）
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
    print("【评分标准】爬虫开始运行")
    print(f"目标: 为 {len(CONTEST_LIST)} 个竞赛生成评分标准Markdown文件")
    print(f"文件保存位置: {os.getcwd()}")
    print(f"文件名格式: 序号-竞赛名称-{SECTION_TAG}.md")
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
        print(f"\n✅ 所有网址均爬取成功！")
    
    print("\n任务完成！")
    print(f"生成文件数量: {len(CONTEST_LIST)} 个")

if __name__ == "__main__":
    main()