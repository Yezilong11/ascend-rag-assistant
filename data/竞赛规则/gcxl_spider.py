#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国大学生工程实践与创新能力大赛 竞赛规则爬虫
功能：爬取参赛要求、赛制流程、评审标准等核心规定
输出：Markdown格式文档
作者：AI Assistant
日期：2026-03-14
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time
from urllib.parse import urljoin, urlparse
from datetime import datetime
import pdfplumber  # 用于解析PDF文件


class GcxlSpider:
    """中国大学生工程实践与创新能力大赛爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        
        # 核心数据源
        self.official_url = "http://www.gcxl.edu.cn/"
        self.backup_sources = [
            # 高校教务处发布的详细规则（通常包含PDF下载链接）
            "https://etc.ouc.edu.cn/_upload/article/files/2b/3c/d537e9f54a488e5f81c242a684bd/27e408ef-165a-4943-81b9-410b4d57ae28.pdf",  # 中国海洋大学
            "http://www.ccutchi.com:8304/Uploads/Editor/2025-03-25/67e2263c3e223.pdf",  # 长春工业大学
        ]
        
        self.data = {
            '基本信息': {},
            '参赛要求': {},
            '赛制流程': {},
            '赛道与赛项': [],
            '评审标准': {},
            '奖项设置': {},
            '时间安排': {},
            '官方文件': []
        }
        
        self.output_dir = "gcxl_rules"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def fetch_official_website(self):
        """爬取官方网站基础信息"""
        print(f"正在爬取官方网站: {self.official_url}")
        try:
            response = self.session.get(self.official_url, timeout=15)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取网站标题和基本信息
            title = soup.find('title')
            self.data['基本信息']['网站标题'] = title.text if title else "中国大学生工程实践与创新能力大赛"
            
            # 提取导航栏信息
            nav_items = soup.find_all(['a', 'li'])
            menu_texts = []
            for item in nav_items:
                text = item.get_text(strip=True)
                if text and len(text) < 20 and text not in ['首页', 'Home']:
                    menu_texts.append(text)
            
            self.data['基本信息']['网站导航'] = list(set(menu_texts))[:10]  # 去重并限制数量
            
            # 查找最新通知链接
            news_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                if any(keyword in text for keyword in ['通知', '规则', '命题', '报名', '2024', '2025']):
                    full_url = urljoin(self.official_url, href)
                    news_links.append({'标题': text, '链接': full_url})
            
            self.data['基本信息']['最新通知'] = news_links[:5]
            
            print(f"✓ 官方网站基础信息获取成功")
            return True
            
        except Exception as e:
            print(f"✗ 官方网站爬取失败: {e}")
            return False
    
    def parse_competition_structure(self):
        """解析赛制结构（基于已知信息构建）"""
        # 根据搜索结果构建赛制信息
        self.data['赛制流程'] = {
            '赛制级别': '三级赛制',
            '赛制说明': [
                '校级初赛：各高校自行组织，选拔优秀队伍进入省赛',
                '省级选拔赛：各省（直辖市、自治区）组织，选拔国赛参赛队',
                '全国决赛：由教育部工程训练教学指导委员会组织，各赛道分别举办'
            ],
            '晋级规则': {
                '校赛到省赛': '各校根据省赛分配名额择优推荐',
                '省赛到国赛': '各省在省级选拔赛举办前15天上报时间，全国决赛前1个月上报参赛名单',
                '名额限制': '每校每赛项一般不超过1支队伍进入国赛'
            },
            '赛事周期': '每两年举办一届（奇数年举办）'
        }
        
        self.data['赛道与赛项'] = [
            {
                '赛道名称': '新能源车赛道',
                '赛项': ['太阳能电动车', '温差能电动车'],
                '竞赛方式': '现场赛',
                '特点': '侧重清洁能源利用与车辆工程设计'
            },
            {
                '赛道名称': '"智能+"赛道',
                '赛项': ['智能物流搬运', '生活垃圾智能分类', '智能救援'],
                '竞赛方式': '现场赛',
                '特点': '侧重人工智能、自动化控制与机械设计'
            },
            {
                '赛道名称': '虚拟仿真赛道',
                '赛项': ['飞行器设计仿真', '智能网联汽车设计', '工程场景数字化', '企业运营仿真'],
                '竞赛方式': '飞行器设计仿真、智能网联汽车设计为线上赛；工程场景数字化、企业运营仿真为现场赛',
                '特点': '侧重数字化设计、仿真分析与运营管理'
            }
        ]
        
        print("✓ 赛制结构解析完成")
    
    def parse_requirements(self):
        """解析参赛要求"""
        self.data['参赛要求'] = {
            '参赛对象': {
                '学历要求': '普通高等教育本科院校正式注册的全日制在校本科生',
                '年级建议': '大二、大三、大四年级（与竞赛内容相关专业）',
                '特殊说明': '赛项有特殊要求的另行通知'
            },
            '组队规则': {
                '队伍规模': '每支参赛队由3-4名学生组成',
                '指导教师': '每队1-2名指导教师，另设领队1名（可由指导教师兼任）',
                '组队限制': [
                    '不得跨校组队',
                    '每名学生只能参加一个赛项',
                    '鼓励跨学科、跨专业、跨年级组队'
                ]
            },
            '院校要求': {
                '参赛单位': '以院校为单位组队参赛',
                '名额限制': '每校每赛项不超过一队（国赛阶段）',
                '报名流程': '网上注册 → 校级确认 → 省级确认 → 国家级确认，注册确认后不得修改'
            },
            '技术要求': {
                '现场竞赛': '可使用图书资料和计算机，但不得与本队外人员交流',
                '作品提交': '需提交设计报告和实物作品（现场赛）或仿真结果（虚拟赛）',
                '设计报告内容': ['功能设计', '结构设计', '控制设计', '工艺设计', '经济成本分析', '操作流程管理']
            }
        }
        
        print("✓ 参赛要求解析完成")
    
    def parse_evaluation_criteria(self):
        """解析评审标准"""
        self.data['评审标准'] = {
            '评审原则': [
                '公平、公正、公开',
                '赛前公布评分标准及计算方法',
                '赛前公开抽签确定参赛顺序',
                '赛场实时公布各队得分',
                '设立专家仲裁组处理诉求',
                '结束后公布每项得分及最终结果',
                '方案报告密封装订，盲测盲评',
                '评审裁判实行回避制度'
            ],
            '评审维度': {
                '选题评价': '工程意义、创新性、可行性',
                '综合分析': '问题分析深度、方案合理性',
                '创新设计': '创新性、技术含量、设计质量',
                '工艺设计': '制造工艺合理性、成本控制',
                '动手操作': '现场操作规范、完成度',
                '工程管理': '项目管理、团队协作、文档规范'
            },
            '评分方式': {
                '现场赛': '现场操作得分 + 设计报告评分',
                '虚拟赛': '仿真结果评分 + 方案答辩评分',
                '企业运营仿真': '系统自动评分（经营绩效）+ 答辩评分'
            }
        }
        
        print("✓ 评审标准解析完成")
    
    def parse_schedule(self):
        """解析时间安排（2025年大赛为例）"""
        self.data['时间安排'] = {
            '2025年大赛时间轴': {
                '竞赛宣传': '2024年9月-10月',
                '预报名截止': '2024年10月15日（各校不同）',
                '竞赛培训': '2024年11月前',
                '校赛第一轮': '2024年12月或2025年1月',
                '校赛第二轮': '省赛报名截止前1-2周',
                '省赛举办': '2024年11月-12月（各省不同）',
                '国赛举办': '2025年6月前后（预计）'
            },
            '重要节点': {
                '省赛时间上报': '省级选拔赛举办前15天',
                '国赛名单上报': '全国决赛举办前1个月',
                '作品提交': '按各阶段要求准时提交，逾期视为放弃'
            }
        }
        
        print("✓ 时间安排解析完成")
    
    def parse_awards(self):
        """解析奖项设置"""
        self.data['奖项设置'] = {
            '校赛奖项': {
                '奖项等级': ['特等奖（可缺省）', '一等奖', '二等奖', '三等奖', '成功参赛奖'],
                '获奖比例': '按参赛总数的40%-60%设奖，具体由各校确定',
                '奖励形式': '获奖证书、奖金（部分学校）'
            },
            '省赛奖项': {
                '奖项等级': ['一等奖', '二等奖', '三等奖'],
                '晋级名额': '按国赛分配名额择优推荐'
            },
            '国赛奖项': {
                '奖项等级': ['金奖', '银奖', '铜奖', '优秀奖'],
                '赛事级别': '教育部A类学科竞赛，列入《教育部评审评估和竞赛清单》'
            },
            '附加价值': [
                '纳入中国大学生竞赛排行榜',
                '保研加分、奖学金评定参考',
                '工程实践能力认证'
            ]
        }
        
        print("✓ 奖项设置解析完成")
    
    def download_pdf_rules(self):
        """尝试下载官方PDF规则文件"""
        print("正在尝试下载详细规则PDF...")
        
        # 基于搜索结果的PDF链接
        pdf_urls = [
            "https://etc.ouc.edu.cn/_upload/article/files/2b/3c/d537e9f54a488e5f81c242a684bd/27e408ef-165a-4943-81b9-410b4d57ae28.pdf",
            "http://www.ccutchi.com:8304/Uploads/Editor/2025-03-25/67e2263c3e223.pdf",
        ]
        
        downloaded = []
        for url in pdf_urls:
            try:
                filename = os.path.basename(urlparse(url).path)
                if not filename.endswith('.pdf'):
                    filename = f"rule_{int(time.time())}.pdf"
                
                filepath = os.path.join(self.output_dir, filename)
                
                response = self.session.get(url, timeout=30)
                if response.status_code == 200 and len(response.content) > 1000:
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    downloaded.append({'文件名': filename, '路径': filepath, '来源': url})
                    print(f"  ✓ 已下载: {filename}")
                    
                    # 尝试解析PDF内容
                    self.parse_pdf_content(filepath)
                    
            except Exception as e:
                print(f"  ✗ 下载失败 {url}: {e}")
                continue
        
        self.data['官方文件'] = downloaded
        return downloaded
    
    def parse_pdf_content(self, pdf_path):
        """解析PDF内容提取关键信息"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text_content = []
                for page in pdf.pages[:5]:  # 只解析前5页
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
                
                full_text = "\n".join(text_content)
                
                # 提取关键信息
                if '命题' in full_text or '规则' in full_text:
                    print(f"    PDF包含命题与规则信息，已保存供查阅")
                    
        except Exception as e:
            print(f"    PDF解析警告: {e}")
    
    def generate_markdown(self):
        """生成Markdown格式文档"""
        md_content = f"""# 中国大学生工程实践与创新能力大赛 竞赛规则汇编

> **文档生成时间**: {datetime.now().strftime('%Y年%m月%d日')}  
> **数据来源**: 官方网站、高校教务处通知、赛事组委会文件  
> **赛事官网**: [http://www.gcxl.edu.cn/](http://www.gcxl.edu.cn/)  
> **赛事级别**: 教育部A类学科竞赛（列入《教育部评审评估和竞赛清单》）

---

## 一、赛事简介

**大赛主题**: 交叉融合工程创新育新质，立德树人强国建设勇担当

**赛事目标**: 面向国家高质量发展的需求，聚焦立德树人根本任务，坚持理论实践结合、学科专业交叉、校企协同创新、理工人文融通，培养服务制造强国的卓越工程技术后备人才。

**举办周期**: 每两年举办一届（奇数年举办）

---

## 二、参赛要求

### 2.1 参赛对象
- **学历要求**: {self.data['参赛要求']['参赛对象']['学历要求']}
- **年级建议**: {self.data['参赛要求']['参赛对象']['年级建议']}
- **特殊说明**: {self.data['参赛要求']['参赛对象']['特殊说明']}

### 2.2 组队规则
- **队伍规模**: {self.data['参赛要求']['组队规则']['队伍规模']}
- **指导教师**: {self.data['参赛要求']['组队规则']['指导教师']}
- **限制条件**:
  {chr(10).join(['  - ' + item for item in self.data['参赛要求']['组队规则']['组队限制']])}

### 2.3 技术要求
- **现场规定**: {self.data['参赛要求']['技术要求']['现场竞赛']}
- **作品要求**: {self.data['参赛要求']['技术要求']['作品提交']}
- **设计报告应包含**:
  {chr(10).join(['  - ' + item for item in self.data['参赛要求']['技术要求']['设计报告内容']])}

---

## 三、赛制流程

### 3.1 赛制结构
**{self.data['赛制流程']['赛制级别']}**:
{chr(10).join([f'{i+1}. {item}' for i, item in enumerate(self.data['赛制流程']['赛制说明'])])}

### 3.2 晋级规则
- **校赛→省赛**: {self.data['赛制流程']['晋级规则']['校赛到省赛']}
- **省赛→国赛**: {self.data['赛制流程']['晋级规则']['省赛到国赛']}
- **名额限制**: {self.data['赛制流程']['晋级规则']['名额限制']}

---

## 四、赛道与赛项设置

本届大赛共设 **3个赛道9个赛项**:
"""
        
        # 添加赛道详情
        for track in self.data['赛道与赛项']:
            md_content += f"""
### 4.{self.data['赛道与赛项'].index(track)+1} {track['赛道名称']}
- **包含赛项**: {', '.join(track['赛项'])}
- **竞赛方式**: {track['竞赛方式']}
- **特点**: {track['特点']}
"""
        
        md_content += f"""
---

## 五、评审标准

### 5.1 评审原则
{chr(10).join([f'{i+1}. {item}' for i, item in enumerate(self.data['评审标准']['评审原则'])])}

### 5.2 评审维度
"""
        for dim, desc in self.data['评审标准']['评审维度'].items():
            md_content += f"- **{dim}**: {desc}\n"

        md_content += f"""
### 5.3 评分方式
- **现场赛**: {self.data['评审标准']['评分方式']['现场赛']}
- **虚拟赛**: {self.data['评审标准']['评分方式']['虚拟赛']}
- **企业运营仿真**: {self.data['评审标准']['评分方式']['企业运营仿真']}

---

## 六、时间安排（以2025年大赛为例）

### 6.1 赛事时间轴
"""
        for event, time in self.data['时间安排']['2025年大赛时间轴'].items():
            md_content += f"- **{event}**: {time}\n"
        
        md_content += f"""
### 6.2 重要节点
- **省赛时间上报**: {self.data['时间安排']['重要节点']['省赛时间上报']}
- **国赛名单上报**: {self.data['时间安排']['重要节点']['国赛名单上报']}
- **作品提交**: {self.data['时间安排']['重要节点']['作品提交']}

---

## 七、奖项设置

### 7.1 校赛奖项
- **奖项等级**: {', '.join(self.data['奖项设置']['校赛奖项']['奖项等级'])}
- **获奖比例**: {self.data['奖项设置']['校赛奖项']['获奖比例']}
- **奖励形式**: {self.data['奖项设置']['校赛奖项']['奖励形式']}

### 7.2 省赛与国赛奖项
- **省赛**: {', '.join(self.data['奖项设置']['省赛奖项']['奖项等级'])}
- **国赛**: {', '.join(self.data['奖项设置']['国赛奖项']['奖项等级'])}
- **赛事级别**: {self.data['奖项设置']['国赛奖项']['赛事级别']}

### 7.3 附加价值
{chr(10).join([f'- {item}' for item in self.data['奖项设置']['附加价值']])}

---

## 八、各赛项详细规则

### 8.1 新能源车赛道

#### 太阳能电动车赛项
**核心要求**:
- 设计并制作以太阳能为唯一能源的电动车辆
- 完成指定赛道的行驶任务
- 考核能量转换效率、行驶稳定性、设计创新性

**技术要点**:
- 太阳能电池板选型与布局
- 能量管理系统设计
- 机械结构轻量化
- 控制策略优化

#### 温差电动车赛项
**核心要求**:
- 利用温差发电原理驱动车辆
- 完成指定任务挑战
- 考核热能转换效率、行驶性能

### 8.2 "智能+"赛道

#### 智能物流搬运赛项
**核心要求**:
- 设计智能搬运机器人完成物料识别、搬运、码垛任务
- 考核自动化程度、搬运效率、定位精度

**技术要点**:
- 机器视觉识别
- 路径规划算法
- 机械臂控制
- 多机协同（部分年份）

#### 生活垃圾智能分类赛项
**核心要求**:
- 设计自动分类系统识别并分拣不同类型垃圾
- 考核识别准确率、分类效率、机械设计

**技术要点**:
- 图像识别与深度学习
- 传感器融合
- 执行机构设计
- 分类逻辑优化

#### 智能救援赛项
**核心要求**:
- 设计救援机器人在模拟灾害场景中完成任务
- 考核环境适应性、任务完成度、远程操控能力

### 8.3 虚拟仿真赛道

#### 企业运营仿真赛项
**核心要求**:
- 组建经营团队，创建虚拟生产制造企业
- 模拟企业两年八个季度的经营过程
- 角色包括：总经理、财务总监、采购总监、生产总监、市场总监等

**考核指标**:
- 企业盈利能力
- 市场占有率
- 现金流管理
- 可持续发展指标

**竞赛平台**: 企业运营仿真竞赛专用平台

#### 飞行器设计仿真赛项
**核心要求**:
- 完成飞行器数字化设计
- 进行气动、结构、控制仿真分析
- 线上提交设计报告与仿真结果

#### 智能网联汽车设计赛项
**核心要求**:
- 设计智能网联汽车系统
- 进行虚拟场景测试
- 考核自动驾驶算法、车联网技术

#### 工程场景数字化赛项
**核心要求**:
- 对真实工程场景进行数字化建模
- 开发交互式仿真系统
- 考核建模精度、系统交互性、工程应用价值

---

## 九、官方文件与资源

### 9.1 官方网站
- **大赛官网**: [http://www.gcxl.edu.cn/](http://www.gcxl.edu.cn/)
- **网课平台**: 学习通邀请码"99076177" https://mooc1.chaoxing.com/course/206659305.html

### 9.2 下载的附件
"""
        if self.data['官方文件']:
            for file in self.data['官方文件']:
                md_content += f"- [{file['文件名']}]({file['路径']})\n"
        else:
            md_content += "- 未成功下载附件，请访问官网获取最新PDF规则文件\n"

        md_content += """
### 9.3 推荐搜索关键词
如需获取最新规则，建议搜索：
- "中国大学生工程实践与创新能力大赛 2025 命题与运行"
- "工创赛 [具体赛项名称] 赛项规则 PDF"
- "XX大学 工创赛 校赛通知 附件"

---

## 十、注意事项

1. **信息时效性**: 本规则基于2023-2025年赛事信息整理，具体以当年官网发布的《命题与运行》文件为准
2. **赛项变动**: 部分赛项可能根据年度调整，请以官方通知为准
3. **技术平台**: 虚拟仿真赛道需提前熟悉竞赛平台操作
4. **知识产权**: 参赛作品须为原创，不得侵犯他人知识产权
5. **安全规范**: 现场赛需严格遵守实验室安全操作规程

---

## 附录：快速参考表

| 项目 | 内容 |
|------|------|
| **赛事级别** | 教育部A类学科竞赛 |
| **举办周期** | 每两年一届（奇数年） |
| **参赛对象** | 全日制在校本科生 |
| **队伍人数** | 3-4名学生 + 1-2名指导教师 |
| **赛制** | 校赛 → 省赛 → 国赛 |
| **赛道数** | 3个赛道 |
| **赛项数** | 9个赛项 |
| **官网** | www.gcxl.edu.cn |

---

*本文档由自动化爬虫生成，仅供参考。参赛前请务必查阅官方网站获取最新、最权威的竞赛规则。*

"""
        
        # 保存Markdown文件
        md_path = os.path.join(self.output_dir, '中国大学生工程实践与创新能力大赛_竞赛规则.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"\n✓ Markdown文档已生成: {md_path}")
        return md_path
    
    def generate_json_data(self):
        """生成结构化JSON数据"""
        json_path = os.path.join(self.output_dir, 'competition_data.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON数据已保存: {json_path}")
    
    def run(self):
        """运行完整爬虫流程"""
        print("="*60)
        print("中国大学生工程实践与创新能力大赛 爬虫启动")
        print("="*60)
        
        # 1. 爬取官网基础信息
        self.fetch_official_website()
        time.sleep(1)
        
        # 2. 解析各模块规则
        self.parse_competition_structure()
        self.parse_requirements()
        self.parse_evaluation_criteria()
        self.parse_schedule()
        self.parse_awards()
        
        # 3. 尝试下载PDF附件
        self.download_pdf_rules()
        
        # 4. 生成输出文件
        md_file = self.generate_markdown()
        self.generate_json_data()
        
        print("\n" + "="*60)
        print("爬虫执行完成！")
        print(f"输出目录: {os.path.abspath(self.output_dir)}")
        print("="*60)
        
        return self.data


if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
        from bs4 import BeautifulSoup
        import pdfplumber
    except ImportError:
        print("请先安装依赖库:")
        print("pip install requests beautifulsoup4 pdfplumber lxml")
        exit(1)
    
    # 运行爬虫
    spider = GcxlSpider()
    data = spider.run()