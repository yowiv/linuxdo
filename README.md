# Linux.do 论坛自动点赞工具

一个用于自动登录 Linux.do 论坛并进行帖子浏览和点赞的 Python 工具。

## 功能特性

- 🔐 自动登录 Linux.do 论坛
- 📄 获取并浏览最新帖子列表
- ❤️ 随机选择帖子进行点赞
- ⚙️ 支持环境变量配置
- 📊 详细的统计信息
- 🛡️ 防止频繁请求的随机延迟

## 安装要求

### Python 依赖

```bash
pip install curl-cffi
```

### Python 版本
- Python 3.7+

## 环境变量配置

### 必需环境变量

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| `LINUX_DO_EMAIL` | 论坛登录邮箱 | `your@email.com` |
| `LINUX_DO_PASSWORD` | 论坛登录密码 | `your_password` |
| `CF_CLEARANCE` | CloudFlare 清除令牌 | `xxx-xxx-xxx` |

### 可选环境变量

| 环境变量 | 说明 | 默认值 | 可选值 |
|---------|------|--------|--------|
| `ENABLE_LIKE` | 是否启用点赞功能 | `true` | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` |
| `LIKE_COUNT` | 点赞帖子数量 | `5` | 任意正整数（最小为1） |
| `BROWSE_COUNT` | 浏览帖子数量 | 全部 | 任意正整数（最小为1） |

### 如何获取 CF_CLEARANCE

1. 在浏览器中访问 `https://linux.do`
2. 按 `F12` 打开开发者工具
3. 切换到 `Network` 标签
4. 刷新页面或登录
5. 查找包含 `cdn-cgi/challenge-platform/h/b/rc/` 的请求
6. 在响应的 `Set-Cookie` 中找到 `cf_clearance` 的值

## 使用方法

### Windows

#### 方法1：设置系统环境变量
```cmd
# 设置环境变量
set LINUX_DO_EMAIL=your@email.com
set LINUX_DO_PASSWORD=your_password
set CF_CLEARANCE=your_cf_clearance_value

# 可选配置
set ENABLE_LIKE=true
set LIKE_COUNT=5
set BROWSE_COUNT=10

# 运行程序
python main.py
```

#### 方法2：一次性运行
```cmd
set LINUX_DO_EMAIL=your@email.com && set LINUX_DO_PASSWORD=your_password && set CF_CLEARANCE=your_cf_clearance && python main.py
```

### Linux/Mac

#### 方法1：设置环境变量
```bash
# 设置环境变量
export LINUX_DO_EMAIL="your@email.com"
export LINUX_DO_PASSWORD="your_password"
export CF_CLEARANCE="your_cf_clearance_value"

# 可选配置
export ENABLE_LIKE=true
export LIKE_COUNT=5
export BROWSE_COUNT=10

# 运行程序
python main.py
```

#### 方法2：一次性运行
```bash
LINUX_DO_EMAIL="your@email.com" LINUX_DO_PASSWORD="your_password" CF_CLEARANCE="your_cf_clearance" python main.py
```

## 使用场景示例

### 场景1：只浏览帖子，不点赞
```bash
# Windows
set ENABLE_LIKE=false && set BROWSE_COUNT=10 && python main.py

# Linux/Mac
ENABLE_LIKE=false BROWSE_COUNT=10 python main.py
```

### 场景2：浏览前15个帖子，随机点赞3个
```bash
# Windows
set ENABLE_LIKE=true && set BROWSE_COUNT=15 && set LIKE_COUNT=3 && python main.py

# Linux/Mac
ENABLE_LIKE=true BROWSE_COUNT=15 LIKE_COUNT=3 python main.py
```

### 场景3：浏览所有帖子，点赞1个（最保守）
```bash
# Windows
set LIKE_COUNT=1 && python main.py

# Linux/Mac
LIKE_COUNT=1 python main.py
```

### 场景4：浏览所有帖子，随机点赞10个
```bash
# Windows
set LIKE_COUNT=10 && python main.py

# Linux/Mac
LIKE_COUNT=10 python main.py
```

## 输出示例

### 启用点赞模式
```
=== Linux.do 论坛自动点赞工具 ===

正在获取 CSRF token...
✅ CSRF token 获取成功: abcd1234...
正在尝试登录...
✅ 构建cookies字符串: _t=xxx; cf_clearance=xxx...
✅ 登录成功!
用户名: your_username
用户ID: 12345
信任等级: 2

🔧 配置信息:
   启用点赞: 是
   点赞数量: 5
   浏览数量: 全部

==================================================
🤖 开始自动点赞...
🔍 正在获取最新帖子列表...
📄 获取到 20 个帖子
📋 浏览所有 20 个帖子

👀 浏览帖子:
 1. 📝 某个帖子标题1 (ID:123456, 👍:5, 💬:10)
 2. 📝 某个帖子标题2 (ID:123457, 👍:3, 💬:7)
 ...

🎯 从浏览的帖子中随机选择 5 个进行点赞:
   1. 某个帖子标题5 (ID:123460)
   2. 某个帖子标题2 (ID:123457)
   ...

🤖 开始点赞，每次点赞后随机延迟 2 到 5 秒...

1. 正在处理帖子:
   📝 标题: 某个帖子标题5
   🆔 主题ID: 123460
   🔍 正在获取帖子详情...
   📍 帖子ID: 654321
   ✅ 点赞成功! (状态码: 200)
   ⏳ 等待 3.2 秒...

📊 统计信息:
   可用帖子总数: 20
   实际浏览数: 20
   选择点赞数: 5
   点赞成功数: 5
   点赞失败数: 0
   点赞成功率: 100.0%
```

### 仅浏览模式
```
🔧 配置信息:
   启用点赞: 否
   浏览数量: 10

⏸️ 点赞功能已禁用，仅浏览帖子...
📄 获取到 20 个帖子

📋 浏览前 10 个帖子:
 1. 📝 某个帖子标题1 (ID:123456, 👍:5, 💬:10)
 2. 📝 某个帖子标题2 (ID:123457, 👍:3, 💬:7)
 ...

📊 浏览统计:
   可用帖子总数: 20
   实际浏览数: 10
```

## 注意事项

### 重要提醒
- ⚠️ **合理使用**：建议设置合理的点赞数量，避免被系统检测
- ⚠️ **网络延迟**：程序内置随机延迟（2-5秒），防止请求过于频繁

### 安全建议
1. 不要在公共环境中暴露账号信息
2. 定期更新 CF_CLEARANCE 值
3. 合理设置点赞数量（建议1-10个）
4. 避免在短时间内频繁运行

### 故障排除

#### 登录失败
- 检查邮箱和密码是否正确
- 确认 CF_CLEARANCE 是否有效
- 尝试重新获取 CF_CLEARANCE

#### 点赞失败
- 检查网络连接
- 确认 CSRF token 是否有效
- 查看是否达到论坛的点赞限制

#### 获取帖子失败
- 检查 cookies 是否有效
- 确认论坛是否正常访问
- 尝试重新登录

## 开发信息

### 主要功能模块
- `get_csrf_token()`: 获取 CSRF 令牌
- `login_linux_do()`: 论坛登录
- `get_latest_topics()`: 获取最新帖子
- `like_post()`: 帖子点赞
- `auto_like_topics()`: 自动点赞流程

### 技术栈
- **HTTP客户端**: curl-cffi
- **数据处理**: Python标准库
- **配置管理**: 环境变量

## 许可证

本项目仅供学习和研究使用，请遵守相关网站的使用条款。
