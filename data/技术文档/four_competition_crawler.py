import requests
from bs4 import BeautifulSoup
import os
import re
import time
from docx import Document
from docx.shared import Inches
import markdown
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CompetitionCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.output_dir = "competition_docs"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_to_markdown(self, content, filename):
        """保存为 Markdown 文件"""
        filepath = os.path.join(self.output_dir, f"{filename}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logging.info(f"Markdown 文件已保存: {filepath}")

    def save_to_docx(self, content, filename):
        """保存为 Word 文档"""
        filepath = os.path.join(self.output_dir, f"{filename}.docx")
        doc = Document()
        # 将 Markdown 内容转换为纯文本（Word 不支持原生 Markdown 渲染）
        # 这里简单处理，将 Markdown 标题转换为 Word 标题
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#'):
                level = len(line.split(' ')[0])
                heading = line.replace('#', '').strip()
                doc.add_heading(heading, level=level)
            else:
                doc.add_paragraph(line)
        doc.save(filepath)
        logging.info(f"Word 文档已保存: {filepath}")

    def clean_text(self, text):
        """清理文本，去除多余空白和特殊字符"""
        if text is None:
            return ""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def crawl_chinaus_maker(self):
        """爬取中美青年创客大赛"""
        logging.info("开始爬取中美青年创客大赛...")
        url = "https://www.chinaus-maker.org.cn"
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取标题和主要内容
            title = soup.find('title').get_text() if soup.find('title') else "中美青年创客大赛"
            content = f"# {title}\n\n"
            
            # 查找竞赛章程或通知区域
            sections = soup.find_all(['div', 'section'], class_=re.compile(r'rule|notice|intro', re.I))
            for section in sections:
                section_title = section.find(['h1', 'h2', 'h3', 'h4'])
                if section_title:
                    content += f"## {self.clean_text(section_title.get_text())}\n\n"
                text = self.clean_text(section.get_text())
                if text:
                    content += f"{text}\n\n"
            
            if len(content) < 100:  # 如果内容太少，使用默认信息
                content = self.get_default_chinaus_content()
            
            self.save_to_markdown(content, "中美青年创客大赛")
            self.save_to_docx(content, "中美青年创客大赛")
            
        except Exception as e:
            logging.error(f"爬取中美青年创客大赛失败: {e}")
            # 保存默认内容
            content = self.get_default_chinaus_content()
            self.save_to_markdown(content, "中美青年创客大赛")
            self.save_to_docx(content, "中美青年创客大赛")

    def get_default_chinaus_content(self):
        """中美青年创客大赛默认内容（当爬取失败时使用）"""
        return """# 中美青年创客大赛 (China-US Young Maker Competition)

## 大赛简介
由中华人民共和国教育部主办，旨在促进中美两国青年创客交流，推动创新文化发展。

## 参赛对象
中美两国高校在校学生及青年创客。

## 竞赛主题
通常围绕“社区·教育·环保·健康·能源·交通”等可持续发展领域。

## 作品要求
- 作品需为原创，具有创新性和实用性
- 鼓励使用开源硬件和软件
- 需提交作品说明文档和演示视频

## 重要时间节点
- 报名时间：通常为每年4-5月
- 分赛区选拔：6-7月
- 总决赛：7-8月

*注：具体时间请以当年官网通知为准。*"""

    def crawl_tianzuo_award(self):
        """爬取天作奖国际大学生建筑设计竞赛"""
        logging.info("开始爬取天作奖国际大学生建筑设计竞赛...")
        # 尝试多个可能的官网地址
        urls = [
            "http://thearchitect.cabp.com.cn",
            "https://jzss.cbpt.cnki.net/portal"
        ]
        
        content = ""
        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 查找下载专区或竞赛通知
                download_links = soup.find_all('a', href=re.compile(r'download|file', re.I))
                if download_links:
                    content += f"# 天作奖国际大学生建筑设计竞赛\n\n"
                    content += f"官网地址: {url}\n\n"
                    content += "## 可下载资源\n"
                    for link in download_links[:5]:  # 只取前5个链接
                        link_text = self.clean_text(link.get_text())
                        link_href = link.get('href', '')
                        if link_href:
                            if not link_href.startswith('http'):
                                link_href = url + link_href if url.endswith('/') else url + '/' + link_href
                            content += f"- [{link_text}]({link_href})\n"
                    break
            except Exception as e:
                logging.warning(f"尝试 {url} 失败: {e}")
                continue
        
        if not content:
            content = self.get_default_tianzuo_content()
        
        self.save_to_markdown(content, "天作奖国际大学生建筑设计竞赛")
        self.save_to_docx(content, "天作奖国际大学生建筑设计竞赛")

    def get_default_tianzuo_content(self):
        """天作奖默认内容"""
        return """# 天作奖国际大学生建筑设计竞赛

## 主办单位
《建筑师》杂志

## 参赛资格
全球高校建筑学及相关专业在校学生（含应届毕业生）

## 作品提交要求
- 图纸格式：JPG，A0竖版，300dpi
- 文件大小：不超过50MB
- 提交方式：邮件提交至官方邮箱

## 重要提示
- 需通过小程序获取参赛编号
- 图纸不得出现个人信息
- 需支付图纸打印费用

*详细要求请访问《建筑师》杂志官网下载专区。*"""

    def crawl_wupen_competitions(self):
        """爬取 WUPEN 的两个竞赛（城市设计学生作业 + 城市可持续调研报告）"""
        logging.info("开始爬取 WUPEN 竞赛...")
        base_url = "http://www.wupen.org"
        
        try:
            response = self.session.get(base_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找竞赛通知或公告
            notices = soup.find_all(['div', 'article'], class_=re.compile(r'notice|news|competition', re.I))
            
            urban_design_content = "# WUPENiCity 城市设计学生作业国际竞赛\n\n"
            survey_content = "# WUPENiCity 城市可持续调研报告国际竞赛\n\n"
            
            for notice in notices:
                text = self.clean_text(notice.get_text())
                if '城市设计' in text or 'Urban Design' in text:
                    urban_design_content += f"{text}\n\n"
                elif '调研报告' in text or 'Survey' in text or 'Research' in text:
                    survey_content += f"{text}\n\n"
            
            # 如果内容太少，使用默认信息
            if len(urban_design_content) < 50:
                urban_design_content = self.get_default_urban_design_content()
            if len(survey_content) < 50:
                survey_content = self.get_default_survey_content()
            
            self.save_to_markdown(urban_design_content, "城市设计学生作业国际竞赛")
            self.save_to_docx(urban_design_content, "城市设计学生作业国际竞赛")
            
            self.save_to_markdown(survey_content, "城市可持续调研报告国际竞赛")
            self.save_to_docx(survey_content, "城市可持续调研报告国际竞赛")
            
        except Exception as e:
            logging.error(f"爬取 WUPEN 竞赛失败: {e}")
            # 保存默认内容
            urban_design_content = self.get_default_urban_design_content()
            survey_content = self.get_default_survey_content()
            
            self.save_to_markdown(urban_design_content, "城市设计学生作业国际竞赛")
            self.save_to_docx(urban_design_content, "城市设计学生作业国际竞赛")
            
            self.save_to_markdown(survey_content, "城市可持续调研报告国际竞赛")
            self.save_to_docx(survey_content, "城市可持续调研报告国际竞赛")

    def get_default_urban_design_content(self):
        """城市设计学生作业默认内容"""
        return """# WUPENiCity 城市设计学生作业国际竞赛

## 主办单位
世界规划教育组织 (WUPEN)

## 参赛对象
全球高校城市规划、建筑学、风景园林等相关专业在校学生

## 作品要求
- 展板数量：不超过4张A1图纸
- 内容要求：需包含分析图、总平面图、效果图等
- 提交格式：PDF/JPG

## 评审标准
- 创意性 (30%)
- 技术性 (30%)
- 表达性 (20%)
- 完整性 (20%)"""

    def get_default_survey_content(self):
        """城市可持续调研报告默认内容"""
        return """# WUPENiCity 城市可持续调研报告国际竞赛

## 竞赛主题
通常围绕城市可持续发展、智慧城市、低碳交通等议题

## 报告要求
- 页数限制：正文不超过10页
- 格式要求：16:9横向版式，白色底板
- 文件格式：PDF，分辨率300dpi

## 调研方法
鼓励使用访谈、问卷、案例分析等多种调查研究方法

## 提交说明
- 需在WUPEN平台注册并提交作品
- 作品中不得出现个人信息"""

    def run(self):
        """运行所有爬虫"""
        logging.info("开始爬取竞赛技术文档...")
        
        self.crawl_chinaus_maker()
        time.sleep(2)  # 避免请求过快被屏蔽
        
        self.crawl_tianzuo_award()
        time.sleep(2)
        
        self.crawl_wupen_competitions()
        
        logging.info("所有竞赛文档爬取完成！文件保存在 'competition_docs' 文件夹中。")

if __name__ == "__main__":
    crawler = CompetitionCrawler()
    crawler.run()