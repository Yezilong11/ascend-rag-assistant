# Cloudflare Tunnel 部署指南

## 概述

Cloudflare Tunnel（原 Cloudflare Argo Tunnel）提供完全免费的内网穿透服务，可长期稳定运行，适合比赛演示连续运行一周的需求。

**优势：**
- ✅ 完全免费
- ✅ 无时长/流量限制
- ✅ 可获得固定公网域名
- ✅ 自动 HTTPS
- ✅ 无第三方"Visit Site"拦截页

---

## 准备工作

### 1. 安装 cloudflared

```powershell
# 方式一：Chocolatey（推荐）
choco install cloudflared

# 方式二：手动下载
# 访问 https://github.com/cloudflare/cloudflared/releases
# 下载 windows_amd64.zip，解压到 PATH 目录
```

验证安装：
```powershell
cloudflared --version
```

### 2. 注册 Cloudflare 账号

1. 访问 https://dash.cloudflare.com/
2. 注册账号（使用邮箱）
3. 完成邮箱验证

### 3. 添加域名（可选，但推荐）

如果你有自己的域名：
1. 在 Cloudflare Dashboard 点击 "Add a Site"
2. 输入你的域名，按照指示修改域名服务器的 DNS
3. 等待 DNS 生效（约 24-48 小时）

> 如果没有域名，Cloudflare 也提供免费的 `trycloudflare.com` 子域名，但每次启动会变化。不推荐用于比赛。

---

## 配置步骤

### 方式一：使用自己的域名（推荐）

#### 步骤 1：登录认证

```powershell
cloudflared tunnel login
```

浏览器会自动打开，选择你的域名授权。

#### 步骤 2：创建隧道

```powershell
cloudflared tunnel create ascend-rag
```

成功后会显示隧道 ID，格式类似：`a1b2c3d4-e5f6-7890-abcd-ef1234567890`

#### 步骤 3：配置隧道

创建配置文件 `~/.cloudflared/config.yml`：

```yaml
tunnel: <你的隧道ID>
credentials-file: C:\Users\<你的用户名>\.cloudflared\<隧道ID>.json

ingress:
  - hostname: ascend-rag.yourdomain.com    # 替换为你的域名
    service: http://localhost:8080
  - service: http_status:404
```

#### 步骤 4：添加 DNS 记录

```powershell
cloudflared tunnel route dns ascend-rag ascend-rag.yourdomain.com
```

#### 步骤 5：运行隧道

```powershell
cloudflared tunnel run ascend-rag
```

看到类似输出表示成功：
```
2024-01-01T00:00:00Z INF Starting tunnel tunnelID=xxx
2024-01-01T00:00:00Z INF Route is watching cfdudozea.cfduaral.com
2024-01-01T00:00:00Z INF Proxying incoming requests on https://ascend-rag.yourdomain.com to http://localhost:8080
```

---

### 方式二：临时测试（无需域名）

如果你只是想快速测试，使用 Cloudflare 的临时域名：

```powershell
cloudflared tunnel --url http://localhost:8080
```

会输出类似：
```
Your temporary Tunnel is here: https://xxxx.trycloudflare.com
```

> ⚠️ 警告：这种方式每次启动域名会变化，且断开后不可恢复。仅用于测试。

---

## 配置为后台服务（Windows）

为了隧道能长期稳定运行，建议配置为 Windows 服务：

### 安装为服务

```powershell
cloudflared service install
```

### 启动服务

```powershell
Start-Service cloudflared
```

### 检查状态

```powershell
Get-Service cloudflared
```

### 查看日志

```powershell
Get-WinEvent -LogName Application -Source cloudflared | Select-Object -First 20
```

### 卸载服务

```powershell
cloudflared service uninstall
```

---

## 一键启动脚本

创建 `start-cloudflare-tunnel.ps1`：

```powershell
# Cloudflare Tunnel 启动脚本
param(
    [string]$TunnelName = "ascend-rag",
    [string]$Domain = "ascend-rag.yourdomain.com"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Ascend RAG - Cloudflare Tunnel" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查 cloudflared 是否安装
$cfVersion = cloudflared --version 2>$null
if (-not $cfVersion) {
    Write-Host "[ERROR] cloudflared 未安装" -ForegroundColor Red
    Write-Host "运行: choco install cloudflared" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] cloudflared version: $cfVersion" -ForegroundColor Green

# 启动隧道
Write-Host "[INFO] 启动 Cloudflare Tunnel..." -ForegroundColor Yellow
Write-Host "[INFO] 访问地址: https://$Domain" -ForegroundColor Cyan

cloudflared tunnel run $TunnelName
```

---

## 更新 CORS 配置

Cloudflare Tunnel 会以 HTTPS 转发请求到本地 HTTP，Origin 会变成你的公网域名。

修改 `docker-compose.yml` 添加环境变量支持：

```yaml
environment:
  - CORS_ORIGINS=https://ascend-rag.yourdomain.com  # 替换为你的实际域名
```

或者设置为允许所有来源（仅演示期间使用）：

```yaml
environment:
  - CORS_ORIGINS=*
```

---

## 故障排查

### 隧道启动失败

```powershell
# 检查隧道是否存在
cloudflared tunnel list

# 查看详细日志
cloudflared tunnel run ascend-rag --loglevel debug
```

### DNS 解析问题

```powershell
# 检查 DNS 记录
nslookup ascend-rag.yourdomain.com

# 手动刷新 DNS
cloudflared tunnel route dns ascend-rag ascend-rag.yourdomain.com
```

### 连接不稳定

1. 检查网络连接
2. 确认防火墙允许 cloudflared 出站
3. 查看 Cloudflare 状态页面

---

## 比赛演示检查清单

| 序号 | 任务 | 状态 |
|------|------|------|
| 1 | 安装 cloudflared | ⬜ |
| 2 | 注册 Cloudflare 账号 | ⬜ |
| 3 | 创建 Cloudflare Tunnel | ⬜ |
| 4 | 配置 DNS 域名解析 | ⬜ |
| 5 | 测试隧道连通性 | ⬜ |
| 6 | 更新 CORS 配置 | ⬜ |
| 7 | 启动 Docker 容器 | ⬜ |
| 8 | 启动 Cloudflare Tunnel | ⬜ |
| 9 | 公网访问测试 | ⬜ |
| 10 | 演示功能预演 | ⬜ |
