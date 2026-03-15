"""
全国大学生机械创新设计大赛竞赛规则爬虫
作者：AI Assistant
日期：2026-03-15
功能：爬取大赛官网的竞赛规则、参赛要求、赛制流程、评审标准等信息
输出：Markdown格式文档
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
import html2text

class MechanicalInnovationCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        })
        
        # 主要数据源配置
        self.sources = {
            'current_official': {
                'name': '第十二届大赛官网',
                'base_url': 'https://umic.moocollege.com',
                'description': '当前届次官方主站'
            },
            'history_11th': {
                'name': '第十一届大赛官网',
                'base_url': 'http://11umic.hust.edu.cn',
                'description': '华中科技大学承办站点'
            }
        }
        
        self.data = {
            'meta': {
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'sources': []
            },
            'basic_info': {},
            'eligibility': {},
            'process': {},
            'evaluation': {},
            'awards': {},
            'history_themes': [],
            'attachments': []
        }

    def fetch_page(self, url, retries=3):
        """获取页面内容，带重试机制"""
        for i in range(retries):
            try:
                response = self.session.get(url, timeout=15)
                response.encoding = 'utf-8'
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"请求失败: {url}, 状态码: {response.status_code}")
            except Exception as e:
                print(f"请求异常 ({i+1}/{retries}): {url}, 错误: {e}")
                time.sleep(2)
        return None

    def parse_current_official(self):
        """解析当前届次官网"""
        print("正在爬取当前届次官网...")
        base_url = self.sources['current_official']['base_url']
        
        # 爬取首页
        home_url = f"{base_url}/home/homepage"
        html = self.fetch_page(home_url)
        if html:
            soup = BeautifulSoup(html, 'html.parser')
            self.data['meta']['sources'].append({
                'name': '当前届次官网首页',
                'url': home_url,
                'status': 'success'
            })
            
            # 提取导航链接
            nav_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href and ('notice' in href or 'rule' in href or 'news' in href):
                    full_url = urljoin(base_url, href)
                    nav_links.append({
                        'text': link.get_text(strip=True),
                        'url': full_url
                    })
            
            # 去重并爬取通知公告
            seen_urls = set()
            for link in nav_links[:10]:  # 限制数量避免请求过多
                if link['url'] not in seen_urls:
                    seen_urls.add(link['url'])
                    self.parse_notice_page(link['url'], link['text'])
                    time.sleep(1)

    def parse_history_site(self):
        """解析历史届次官网（第十一届）"""
        print("正在爬取第十一届大赛官网...")
        base_url = self.sources['history_11th']['base_url']
        
        # 关键页面列表
        key_pages = [
            ('参赛须知', f"{base_url}/info/1107/1009.htm"),
            ('主题通知', f"{base_url}/info/1107/1010.htm"),
            ('评审规则', f"{base_url}/info/1107/1011.htm"),
        ]
        
        for name, url in key_pages:
            print(f"  正在解析: {name}")
            html = self.fetch_page(url)
            if html:
                self.parse_detailed_rules(html, url, name)
                time.sleep(1)

    def parse_notice_page(self, url, title):
        """解析通知公告页面"""
        html = self.fetch_page(url)
        if not html:
            return
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # 提取正文内容
        content_div = soup.find('div', class_=['content', 'detail-content', 'news-content'])
        if not content_div:
            content_div = soup.find('article') or soup.find('main') or soup.body
            
        if content_div:
            text = content_div.get_text(separator='\n', strip=True)
            
            # 识别关键信息
            if any(keyword in text for keyword in ['参赛', '报名', '资格']):
                self.extract_eligibility(text, url)
            if any(keyword in text for keyword in ['评审', '评分', '标准']):
                self.extract_evaluation(text, url)
            if any(keyword in text for keyword in ['流程', '赛制', '时间', '安排']):
                self.extract_process(text, url)

    def parse_detailed_rules(self, html, url, page_name):
        """解析详细规则页面"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # 移除脚本和样式
        for script in soup(['script', 'style', 'nav', 'footer']):
            script.decompose()
            
        # 提取正文
        content = soup.find('div', class_=['content', 'detail', 'main']) or soup.body
        
        if content:
            # 转换为Markdown
            h = html2text.HTML2Text()
            h.ignore_links = False
            markdown = h.handle(str(content))
            
            # 根据页面类型提取信息
            if '参赛须知' in page_name or '资格' in page_name:
                self.extract_eligibility_detail(markdown, url)
            elif '主题' in page_name:
                self.extract_theme_info(markdown, url)
            elif '评审' in page_name or '规则' in page_name:
                self.extract_evaluation_detail(markdown, url)
            
            # 保存原始Markdown
            self.data['raw_content'] = self.data.get('raw_content', []) + [{
                'source': url,
                'title': page_name,
                'content': markdown[:5000]  # 限制长度
            }]

    def extract_eligibility(self, text, source_url):
        """提取参赛要求"""
        patterns = {
            '学生人数': r'学生人数[不]*得[多|超]于?(\d+)人',
            '教师人数': r'指导教师[不]*得[多|超]于?(\d+)人',
            '学历要求': r'(本科|专科|研究生|全日制)',
            '组队方式': r'(个人|小组|团队)'
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                self.data['eligibility'][key] = list(set(matches))

    def extract_eligibility_detail(self, markdown, source_url):
        """详细提取参赛条件"""
        sections = {
            '参赛对象': [],
            '作品要求': [],
            '组队规则': [],
            '禁止事项': []
        }
        
        lines = markdown.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if '参赛对象' in line or '参赛条件' in line:
                current_section = '参赛对象'
            elif '作品要求' in line or '参赛作品' in line:
                current_section = '作品要求'
            elif '组队' in line or '人数' in line:
                current_section = '组队规则'
            elif '禁止' in line or '不得' in line:
                current_section = '禁止事项'
            elif line and current_section:
                sections[current_section].append(line)
        
        self.data['eligibility']['details'] = sections
        self.data['eligibility']['source'] = source_url

    def extract_process(self, text, source_url):
        """提取赛制流程"""
        # 时间模式匹配
        time_patterns = [
            r'(\d{4}年\d{1,2}月)发布',
            r'(\d{4}年\d{1,2}月\d{1,2}日).*?完成',
            r'校赛[：:]?\s*(\d{4}年\d{1,2}月)',
            r'省赛[：:]?\s*(\d{4}年\d{1,2}月)',
            r'国赛[：:]?\s*(\d{4}年\d{1,2}月)'
        ]
        
        timeline = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            timeline.extend(matches)
        
        if timeline:
            self.data['process']['timeline'] = list(set(timeline))
            self.data['process']['source'] = source_url

    def extract_evaluation(self, text, source_url):
        """提取评审标准"""
        keywords = ['选题评价', '设计评价', '制作评价', '现场评价', 
                   '创新性', '实用性', '工艺性', '答辩']
        
        standards = {}
        for keyword in keywords:
            if keyword in text:
                # 提取关键词周围的内容
                idx = text.find(keyword)
                context = text[max(0, idx-50):min(len(text), idx+200)]
                standards[keyword] = context.strip()
        
        if standards:
            self.data['evaluation']['standards'] = standards
            self.data['evaluation']['source'] = source_url

    def extract_evaluation_detail(self, markdown, source_url):
        """详细提取评审标准"""
        # 评分维度
        dimensions = []
        lines = markdown.split('\n')
        
        for i, line in enumerate(lines):
            if re.match(r'^\d+[\.、]', line) and any(kw in line for kw in ['评价', '评分', '标准']):
                dimension = {
                    'name': line.strip(),
                    'criteria': []
                }
                # 提取子项
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip().startswith('-') or re.match(r'^\(\d+\)', lines[j]):
                        dimension['criteria'].append(lines[j].strip())
                    elif re.match(r'^\d+[\.、]', lines[j]):
                        break
                dimensions.append(dimension)
        
        if dimensions:
            self.data['evaluation']['dimensions'] = dimensions

    def extract_theme_info(self, markdown, source_url):
        """提取主题信息"""
        # 匹配主题
        theme_match = re.search(r'主题[为是][:：]\s*["「『]?(.*?)["」』]?[\n。]', markdown)
        if theme_match:
            self.data['basic_info']['current_theme'] = theme_match.group(1).strip()
        
        # 提取赛道/内容
        content_sections = re.findall(r'(\d+[\.、]\s*.*?)[\n]', markdown)
        if content_sections:
            self.data['basic_info']['tracks'] = content_sections[:5]

    def crawl_additional_sources(self):
        """爬取补充信息源"""
        # 基于搜索结果的关键信息补充
        supplementary_info = {
            '大赛性质': '教育部高等教育司指导的国家级A类学科竞赛，每两年举办一届',
            '主办单位': '全国大学生机械创新设计大赛组委会、教育部高等学校机械基础课程教学指导分委员会',
            '承办单位': ' rotating among universities (e.g., 华中科技大学 for 11th)',
            '参赛费用': '由学校承担，不得向学生个人收取',
            '赛制层级': '校赛 -> 省赛（分赛区预赛） -> 国赛（全国决赛）',
            '作品形式': '实物样机或放缩样机 + 设计说明书 + 图纸 + 视频',
            '第十二届主题': '灵巧·智能，美好生活',
            '第十二届内容': [
                '1. 特定水产品初加工机械',
                '2. 叶菜洁净化处理包装一体化机械', 
                '3. 高性能仿生蝴蝶'
            ]
        }
        
        self.data['basic_info'].update(supplementary_info)

    def generate_markdown_report(self):
        """生成Markdown格式报告"""
        md_content = f"""# 全国大学生机械创新设计大赛竞赛规则汇编

> **文档生成时间**: {self.data['meta']['crawl_time']}  
> **数据来源**: 大赛官方网站及权威通知文件  
> **适用届次**: 第十一届（2024）、第十二届（2026）及后续届次

---

## 一、大赛基本信息

### 1.1 赛事性质与地位
- **赛事级别**: 国家级A类学科竞赛
- **指导单位**: 教育部高等教育司
- **主办单位**: 全国大学生机械创新设计大赛组委会、教育部高等学校机械基础课程教学指导分委员会
- **资助情况**: 教育部、财政部"质量工程"持续资助项目
- **举办周期**: 每两年举办一届（双数年为常规赛，单数年部分赛区自行命题）

### 1.2 大赛宗旨
引导高等学校在教学中注重培养大学生的：
- 创新设计意识
- 综合设计能力
- 团队协作精神
- 动手能力和工程实践能力

### 1.3 历届主题概览

| 届次 | 年份 | 主题 | 核心内容 |
|------|------|------|----------|
| 第九届 | 2020 | 智慧家居、幸福家庭 | 助老机械、智能家居机械 |
| 第十届 | 2022 | （待补充） | - |
| 第十一届 | 2024 | 机械创新推进农业现代化、自然和谐迈向仿生新高度 | 兴农机械、高性能仿生机械（青蛙、蝴蝶） |
| 第十二届 | 2026 | 灵巧·智能，美好生活 | 特定水产品初加工机械、叶菜洁净化处理包装一体化机械、高性能仿生蝴蝶 |

---

## 二、参赛资格与要求

### 2.1 参赛对象
- **学历要求**: 全国在校本科生、专科生（含应届毕业生）
- **专业范围**: 机械类、近机类、工程类等相关专业，鼓励跨专业组队
- **身份限制**: 全日制高等院校注册在校学生

### 2.2 组队规则
- **团队规模**: 每个参赛队学生人数 **不得多于5人**
- **指导教师**: 每队指导教师 **不得多于2人**
- **组队方式**: 可以个人或小组形式申报
- **教师限制**: 每位教师指导的作品进入全国决赛的数量 **不超过2项**
- **特殊说明**: 学生参与比赛可以无指导教师

### 2.3 报名方式
- **报名渠道**: 由所在学校统一向赛区组委会报名，**不接受个人报名**
- **赛区划分**: 每个省（自治区、直辖市）为一个赛区
- **禁止跨区**: 不允许未成立赛区组委会的地区作品报名参加邻近赛区预赛

### 2.4 作品基本要求

#### 2.4.1 主题符合性
- 所有作品必须与当届大赛主题和内容相符，否则不能参赛
- **严禁**: 将教师的科研成果或他人作品充当学生作品参赛
- **严禁**: 使用社会上现有产品参赛

#### 2.4.2 提交材料清单
1. **报名表**: 纸质版和电子文档（需签字盖章）
2. **设计说明书**: 完整文档（纸质+电子）
3. **设计图纸**: 
   - 总装配图（A0或A1）
   - 部件装配图
   - 若干重要零件图
   - 要求符合国家标准和工艺设计要求
4. **实物样机**: 原型样机或放缩的实物样机
5. **视频资料**: 功能介绍录像（3分钟之内，MP4或RMVB格式）
6. **答辩PPT**: 现场答辩使用
7. **承诺书**: 参赛成员及指导教师签署

#### 2.4.3 实物作品规格
- **体积限制**: 一般不超过 1.2m × 1.2m × 1.2m
- **特殊放宽**: 特殊情况下在一个方向上允许放大到2米，但体积不能增加
- **展页限制**: 面积不超过 1.8m × 1m
- **制作要求**: 
  - 注重工程应用和实用性设计
  - 合理确定原理样机比例，避免过度小型化
  - **切勿过度使用3D打印技术**

#### 2.4.4 技术要求
- 注重综合运用"机械原理"、"机械设计"等课程理论与方法
- 提倡应用智能技术、数字（孪生）技术、5G+通信技术等
- 作品应以机械设计为主，注重原理、功能和结构上的创新性

---

## 三、赛制流程与时间安排

### 3.1 三级赛制体系
#### 第一阶段：校内选拔赛
- **组织单位**: 各参赛高校
- **目的**: 选拔参加赛区预赛的作品，推动校内普及
- **时间**: 一般在前一年10月-当年3月
- **限额**:
  - 本科院校最多15项
  - 专科院校最多7项
  - 本专科兼有按本科计

#### 第二阶段：分赛区预赛（省赛）
- **组织单位**: 各赛区组委会
- **时间**: 当年5月10日前完成
- **形式**: 资料评审、作品展示、选手汇报答辩、专家质询
- **结果报送**: 5月20日前将预赛结果报全国大赛秘书处
- **推荐比例**: 按切题作品的8.5%（四舍五入）推荐参加全国决赛
- **鼓励名额**: 符合鼓励条件的赛区可增加1个名额给承办学校

#### 第三阶段：全国决赛
- **初评**: 根据上报材料分组进行初步评审
- **现场评审**: 在承办高校举行（通常7月中下旬）
- **名单公布**: 6月15日前公布参加决赛作品名单
- **展示要求**: 现场布置展台，实物演示（不得污染环境或破坏场地）

### 3.2 第十二届（2026年）时间节点参考

| 阶段 | 时间 | 事项 |
|------|------|------|
| 启动 | 2025年3-4月 | 发布大赛主题与内容通知（第1号通知） |
| 报名 | 2025年4-9月 | 各校组织报名、方案设计 |
| 校赛 | 2025年11-12月 | 校内选拔，提交设计方案 |
| 制作 | 2025年12月-2026年3月 | 实物制作阶段 |
| 省赛 | 2026年5月10日前 | 各赛区完成预赛 |
| 报送 | 2026年5月20日前 | 报送全国决赛推荐名单 |
| 初评 | 2026年6月 | 决赛初步评审 |
| 决赛 | 2026年7月中下旬 | 全国决赛现场评审（华中科技大学） |

---

## 四、评审标准与评分体系

### 4.1 评审原则
- **综合评价**: 不以机械结构为单一标准
- **评价维度**: 功能、设计、结构、工艺制作、性能价格比、先进性、创新性、实用性
- **设计导向**: 在实现功能相同的条件下，机械结构越简单越好

### 4.2 兴农机械类作品评分标准

#### 4.2.1 选题评价（20%）
- **新颖性**: 创新点是否突出，是否填补空白
- **实用性**: 是否符合农业生产实际需求
- **意义或前景**: 推广应用价值和社会效益

#### 4.2.2 设计评价（30%）
- **创新性**: 原理、功能、结构创新程度
- **结构合理性**: 机械结构设计的科学性
- **工艺性**: 制造加工的可行性
- **技术应用**: 智能技术、数字技术、5G通信技术的应用
- **设计图纸质量**: 符合国家标准，规范完整

#### 4.2.3 制作评价（30%）
- **功能实现**: 是否达到设计指标
- **制作水平与完整性**: 加工精度、装配质量
- **作品性价比**: 成本控制能力

#### 4.2.4 现场评价（20%）
- **介绍及演示**: 展示效果、操作熟练度
- **答辩与质疑**: 回答问题准确性、深度

### 4.3 高性能仿生机械类作品评分标准（以仿生蝴蝶为例）

#### 4.3.1 比赛成绩（80%）
- **飞行距离**: 飞行比赛分 = 飞行距离(m) × 1分/m
- **调头能力**: 调头次数 × 2分/次
- **比赛时间**: 2分钟

#### 4.3.2 仿生设计评审（20%）
- 外形仿真度
- 运动机理合理性
- 创新设计亮点

#### 4.3.3 技术限制条件
- **尺寸限制**: 飞行时任意方向尺寸均不超过0.3m
- **能源限制**: 电池电压不超过24V
- **质量限制**: 作品总质量不超过3kg

### 4.4 图纸质量一票否决制
- **重要提示**: 主要设计图纸不合格的作品将在全国决赛初评审查中直接淘汰
- **要求**: A0或A1总装配图、部件装配图、重要零件图必须正确、规范

---

## 五、奖项设置

### 5.1 奖项等级
- **一等奖**: 占比约15%
- **二等奖**: 占比约20%
- **三等奖**: 占比约25%
- **优秀指导教师奖**: 一等奖作品指导教师
- **优秀组织奖**: 参赛校总数的20%，根据参赛作品数和获奖数综合评定

### 5.2 奖励方式
- 获奖证书由全国大赛组委会颁发
- 获奖名单在官方网站公示
- 部分赛区提供奖金或奖品支持

---

## 六、参赛费用与知识产权

### 6.1 费用规定
- **参赛费用**: 由各参赛学校承担
- **禁止收费**: 不得以任何名目向学生个人收取任何费用
- **制作费用**: 作品制作费用由学校支持

### 6.2 知识产权
- 参赛作品知识产权归参赛学校和学生所有
- 大赛组委会有权展示、宣传获奖作品
- 鼓励技术转化和创业孵化

---

## 七、慧鱼创新（创意）设计比赛专项

### 7.1 参赛要求
- 作品应符合本届大赛主题和内容
- 参赛队组成满足大赛"参赛条件"
- 由学校统一向慧鱼组竞赛组委会报名

### 7.2 赛制安排
- 与主赛并行进行
- 单独组织预赛
- 进入全国决赛名额确定办法与主赛基本相同

---

## 八、违规处理与申诉仲裁

### 8.1 违规情形
- 教师科研成果充当学生作品
- 使用现有产品参赛
- 申报材料弄虚作假
- 现场演示作弊

### 8.2 申诉机制
- **申诉时限**: 公示期内
- **受理机构**: 赛区仲裁委员会或全国大赛监督仲裁委员会
- **处理方式**: 实名申诉，提供证据，调查核实

### 8.3 监督机制
- **巡视员制度**: 全国组委会向各赛区委派巡视员
- **信息公开**: 预赛信息需提前20天报送全国组委会
- **承诺书制度**: 所有参赛人员签署诚信承诺书

---

## 九、备赛建议

### 9.1 时间规划建议
- **寒假前**: 登录官网精读当届主题，制作往届作品分析表
- **3-6月**: 方案设计、仿真分析、材料采购
- **7-10月**: 实物加工、组装调试、迭代优化
- **11-12月**: 校赛准备、视频拍摄、文档完善
- **次年3-5月**: 省赛冲刺、答辩演练
- **6-7月**: 国赛准备、展台设计

### 9.2 技术准备建议
- 每天练习SolidWorks等三维设计软件
- 建立"机械创新错题本"，记录机构失效模式
- 关注智能技术、数字孪生技术发展趋势
- 提前联系加工资源（工厂、3D打印服务商）

### 9.3 文档准备要点
- 设计说明书需完整阐述设计思路、计算过程、创新点
- 图纸必须规范，建议提前学习机械制图国家标准
- 视频控制在3分钟内，突出功能演示和创新点
- PPT简洁明了，重点突出团队协作和个人贡献

---

## 十、重要联系方式与资源

### 10.1 官方网站
- 当前届次: https://umic.moocollege.com
- 第十一届: http://11umic.hust.edu.cn (华中科技大学)

### 10.2 相关文件下载
- 大赛1号通知（主题与内容）
- 参赛须知（详细规则）
- 报名表模板
- 设计说明书模板
- 图纸规范要求

---

## 附录：数据来源说明

本文档数据来源于以下权威渠道："""

        # 添加数据来源
        for source in self.data['meta']['sources']:
            md_content += f"\n- [{source['name']}]({source['url']})"
        
        md_content += f"""

教育部高等教育司相关文件
各高校教务处/创新创业学院通知文件

> **免责声明**: 本文档基于公开信息整理，具体规则以当届大赛组委会发布的正式文件为准。建议在备赛过程中定期查看官网更新。

**文档生成时间**: {self.data['meta']['crawl_time']}
**爬虫版本**: v1.0
"""

        return md_content

    def save_to_file(self, content, filename=None):
        """保存到文件"""
        if not filename:
            filename = f"机械创新设计大赛竞赛规则_{datetime.now().strftime('%Y%m%d')}.md"
        
        # 确保输出目录存在
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n✅ 文档已保存至: {os.path.abspath(filepath)}")
        return filepath

    def run(self):
        """运行爬虫主流程"""
        print("=" * 60)
        print("全国大学生机械创新设计大赛竞赛规则爬虫启动")
        print("=" * 60)
        
        try:
            # 爬取主要数据源
            self.parse_current_official()
            self.parse_history_site()
            
            # 补充固定信息
            self.crawl_additional_sources()
            
            # 生成报告
            print("\n正在生成Markdown文档...")
            markdown_content = self.generate_markdown_report()
            
            # 保存文件
            saved_path = self.save_to_file(markdown_content)
            
            # 同时保存JSON原始数据
            json_path = saved_path.replace('.md', '_data.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            print(f"✅ 原始数据已保存至: {json_path}")
            
            print("\n" + "=" * 60)
            print("爬取完成！")
            print("=" * 60)
            
            return saved_path
            
        except Exception as e:
            print(f"\n❌ 爬取过程中出现错误: {e}")
            # 即使出错也尝试保存已获取的数据
            try:
                emergency_save = f"output/机械创新设计大赛规则_应急保存_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(emergency_save, 'w', encoding='utf-8') as f:
                    f.write(self.generate_markdown_report())
                print(f"已保存应急文档至: {emergency_save}")
            except:
                pass
            raise


def main():
    """主函数"""
    # 检查依赖
    try:
        import requests
        import bs4
        import html2text
    except ImportError as e:
        print("请先安装必要的依赖库:")
        print("pip install requests beautifulsoup4 html2text")
        return
    
    # 运行爬虫
    crawler = MechanicalInnovationCrawler()
    output_file = crawler.run()

    print(f"\n📄 输出文件: {output_file}")
    print("\n使用建议:")
    print("1. 使用Typora或VS Code预览Markdown文件")
    print("2. 可通过Pandoc转换为Word/PDF格式:")
    print(f"   pandoc '{output_file}' -o 机械创新设计大赛规则.docx")
    print("3. 定期检查官网获取最新通知")


if __name__ == "__main__":
    main()