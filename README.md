# B站用户数据查询程序

一个用于查询B站用户数据的Python程序，通过B站API获取用户信息、关注/粉丝数量、播放量和点赞数等数据，并支持下载用户头像、头像框和勋章图片。

## 功能特性

- 查询用户基本信息（ID、昵称、性别、签名、等级、会员信息等）
- 获取关注数和粉丝数
- 获取播放量和点赞数
- 下载用户头像、头像框和勋章图片
- 数据以JSON格式保存到本地
- 网络请求失败自动重试机制
- 支持批量查询多个用户

## 环境要求

- Python 3.6+
- requests库

## 安装依赖

```bash
pip install requests
```

## 使用教程

### 1. 获取B站Cookie

1. 打开B站网站 (https://www.bilibili.com) 并登录账号
2. 按F12打开开发者工具
3. 切换到"网络"或"Network"标签页
4. 刷新页面，找到任意一个B站API请求
5. 在请求的Headers中找到Cookie信息
6. 复制Cookie内容

### 2. 配置Cookie

在项目根目录创建`cookie.txt`文件，将获取到的Cookie粘贴进去并保存：

```
buvid3=xxx; _uuid=xxx; SESSDATA=xxx; bili_jct=xxx
```

### 3. 运行主程序

```bash
python app.py
```

程序运行后会提示输入B站用户MID（用户ID），输入后按回车开始查询：

```
请输入B站用户MID（输入'quit'退出）: 123456789
```

查询完成后，数据会保存到`data/`目录下，图片会保存到`img/`目录下。

## 输出文件说明

### 数据文件

- 位置：`data/{用户ID}_data.json`
- 格式：JSON
- 包含：用户基本信息、关注粉丝数、播放点赞数等

### 图片文件

- 位置：`img/`
- 格式：JPG/PNG
- 文件名格式：
  - `{用户ID}_face.xxx` - 用户头像
  - `{用户ID}_pendant.xxx` - 头像框
  - `{用户ID}_nameplate.xxx` - 勋章

## 数据字段说明

| 字段名 | 说明 |
|--------|------|
| mid | 用户ID |
| name | 用户名 |
| sex | 性别 |
| sign | 签名 |
| level | 等级 |
| vip_text | 会员信息 |
| official_title | 官方认证标题 |
| attestation_title | 认证信息 |
| nameplate_name | 勋章名称 |
| pendant_name | 头像框名称 |
| following | 关注数量 |
| follower | 粉丝数量 |
| view | 播放量 |
| likes | 点赞总数 |

## API接口

程序使用以下B站API接口：
- `https://api.bilibili.com/x/space/acc/info` - 获取用户基本信息
- `https://api.bilibili.com/x/relation/stat` - 获取关注和粉丝数量
- `https://api.bilibili.com/x/space/upstat` - 获取播放和点赞数量

## 错误处理

- 网络请求失败时会自动重试（最多3次）
- API返回错误时会显示错误信息
- Cookie无效时可能导致部分数据无法获取

## 注意事项

1. 请使用自己的B站账号Cookie，不要使用他人的Cookie
2. 查询频率不宜过快，避免被B站限制访问
3. Cookie过期时需要重新获取并更新`cookie.txt`文件
4. 本程序仅供学习交流使用，请遵守B站相关服务条款

## 目录结构

```
biliuserquery/
├── app.py                 # 主程序入口
├── draw_user_card.py      # 用户信息卡片生成器
├── cookie.txt             # 存放B站Cookie信息
├── api/
│   ├── __init__.py
│   ├── user_info.py       # 用户信息API
│   ├── relation_stat.py   # 关系统计API
│   └── upstat.py          # UP主统计数据API
├── data/                  # 存放查询结果数据
└── img/                   # 存放下载的用户图片
```
1