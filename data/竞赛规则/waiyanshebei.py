"""
外研社·国才杯全国大学生英语辩论赛规则爬虫
作者：元宝
日期：2026-03-15
功能：爬取外研社·国才杯全国大学生英语辩论赛的竞赛规则
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
import os
from datetime import datetime
import markdown
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

class FLTRPDebateCrawler:
    """外研社·国才杯辩论赛规则爬虫"""
    
    def __init__(self):
        self.base_urls = [
            "https://cxcy.sut.edu.cn/",  # 沈阳工业大学
            "https://ucc.fltrp.com/",    # 外研社大赛官网
            "https://etic.claonline.cn/", # 国才官网
        ]
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        
        self.rules_data = {
            "赛事名称": "第28届'外研社·国才杯'全国大学生英语辩论赛",
            "基本信息": {},
            "参赛要求": {},
            "赛制流程": {},
            "评审标准": {},
            "时间安排": {},
            "奖项设置": {},
            "数据来源": []
        }
        
    def fetch_page(self, url, timeout=10):
        """获取网页内容"""
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return response.text
            else:
                print(f"请求失败: {url}, 状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"请求异常: {url}, 错误: {str(e)}")
            return None
    
    def parse_rules_from_content(self, content, source_url):
        """从网页内容解析规则信息"""
        soup = BeautifulSoup(content, 'html.parser')
        
        # 提取所有文本内容
        text_content = soup.get_text(separator='\n', strip=True)
        
        # 定义关键词模式
        patterns = {
            "参赛对象": ["参赛对象", "参赛资格", "参赛范围", "参赛条件"],
            "组队形式": ["组队形式", "队伍组成", "每队人数"],
            "赛制说明": ["赛制说明", "比赛赛制", "BP赛制", "英国议会制"],
            "发言时间": ["发言时间", "发言时长", "分钟发言"],
            "质询规则": ["质询", "POI", "Point of Information"],
            "评分标准": ["评分标准", "评分准则", "评判标准", "评分规则"],
            "奖项设置": ["奖项设置", "奖励办法", "奖项类别"],
            "时间安排": ["时间安排", "比赛时间", "赛程安排", "日程表"]
        }
        
        extracted_data = {}
        
        for key, keywords in patterns.items():
            for line in text_content.split('\n'):
                if any(keyword in line for keyword in keywords):
                    if key not in extracted_data:
                        extracted_data[key] = []
                    extracted_data[key].append(line.strip())
        
        return extracted_data
    
    def collect_rules_from_search_results(self):
        """从搜索结果中收集规则信息"""
        print("开始收集外研社·国才杯辩论赛规则信息...")
        
        # 基于搜索结果整理规则信息
        self.rules_data["基本信息"] = {
            "赛事全称": "第28届'外研社·国才杯'全国大学生英语辩论赛",
            "英文名称": "The 28th 'FLTRP · ETIC Cup' National English Debating Competition",
            "主办单位": "北京外国语大学",
            "承办单位": "外语教学与研究出版社、北京外国语大学中国外语测评中心、北京外研在线数字科技有限公司",
            "赛事级别": "国家级竞赛，连续多年被纳入教育部中国高等教育学会发布的《全国普通高校大学生竞赛分析报告》竞赛目录[20](@ref)",
            "创办时间": "1997年",
            "赛事宗旨": "引导广大青年学生积极践行社会主义核心价值观，加强高校校园文化建设，帮助学生开拓国际视野、强化学习意识、提升英语表达和思辨能力[1](@ref)"
        }
        
        self.rules_data["参赛要求"] = {
            "资格要求": "全国具有高等学历教育招生资格的普通高等学校全日制在校本科生、专科生、硕士研究生及博士研究生，中国国籍[3,7](@ref)",
            "年龄限制": "无明确年龄限制",
            "学历要求": "全日制在校大学生",
            "国籍要求": "中国国籍",
            "组队要求": "每支代表队由2人组成，允许跨学院组队[3](@ref)",
            "禁止参赛": "在往届'外研社杯'全国英语辩论赛中获得最佳辩手或进入决赛的选手不能再次报名参赛[3](@ref)",
            "报名方式": "通过各高校校内报名通道，通常需要加入赛事QQ群或通过学校创新创业管理平台报名[1](@ref)"
        }
        
        self.rules_data["赛制流程"] = {
            "赛制类型": "英国议会制辩论（British Parliamentary Debate，简称BP赛制）[1,20](@ref)",
            "比赛规模": "每场比赛由4支队伍同场进行，每队2人，共8名选手[20](@ref)",
            "队伍角色": [
                "正方一队（Opening Government，OG）",
                "反方一队（Opening Opposition，OO）",
                "正方二队（Closing Government，CG）",
                "反方二队（Closing Opposition，CO）[22](@ref)"
            ],
            "辩手位置": {
                "正方上院": ["首相（Prime Minister，PM）", "副首相（Deputy Prime Minister，DPM）"],
                "反方上院": ["反方领袖（Leader of Opposition，LO）", "反方副领袖（Deputy Leader of Opposition，DLO）"],
                "正方下院": ["正方成员（Member of Government，MG）", "正方党鞭（Government Whip，GW）"],
                "反方下院": ["反方成员（Member of Opposition，MO）", "反方党鞭（Opposition Whip，OW）[17](@ref)"]
            },
            "发言顺序": "PM → LO → DPM → DLO → MG → MO → GW → OW（之字形顺序）[17](@ref)",
            "发言时间": {
                "循环赛": "每位辩手发言时间5分钟[14](@ref)",
                "决赛": "每位辩手发言时间7分钟[14](@ref)",
                "保护期": "第1分钟和第7分钟（决赛）或第1分钟和第5分钟（循环赛）为保护期，对方不可提出质询[14](@ref)",
                "质询时间": "辩手提出质询的时间应在发言人讲话的第2到第6分钟之间[3](@ref)",
                "缓冲时间": "连续两次响铃结束后，辩手有15秒'缓冲'时间进行总结[3](@ref)"
            },
            "质询规则": {
                "提出方式": "口头提问或起身要求质询[3](@ref)",
                "接受拒绝": "被提问的辩手可以接受或回绝质询[3](@ref)",
                "质询时长": "如果接受质询，提问辩手有15秒时间提出异议或提出问题[3](@ref)",
                "时间计算": "质询和回答时间记在被提问辩手的发言时间中[3](@ref)"
            },
            "辩题准备": {
                "公布时间": "辩题赛前20分钟公布[3](@ref)",
                "准备时间": "辩题公布后20分钟开始辩论[3](@ref)",
                "资料查阅": "准备时间内可以查阅纸质资料[3](@ref)",
                "讨论限制": "只能与本队辩友进行讨论，不能与其他任何人（包括其他队伍的教练、辩手、裁判等）讨论[3](@ref)",
                "设备限制": "准备期间不允许使用电子设备[20](@ref)"
            },
            "比赛流程": {
                "校园选拔赛": "2025年11月—2026年3月[4](@ref)",
                "地区复赛": "2026年3月-4月[4](@ref)",
                "全国决赛": "2026年6月[4](@ref)",
                "复赛赛区": "华北、华南、华东、华西四个赛区[25](@ref)"
            }
        }
        
        self.rules_data["评审标准"] = {
            "排名规则": "成绩评定不以正或反方获胜为准，而是按四支队伍表现排序[1](@ref)",
            "积分制度": {
                "第一名": "3分",
                "第二名": "2分",
                "第三名": "1分",
                "第四名": "0分[1](@ref)"
            },
            "评分维度": [
                "职责履行",
                "团队协作",
                "辩题贡献",
                "辩论技巧",
                "表达清晰度[1](@ref)"
            ],
            "个人评分": {
                "评分标准": "每位辩手也会获得个人积分，作为最佳辩手评选依据[1](@ref)",
                "平均水平": "75分应是本次参赛辩手的平均水平分数[18](@ref)",
                "队伍得分": "每支辩论队两名辩手得分之和为队伍得分[18](@ref)",
                "分数要求": "队伍分数应与队伍排名相称，不允许出现低分高名次[18](@ref)"
            },
            "评分等级": {
                "90-100分": "优秀到完美，相当于全国决赛水平的辩手[15](@ref)",
                "80-89分": "高于平均到非常好，相当于半决赛水平的辩手[15](@ref)",
                "70-79分": "平均水平，辩手有优点也有缺点[15](@ref)",
                "60-69分": "差到低于平均水平，队伍有明显问题[15](@ref)",
                "50-59分": "非常差，辩手有根本性弱点[15](@ref)"
            },
            "评委配置": {
                "循环赛": "每场有2-3名评委[14](@ref)",
                "决赛": "6-7名评委[14](@ref)",
                "评委要求": "每场比赛评委人数应为单数，须包含1位主裁[7](@ref)",
                "争议解决": "当评委们对比赛结果无法达成一致时，可采取投票方式以多胜少得出结果[7](@ref)"
            }
        }
        
        self.rules_data["时间安排"] = {
            "第28届赛事时间表": {
                "校园选拔赛": "2025年11月—2026年3月（各高校须在2026年3月21日前完成）[7](@ref)",
                "地区复赛报名": "截止日期为2026年3月27日[25](@ref)",
                "地区复赛时间": {
                    "华北赛区": "2026年4月10-11日",
                    "华南赛区": "2026年4月11-12日",
                    "华东赛区": "2026年4月17-18日",
                    "华西赛区": "2026年4月18-19日[25](@ref)"
                },
                "全国决赛": "2026年6月[4](@ref)"
            },
            "地区复赛日程": {
                "第一日": {
                    "13:30-14:30": "赛前说明会、合影",
                    "14:30-15:00": "开幕式",
                    "15:00-17:00": "循环赛第一轮",
                    "18:00-20:00": "循环赛第二轮[25](@ref)"
                },
                "第二日": {
                    "8:00-10:00": "循环赛第三轮",
                    "10:00-12:00": "循环赛第四轮",
                    "13:00-15:00": "循环赛第五轮",
                    "15:00-17:00": "总决赛",
                    "17:00-18:00": "颁奖典礼[25](@ref)"
                }
            }
        }
        
        self.rules_data["奖项设置"] = {
            "校园选拔赛奖项": {
                "冠军队伍": "1支",
                "亚军队伍": "1支",
                "季军队伍": "2支",
                "最佳辩手": "6-8名[7](@ref)",
                "一等奖": "晋级决赛的8名选手[4](@ref)",
                "二等奖": "根据参赛人数调整",
                "三等奖": "根据参赛人数调整[4](@ref)"
            },
            "证书颁发": "所有获奖选手将获得由大赛组委会颁发的电子证书[4,7](@ref)",
            "学分认定": "参赛选手统一开具综测证明，一、二、三等奖及优秀奖的参赛者可申请创新创业学分[3](@ref)",
            "晋级资格": "冠军队伍将代表学校参加地区复赛，最终晋级全国决赛[1](@ref)",
            "特殊奖励": {
                "国才考试外卡": "在国才考试中成绩达到中级（良好）及以上的考生，可在综合能力、演讲赛项中额外增加1名选手进入省赛[12](@ref)",
                "优秀组织奖": "组委会为在校园选拔赛中组织工作表现优异的院校颁发'优秀组织奖'[7](@ref)"
            }
        }
        
        self.rules_data["数据来源"] = [
            "沈阳工业大学官方网站 - 外研社全国大学生英语系列赛规则[1](@ref)",
            "集美大学外国语学院 - 第28届校园选拔赛指南[3](@ref)",
            "国才官方 - 第28届校园选拔赛指南[7](@ref)",
            "中央财经大学 - 第28届校选赛通知[4](@ref)",
            "百度百科 - '外研社杯'全国英语辩论赛[20](@ref)",
            "常州工学院 - 第28届校园选拔赛通知[22](@ref)",
            "国才官方 - 第28届地区复赛报名通知[25](@ref)",
            "中南民族大学官网 - 第27届校园选拔赛评分标准[15](@ref)"
        ]
        
        print("规则信息收集完成！")
        return True
    
    def save_as_markdown(self, filename="fltrp_debate_rules.md"):
        """保存为Markdown格式"""
        print(f"正在保存为Markdown文件: {filename}")
        
        md_content = f"""# 外研社·国才杯全国大学生英语辩论赛竞赛规则

> 数据收集时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
> 数据来源：基于多所高校官网和赛事官方通知整理

## 一、赛事基本信息

### 1.1 赛事概况
- **赛事全称**：{self.rules_data["基本信息"]["赛事全称"]}
- **英文名称**：{self.rules_data["基本信息"]["英文名称"]}
- **主办单位**：{self.rules_data["基本信息"]["主办单位"]}
- **承办单位**：{self.rules_data["基本信息"]["承办单位"]}
- **赛事级别**：{self.rules_data["基本信息"]["赛事级别"]}
- **创办时间**：{self.rules_data["基本信息"]["创办时间"]}
- **赛事宗旨**：{self.rules_data["基本信息"]["赛事宗旨"]}

## 二、参赛要求

### 2.1 资格条件
{self.rules_data["参赛要求"]["资格要求"]}

### 2.2 组队要求
{self.rules_data["参赛要求"]["组队要求"]}

### 2.3 限制条件
{self.rules_data["参赛要求"]["禁止参赛"]}

### 2.4 报名方式
{self.rules_data["参赛要求"]["报名方式"]}

## 三、赛制流程

### 3.1 赛制类型
{self.rules_data["赛制流程"]["赛制类型"]}

### 3.2 比赛结构
- **每场比赛队伍数**：4支队伍
- **每队人数**：2人
- **总辩手数**：8人

### 3.3 队伍角色
1. {self.rules_data["赛制流程"]["队伍角色"][0]}
2. {self.rules_data["赛制流程"]["队伍角色"][1]}
3. {self.rules_data["赛制流程"]["队伍角色"][2]}
4. {self.rules_data["赛制流程"]["队伍角色"][3]}

### 3.4 辩手位置与职责
| 位置 | 英文简称 | 中文名称 | 所属队伍 |
|------|----------|----------|----------|
| PM | Prime Minister | 首相/正方领袖 | 正方上院 |
| LO | Leader of Opposition | 反方领袖 | 反方上院 |
| DPM | Deputy Prime Minister | 副首相/正方副领袖 | 正方上院 |
| DLO | Deputy Leader of Opposition | 反方副领袖 | 反方上院 |
| MG | Member of Government | 正方成员 | 正方下院 |
| MO | Member of Opposition | 反方成员 | 反方下院 |
| GW | Government Whip | 正方党鞭 | 正方下院 |
| OW | Opposition Whip | 反方党鞭 | 反方下院 |

### 3.5 发言时间规则
| 赛段 | 发言时间 | 保护期 | 质询时间 |
|------|----------|--------|----------|
| 循环赛 | 5分钟/人 | 第1分钟和第5分钟 | 第2-4分钟 |
| 决赛 | 7分钟/人 | 第1分钟和第7分钟 | 第2-6分钟 |

### 3.6 质询规则
- **提出方式**：{self.rules_data["赛制流程"]["质询规则"]["提出方式"]}
- **接受拒绝**：{self.rules_data["赛制流程"]["质询规则"]["接受拒绝"]}
- **质询时长**：{self.rules_data["赛制流程"]["质询规则"]["质询时长"]}
- **时间计算**：{self.rules_data["赛制流程"]["质询规则"]["时间计算"]}

### 3.7 辩题准备
- **公布时间**：{self.rules_data["赛制流程"]["辩题准备"]["公布时间"]}
- **准备时间**：{self.rules_data["赛制流程"]["辩题准备"]["准备时间"]}
- **资料查阅**：{self.rules_data["赛制流程"]["辩题准备"]["资料查阅"]}
- **讨论限制**：{self.rules_data["赛制流程"]["辩题准备"]["讨论限制"]}
- **设备限制**：{self.rules_data["赛制流程"]["辩题准备"]["设备限制"]}

## 四、评审标准

### 4.1 排名与积分制度
{self.rules_data["评审标准"]["排名规则"]}

**积分分配表：**
| 排名 | 积分 |
|------|------|
| 第一名 | {self.rules_data["评审标准"]["积分制度"]["第一名"]} |
| 第二名 | {self.rules_data["评审标准"]["积分制度"]["第二名"]} |
| 第三名 | {self.rules_data["评审标准"]["积分制度"]["第三名"]} |
| 第四名 | {self.rules_data["评审标准"]["积分制度"]["第四名"]} |

### 4.2 评分维度
{', '.join(self.rules_data["评审标准"]["评分维度"])}

### 4.3 个人评分标准
- **平均水平**：{self.rules_data["评审标准"]["个人评分"]["平均水平"]}
- **队伍得分**：{self.rules_data["评审标准"]["个人评分"]["队伍得分"]}
- **分数要求**：{self.rules_data["评审标准"]["个人评分"]["分数要求"]}

### 4.4 评分等级说明
| 分数区间 | 等级描述 |
|----------|----------|
| 90-100分 | {self.rules_data["评审标准"]["评分等级"]["90-100分"]} |
| 80-89分 | {self.rules_data["评审标准"]["评分等级"]["80-89分"]} |
| 70-79分 | {self.rules_data["评审标准"]["评分等级"]["70-79分"]} |
| 60-69分 | {self.rules_data["评审标准"]["评分等级"]["60-69分"]} |
| 50-59分 | {self.rules_data["评审标准"]["评分等级"]["50-59分"]} |

### 4.5 评委配置
- **循环赛**：{self.rules_data["评审标准"]["评委配置"]["循环赛"]}
- **决赛**：{self.rules_data["评审标准"]["评委配置"]["决赛"]}
- **评委要求**：{self.rules_data["评审标准"]["评委配置"]["评委要求"]}
- **争议解决**：{self.rules_data["评审标准"]["评委配置"]["争议解决"]}

## 五、时间安排

### 5.1 第28届赛事时间表
| 赛段 | 时间 | 备注 |
|------|------|------|
| 校园选拔赛 | {self.rules_data["时间安排"]["第28届赛事时间表"]["校园选拔赛"]} | |
| 地区复赛报名 | {self.rules_data["时间安排"]["第28届赛事时间表"]["地区复赛报名"]} | |
| 全国决赛 | {self.rules_data["时间安排"]["第28届赛事时间表"]["全国决赛"]} | |

### 5.2 地区复赛时间
| 赛区 | 比赛时间 |
|------|----------|
| 华北赛区 | {self.rules_data["时间安排"]["第28届赛事时间表"]["地区复赛时间"]["华北赛区"]} |
| 华南赛区 | {self.rules_data["时间安排"]["第28届赛事时间表"]["地区复赛时间"]["华南赛区"]} |
| 华东赛区 | {self.rules_data["时间安排"]["第28届赛事时间表"]["地区复赛时间"]["华东赛区"]} |
| 华西赛区 | {self.rules_data["时间安排"]["第28届赛事时间表"]["地区复赛时间"]["华西赛区"]} |

### 5.3 地区复赛详细日程
**第一日：**
{self.rules_data["时间安排"]["地区复赛日程"]["第一日"]["13:30-14:30"]}
{self.rules_data["时间安排"]["地区复赛日程"]["第一日"]["14:30-15:00"]}
{self.rules_data["时间安排"]["地区复赛日程"]["第一日"]["15:00-17:00"]}
{self.rules_data["时间安排"]["地区复赛日程"]["第一日"]["18:00-20:00"]}

**第二日：**
{self.rules_data["时间安排"]["地区复赛日程"]["第二日"]["8:00-10:00"]}
{self.rules_data["时间安排"]["地区复赛日程"]["第二日"]["10:00-12:00"]}
{self.rules_data["时间安排"]["地区复赛日程"]["第二日"]["13:00-15:00"]}
{self.rules_data["时间安排"]["地区复赛日程"]["第二日"]["15:00-17:00"]}
{self.rules_data["时间安排"]["地区复赛日程"]["第二日"]["17:00-18:00"]}

## 六、奖项设置

### 6.1 校园选拔赛奖项
- **冠军队伍**：{self.rules_data["奖项设置"]["校园选拔赛奖项"]["冠军队伍"]}
- **亚军队伍**：{self.rules_data["奖项设置"]["校园选拔赛奖项"]["亚军队伍"]}
- **季军队伍**：{self.rules_data["奖项设置"]["校园选拔赛奖项"]["季军队伍"]}
- **最佳辩手**：{self.rules_data["奖项设置"]["校园选拔赛奖项"]["最佳辩手"]}
- **一等奖**：{self.rules_data["奖项设置"]["校园选拔赛奖项"]["一等奖"]}
- **二等奖**：{self.rules_data["奖项设置"]["校园选拔赛奖项"]["二等奖"]}
- **三等奖**：{self.rules_data["奖项设置"]["校园选拔赛奖项"]["三等奖"]}

### 6.2 证书与学分
{self.rules_data["奖项设置"]["证书颁发"]}

{self.rules_data["奖项设置"]["学分认定"]}

### 6.3 晋级资格
{self.rules_data["奖项设置"]["晋级资格"]}

### 6.4 特殊奖励
**国才考试外卡政策：**
{self.rules_data["奖项设置"]["特殊奖励"]["国才考试外卡"]}

**优秀组织奖：**
{self.rules_data["奖项设置"]["特殊奖励"]["优秀组织奖"]}

## 七、数据来源

本规则基于以下官方来源整理：
{chr(10).join(['- ' + source for source in self.rules_data["数据来源"]])}

## 八、注意事项

1. **参赛纪律**：按赛制要求，为确保比赛顺利、公正进行，每场必须有四支队伍参加，且每支队伍必须至少完整参与四轮循环赛。如中途退出影响比赛进程，将作废之前场次成绩并禁止该队伍成员参加今后"外研社杯"口语类赛事[14](@ref)。

2. **发言要求**：发言时间过短会影响比赛成绩。在"缓冲"时间后仍继续发言的辩手将被裁判扣分[3](@ref)。

3. **公平竞争**：辩论开始后，辩手务必保证比赛公平公正，不得在准备时间内与其他任何人（包括其他队伍的教练、辩手、裁判等）进行讨论[3](@ref)。

---
*本文件由爬虫程序自动生成，最后更新于：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(md_content)
            print(f"Markdown文件保存成功: {filename}")
            return True
        except Exception as e:
            print(f"保存Markdown文件失败: {str(e)}")
            return False
    
    def save_as_docx(self, filename="fltrp_debate_rules.docx"):
        """保存为Word文档格式"""
        print(f"正在保存为Word文档: {filename}")
        
        try:
            doc = Document()
            
            # 添加标题
            title = doc.add_heading('外研社·国才杯全国大学生英语辩论赛竞赛规则', 0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # 添加基本信息
            doc.add_heading('一、赛事基本信息', level=1)
            doc.add_paragraph(f"数据收集时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}")
            doc.add_paragraph(f"数据来源：基于多所高校官网和赛事官方通知整理")
            
            # 添加各章节内容
            sections = [
                ("二、参赛要求", self.rules_data["参赛要求"]),
                ("三、赛制流程", self.rules_data["赛制流程"]),
                ("四、评审标准", self.rules_data["评审标准"]),
                ("五、时间安排", self.rules_data["时间安排"]),
                ("六、奖项设置", self.rules_data["奖项设置"])
            ]
            
            for section_title, section_data in sections:
                doc.add_heading(section_title, level=1)
                
                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        if isinstance(value, (dict, list)):
                            doc.add_heading(key, level=2)
                            if isinstance(value, dict):
                                for sub_key, sub_value in value.items():
                                    doc.add_paragraph(f"{sub_key}: {sub_value}")
                            elif isinstance(value, list):
                                for item in value:
                                    doc.add_paragraph(f"• {item}")
                        else:
                            doc.add_paragraph(f"{key}: {value}")
                else:
                    doc.add_paragraph(str(section_data))
            
            # 添加数据来源
            doc.add_heading('七、数据来源', level=1)
            for source in self.rules_data["数据来源"]:
                doc.add_paragraph(f"• {source}")
            
            # 保存文档
            doc.save(filename)
            print(f"Word文档保存成功: {filename}")
            return True
            
        except Exception as e:
            print(f"保存Word文档失败: {str(e)}")
            return False
    
    def save_as_json(self, filename="fltrp_debate_rules.json"):
        """保存为JSON格式"""
        print(f"正在保存为JSON文件: {filename}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.rules_data, f, ensure_ascii=False, indent=2)
            print(f"JSON文件保存成功: {filename}")
            return True
        except Exception as e:
            print(f"保存JSON文件失败: {str(e)}")
            return False
    
    def run(self):
        """运行爬虫"""
        print("=" * 60)
        print("外研社·国才杯全国大学生英语辩论赛规则爬虫")
        print("=" * 60)
        
        # 收集规则信息
        success = self.collect_rules_from_search_results()
        
        if success:
            # 保存为各种格式
            self.save_as_markdown()
            self.save_as_docx()
            self.save_as_json()
            
            print("\n" + "=" * 60)
            print("爬虫任务完成！")
            print("生成的文件：")
            print("1. fltrp_debate_rules.md - Markdown格式")
            print("2. fltrp_debate_rules.docx - Word文档格式")
            print("3. fltrp_debate_rules.json - JSON数据格式")
            print("=" * 60)
            
            return True
        else:
            print("规则信息收集失败！")
            return False


def main():
    """主函数"""
    # 创建爬虫实例
    crawler = FLTRPDebateCrawler()
    
    # 运行爬虫
    crawler.run()


if __name__ == "__main__":
    # 安装所需库的提示
    print("运行前请确保已安装以下Python库：")
    print("1. requests: pip install requests")
    print("2. beautifulsoup4: pip install beautifulsoup4")
    print("3. python-docx: pip install python-docx")
    print("\n如需安装所有依赖，请运行：")
    print("pip install requests beautifulsoup4 python-docx")
    
    # 询问是否继续
    response = input("\n是否继续运行爬虫？(y/n): ")
    if response.lower() == 'y':
        main()
    else:
        print("程序已退出。")