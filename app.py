# app.py (修改版本)
import os
import json
import requests
import time
import sys
from datetime import datetime
from collections import deque
import threading

# 导入API模块
from api.user_info import get_user_info_with_retry
from api.relation_stat import get_relation_stat_with_retry
from api.upstat import get_upstat_with_retry
from draw_user_card import draw_user_card
from web_api import run_web_api  # 导入Web API启动函数
from common import manage_query_history, delete_user_data  # 导入共享功能

def load_cookie():
    """
    从cookie.txt文件加载Cookie信息
    """
    try:
        with open('cookie.txt', 'r', encoding='utf-8') as f:
            cookie = f.read().strip()
        if not cookie:
            raise ValueError("Cookie文件为空")
        return cookie
    except FileNotFoundError:
        print("错误: 未找到cookie.txt文件")
        print("请在项目根目录创建cookie.txt，并填入你的B站Cookie")
        return None
    except Exception as e:
        print(f"读取Cookie时出错: {e}")
        return None

def create_headers(cookie):
    """
    创建请求头，包含Cookie和User-Agent
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Cookie': cookie,
        'Referer': 'https://www.bilibili.com/',
        'Origin': 'https://www.bilibili.com'
    }
    return headers

def save_combined_data(mid, user_info, relation_stat, upstat_data):
    """
    保存合并后的数据到一个文件
    """
    # 创建data目录
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # 合并所有数据
    combined_data = {}
    
    # 添加用户基本信息
    if user_info:
        combined_data.update(user_info)
    
    # 添加关系数据
    if relation_stat:
        combined_data.update(relation_stat)
    
    # 添加统计数据
    if upstat_data:
        combined_data.update(upstat_data)
    
    filename = f"data/{mid}_data.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到: {filename}")
        return True
    except Exception as e:
        print(f"保存数据时出错: {e}")
        return False

def query_user_data(mid, headers):
    """
    按顺序查询用户数据，每个API都有重试机制
    """
    print(f"\n开始查询用户 {mid} 的数据...")
    
    # 管理查询历史记录
    manage_query_history(mid)
    
    # 1. 查询用户基本信息（带重试）
    print("1. 查询用户基本信息...")
    user_info = get_user_info_with_retry(mid, headers)
    if not user_info:
        print("用户基本信息查询失败，停止后续查询")
        return False
    
    # 2. 查询关注和粉丝数量（带重试）
    print("2. 查询关注和粉丝数量...")
    relation_stat = get_relation_stat_with_retry(mid, headers)
    if not relation_stat:
        print("关注粉丝数据查询失败，停止后续查询")
        return False
    
    # 3. 查询播放和点赞数量（带重试）
    print("3. 查询播放和点赞数量...")
    upstat_data = get_upstat_with_retry(mid, headers)
    if not upstat_data:
        print("播放点赞数据查询失败")
        return False
    
    # 4. 保存合并后的数据
    print("4. 保存数据...")
    save_combined_data(mid, user_info, relation_stat, upstat_data)
    
    # 5. 生成用户信息卡片
    print("5. 生成用户信息卡片...")
    draw_user_card(mid)
    
    print(f"\n用户 {mid} 的所有数据查询完成！")
    return True

def start_web_api():
    """
    在单独线程中启动Web API服务
    """
    print("正在启动Web API服务...")
    web_api_thread = threading.Thread(target=run_web_api, daemon=True)
    web_api_thread.start()
    print("Web API服务已启动在 http://127.0.0.1:12561")

def run_interactive_mode(headers):
    """
    运行交互式命令行模式
    """
    print("\n交互式命令行模式已启动，您可以通过以下方式访问：")
    print("  - 查询用户数据: http://127.0.0.1:12561/<mid>")
    print("  - 获取用户卡片: http://127.0.0.1:12561/card/<mid>")
    print("\n同时您也可以在此命令行界面继续查询用户：")
    
    while True:
        try:
            # 获取用户MID
            mid_input = input("\n请输入B站用户MID（输入'quit'退出）: ").strip()
            
            if mid_input.lower() == 'quit':
                print("程序退出，再见！")
                break
            
            # 验证MID是否为数字
            if not mid_input.isdigit():
                print("错误: MID必须是数字")
                continue
            
            mid = int(mid_input)
            
            # 执行查询
            success = query_user_data(mid, headers)
            if not success:
                print("部分或全部数据查询失败，请稍后重试")
                continue
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except EOFError:
            # 当在后台运行时遇到EOF错误，退出交互模式
            print("\n检测到非交互式环境，退出命令行模式，Web API服务继续运行...")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")

def is_interactive_environment():
    """
    检查是否在交互式环境中运行
    """
    return sys.stdin.isatty()

def main():
    """
    主程序
    """
    print("=" * 50)
    print("B站用户数据查询程序")
    print("=" * 50)
    
    # 启动Web API服务
    start_web_api()
    
    # 加载Cookie
    cookie = load_cookie()
    if not cookie:
        print("无法启动服务：Cookie加载失败")
        return
    
    # 创建请求头
    headers = create_headers(cookie)
    
    # 检查是否在交互式环境中
    if is_interactive_environment():
        # 交互式环境：启动命令行界面
        run_interactive_mode(headers)
    else:
        # 非交互式环境：只启动Web API服务，不进入命令行循环
        print("检测到非交互式环境，仅启动Web API服务")
        print("Web API服务已启动，您可以通过以下方式访问：")
        print("  - 查询用户数据: http://127.0.0.1:12561/<mid>")
        print("  - 获取用户卡片: http://127.0.0.1:12561/card/<mid>")
        print("\n程序将在后台持续运行...")
        
        # 保持主线程运行，防止程序退出
        try:
            while True:
                time.sleep(60)  # 每分钟检查一次
        except KeyboardInterrupt:
            print("\n程序被用户中断")
            

if __name__ == "__main__":
    main()