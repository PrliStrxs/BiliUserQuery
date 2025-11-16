# IFLOW.md - B站用户数据查询程序

## 项目概述

这是一个用于查询B站用户数据的Python程序。该程序通过B站API接口获取用户的基本信息、关注/粉丝数量、播放量和点赞数等数据，并支持将数据保存到本地JSON文件中。同时，程序还能下载用户的头像、头像框和勋章图片。

项目采用模块化设计，将不同API的调用封装在`api`目录下的独立模块中，包含：
- `user_info.py` - 用户基本信息查询（包括头像、勋章等图片下载）
- `relation_stat.py` - 关注和粉丝数量查询
- `upstat.py` - 播放量和点赞数量查询

## 项目结构

```
biliuserquery/
├── app.py                 # 主程序入口
├── cookie.txt             # 存放B站Cookie信息
├── api/
│   ├── __init__.py
│   ├── user_info.py       # 用户信息API
│   ├── relation_stat.py   # 关系统计API
│   └── upstat.py          # UP主统计数据API
├── data/                  # 存放查询结果数据
├── img/                   # 存放下载的用户图片
└── .git/                  # Git版本控制目录
```

## 依赖与配置

程序依赖以下Python库：
- `requests` - 用于HTTP请求
- `json` - 用于JSON数据处理
- `os`, `time`, `datetime` - 标准库

### 配置要求

1. **Cookie配置**：在项目根目录创建`cookie.txt`文件，填入有效的B站Cookie信息
2. **API访问**：程序通过B站API获取数据，需要有效的Cookie以通过身份验证

## 功能特性

1. **数据查询**：
   - 用户基本信息（ID、昵称、性别、签名、等级、会员信息等）
   - 关注数和粉丝数
   - 播放量和点赞数

2. **图片下载**：
   - 用户头像
   - 头像框（挂件）
   - 勋章图片

3. **数据保存**：
   - 查询结果以JSON格式保存到`data/`目录
   - 文件名格式为`{用户ID}_data.json`

4. **错误处理**：
   - 网络请求失败重试机制（最多3次）
   - API返回错误处理
   - 数据提取异常处理

## 使用方法

1. 确保已安装Python和`requests`库
2. 在`cookie.txt`中填入有效的B站Cookie
3. 运行`python app.py`
4. 按提示输入要查询的B站用户MID

## API接口

程序使用以下B站API接口：
- `https://api.bilibili.com/x/space/acc/info` - 获取用户基本信息
- `https://api.bilibili.com/x/relation/stat` - 获取关注和粉丝数量
- `https://api.bilibili.com/x/space/upstat` - 获取播放和点赞数量

## 数据字段

查询结果包含以下数据字段：
- `mid`: 用户ID
- `name`: 用户名
- `sex`: 性别
- `sign`: 签名
- `level`: 等级
- `vip_text`: 会员信息
- `official_title`: 官方认证标题
- `attestation_title`: 认证信息
- `nameplate_name`: 勋章名称
- `pendant_name`: 头像框名称
- `following`: 关注数量
- `follower`: 粉丝数量
- `view`: 播放量
- `likes`: 点赞总数

## 存储结构

- 用户数据保存在`data/`目录下，格式为JSON
- 用户图片保存在`img/`目录下，以用户ID命名