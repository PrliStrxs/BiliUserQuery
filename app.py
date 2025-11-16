import os
import json
import requests
import time
from datetime import datetime

# 导入API模块
from api.user_info import get_user_info_with_retry
from api.relation_stat import get_relation_stat_with_retry
from api.upstat import get_upstat_with_retry

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
    
    print(f"\n用户 {mid} 的所有数据查询完成！")
    return True

def main():
    """
    主程序
    """
    print("=" * 50)
    print("B站用户数据查询程序")
    print("=" * 50)
    
    # 加载Cookie
    cookie = load_cookie()
    if not cookie:
        return
    
    # 创建请求头
    headers = create_headers(cookie)
    
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
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")

if __name__ == "__main__":
    main()