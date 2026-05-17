# cpolar 部署指南

## 概述

cpolar 是一款国内开发的内网穿透服务，在国内访问速度快，配置简单，适合比赛演示场景。

**优势：**
- ✅ 国内访问速度快
- ✅ 配置简单易用
- ✅ 支持长期稳定运行
- ✅ 提供 HTTP/HTTPS 双协议

**限制：**
- ⚠️ 免费版有流量限制（2GB/月）
- ⚠️ 免费版只支持随机子域名
- ⚠️ 付费版可获得固定域名（约 20元/月）

---

## 注册与安装

### 1. 注册 cpolar 账号

1. 访问 https://www.cpolar.com/
2. 点击"免费注册"
3. 使用邮箱注册账号
4. 完成邮箱验证

### 2. 获取认证 Token

1. 登录 cpolar 后台：https://dashboard.cpolar.com/
2. 复制你的认证 Token（类似：`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`）

### 3. 安装 cpolar

#### 方式一：Chocolatey（推荐）

```powershell
choco install cpolar
```

#### 方式二：手动下载

```powershell
# 访问 https://www.cpolar.com/download
# 下载 Windows 版本，解压到 PATH 目录
```

验证安装：
```powershell
cpolar version
```

### 4. 配置认证 Token

```powershell
cpolar authtoken <你的Token>
```

认证信息会保存在 `C:\Users\<用户名>\.cpolar\cpolar.yml`

---

## 快速启动

### 临时隧道（无需配置）

```powershell
cpolar http 8080
```

输出示例：
```
Online  Status: Online
Forwarding  http://abc12345.vip.cpolar.cn -> http://localhost:8080
Forwarding  https://abc12345.vip.cpolar.cn -> http://localhost:8080
```

> ⚠️ 免费版域名随机变化，不适合长期演示

---

## 配置固定域名（推荐）

cpolar 付费版支持固定域名，确保评委可以收藏链接。

### 1. 升级套餐

1. 访问 https://www.cpolar.com/pricing
2. 选择套餐（Basic 计划约 20元/月，支持固定域名）
3. 完成支付

### 2. 预留域名

1. 登录 cpolar 后台
2. 进入"预留"页面
3. 选择域名类型，填写子域名（如 `ascend-rag`）
4. 选择离你最近的服务器节点
5. 点击"创建"

### 3. 创建隧道配置

编辑 `C:\Users\<用户名>\.cpolar\cpolar.yml`：

```yaml
 tunnels:
   ascend-rag:
     proto: http
     addr: 8080
     subdomain: ascend-rag      # 你的固定子域名
     region: cn_bj             # 北京节点，可选: cn_hk, cn_sh, us
     hostname: ascend-rag.vip.cpolar.cn
     http_header:
       - name: Host
         value: ascend-rag.vip.cpolar.cn
```

### 4. 启动指定隧道

```powershell
cpolar start ascend-rag
```

---

## 配置为后台服务

### 安装服务

```powershell
cpolar service install
```

### 启动服务

```powershell
cpolar service start
```

### 检查状态

```powershell
cpolar service status
```

### 查看日志

```powershell
# Windows 事件查看器
Get-WinEvent -LogName Application | Where-Object {$_.ProviderName -eq "cpolar"} | Select-Object -First 20
```

---

## 一键启动脚本

创建 `start-cpolar.ps1`：

```powershell
# cpolar 启动脚本
param(
    [string]$TunnelName = "ascend-rag"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ascend RAG - cpolar Tunnel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查 cpolar 是否安装
$cpolarVersion = cpolar version 2>$null
if (-not $cpolarVersion) {
    Write-Host "[ERROR] cpolar 未安装" -ForegroundColor Red
    Write-Host "安装命令: choco install cpolar" -ForegroundColor Yellow
    Write-Host "或访问: https://www.cpolar.com/download" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] cpolar version: $cpolarVersion" -ForegroundColor Green

# 检查是否已配置 authtoken
$authConfigured = Test-Path "$env:USERPROFILE\.cpolar\cpolar.yml"
if (-not $authConfigured) {
    Write-Host "[ERROR] cpolar 未配置 authtoken" -ForegroundColor Red
    Write-Host "运行: cpolar authtoken <你的Token>" -ForegroundColor Yellow
    exit 1
}

# 启动隧道
Write-Host "[INFO] 启动 cpolar 隧道: $TunnelName" -ForegroundColor Yellow
Write-Host "[INFO] 预设域名: ascend-rag.vip.cpolar.cn" -ForegroundColor Cyan
Write-Host "[INFO] HTTPS 地址: https://ascend-rag.vip.cpolar.cn" -ForegroundColor Cyan

cpolar start $TunnelName
```

---

## 更新 CORS 配置

根据 cpolar 给出的实际域名更新 docker-compose.yml：

```yaml
environment:
  - CORS_ORIGINS=https://ascend-rag.vip.cpolar.cn
```

或者允许所有来源（仅演示期间）：

```yaml
environment:
  - CORS_ORIGINS=*
```

---

## 套餐对比

| 功能 | 免费版 | Basic (¥20/月) | Pro (¥50/月) |
|------|--------|----------------|--------------|
| 流量 | 2GB/月 | 100GB/月 | 500GB/月 |
| 固定域名 | ❌ | ✅ | ✅ |
| 自定义域名 | ❌ | ❌ | ✅ |
| 并发隧道 | 1个 | 3个 | 无限 |
| 在线时长 | 24小时 | 永久在线 | 永久在线 |

---

## 故障排查

### 隧道启动失败

```powershell
# 查看详细日志
cpolar http 8080 -log-level debug
```

### 连接被拒绝

1. 确认 Docker 容器已启动
2. 检查本地服务是否正常运行：`curl http://localhost:8080`
3. 检查防火墙设置

### 流量超限

免费版流量用完后服务会暂停：
1. 等待下月重置
2. 或升级到付费套餐
3. 或使用 Cloudflare Tunnel 作为备选

---

## 比赛演示检查清单

| 序号 | 任务 | 状态 |
|------|------|------|
| 1 | 注册 cpolar 账号 | ⬜ |
| 2 | 购买 Basic 套餐（可选） | ⬜ |
| 3 | 安装 cpolar | ⬜ |
| 4 | 配置 authtoken | ⬜ |
| 5 | 预留固定域名（付费版） | ⬜ |
| 6 | 配置隧道 | ⬜ |
| 7 | 测试隧道连通性 | ⬜ |
| 8 | 更新 CORS 配置 | ⬜ |
| 9 | 启动 Docker 容器 | ⬜ |
| 10 | 启动 cpolar | ⬜ |
| 11 | 公网访问测试 | ⬜ |
| 12 | 演示功能预演 | ⬜ |
