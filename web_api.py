# web_api.py
from flask import Flask, jsonify, send_file
import os
import json
import time
from datetime import datetime
from collections import deque
import threading

# 导入现有的API模块
from api.user_info import get_user_info_with_retry
from api.relation_stat import get_relation_stat_with_retry
from api.upstat import get_upstat_with_retry
from draw_user_card import draw_user_card
from common import manage_query_history, delete_user_data  # 导入共享功能

app = Flask(__name__)

# 全局变量存储Cookie和请求头
global_cookie = None
global_headers = None

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

def query_user_data(mid):
    """
    按顺序查询用户数据，每个API都有重试机制
    """
    global global_headers
    
    if not global_headers:
        return {"error": "未加载Cookie信息，请检查cookie.txt文件"}
    
    print(f"开始查询用户 {mid} 的数据...")
    
    # 管理查询历史记录
    manage_query_history(mid)
    
    # 1. 查询用户基本信息（带重试）
    print("1. 查询用户基本信息...")
    user_info = get_user_info_with_retry(mid, global_headers)
    if not user_info:
        return {"error": "用户基本信息查询失败"}
    
    # 2. 查询关注和粉丝数量（带重试）
    print("2. 查询关注和粉丝数量...")
    relation_stat = get_relation_stat_with_retry(mid, global_headers)
    if not relation_stat:
        return {"error": "关注粉丝数据查询失败"}
    
    # 3. 查询播放和点赞数量（带重试）
    print("3. 查询播放和点赞数量...")
    upstat_data = get_upstat_with_retry(mid, global_headers)
    if not upstat_data:
        return {"error": "播放点赞数据查询失败"}
    
    # 4. 保存合并后的数据
    print("4. 保存数据...")
    if not save_combined_data(mid, user_info, relation_stat, upstat_data):
        return {"error": "数据保存失败"}
    
    # 5. 生成用户信息卡片
    print("5. 生成用户信息卡片...")
    if not draw_user_card(mid):
        return {"error": "生成用户卡片失败"}
    
    print(f"用户 {mid} 的所有数据查询完成！")
    
    # 返回合并数据
    combined_data = {}
    combined_data.update(user_info)
    combined_data.update(relation_stat)
    combined_data.update(upstat_data)
    
    return combined_data

def load_user_data_from_file(mid):
    """
    从文件加载用户数据
    """
    data_file = f"data/{mid}_data.json"
    if not os.path.exists(data_file):
        return None
    
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"加载数据文件失败: {e}")
        return None

@app.route('/')
def index():
    """
    首页
    """
    return jsonify({
        "message": "B站用户数据查询API服务",
        "usage": {
            "query_user": "/<mid> - 查询指定MID的用户数据",
            "get_card": "/card/<mid> - 获取用户信息卡片图片",
            "example": "/2 - 查询MID为2的用户数据"
        },
        "status": "running"
    })

@app.route('/<int:mid>')
def get_user_data(mid):
    """
    获取用户数据的API接口
    """
    try:
        # 首先尝试从文件加载数据
        user_data = load_user_data_from_file(mid)
        
        if user_data is None:
            # 如果文件不存在，查询用户数据
            print(f"数据文件不存在，开始查询用户 {mid} 数据...")
            result = query_user_data(mid)
            
            # 检查是否有错误
            if "error" in result:
                return jsonify({
                    "success": False,
                    "error": result["error"],
                    "mid": mid
                }), 400
            
            user_data = result
        
        # 添加卡片下载链接到数据中
        user_data_with_card = user_data.copy()
        user_data_with_card["card_image_url"] = f"http://127.0.0.1:12561/card/{mid}"
        
        # 确保卡片存在
        card_path = f"output/{mid}.png"
        if not os.path.exists(card_path):
            print(f"卡片不存在，重新生成用户 {mid} 卡片...")
            if not draw_user_card(mid):
                return jsonify({
                    "success": False,
                    "error": "生成用户卡片失败",
                    "mid": mid
                }), 500
        
        # 返回成功结果
        return jsonify({
            "success": True,
            "mid": mid,
            "data": user_data_with_card,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"服务器内部错误: {str(e)}",
            "mid": mid
        }), 500

@app.route('/card/<int:mid>')
def get_user_card(mid):
    """
    获取用户信息卡片图片
    """
    try:
        # 检查卡片文件是否存在
        card_path = f"output/{mid}.png"
        if not os.path.exists(card_path):
            # 如果卡片不存在，检查数据是否存在
            data_file = f"data/{mid}_data.json"
            if not os.path.exists(data_file):
                # 如果数据也不存在，先查询数据
                print(f"数据文件不存在，开始查询用户 {mid} 数据...")
                result = query_user_data(mid)
                if "error" in result:
                    return jsonify({
                        "success": False,
                        "error": result["error"],
                        "mid": mid
                    }), 400
            else:
                # 数据存在但卡片不存在，重新生成卡片
                print(f"数据文件存在，重新生成用户 {mid} 卡片...")
                if not draw_user_card(mid):
                    return jsonify({
                        "success": False,
                        "error": "生成用户卡片失败",
                        "mid": mid
                    }), 500
        
        # 返回图片文件
        return send_file(card_path, mimetype='image/png')
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"获取卡片失败: {str(e)}",
            "mid": mid
        }), 500

def initialize():
    """
    初始化函数，在应用上下文中加载Cookie
    """
    global global_cookie, global_headers
    print("正在初始化Web API服务...")
    
    # 加载Cookie
    global_cookie = load_cookie()
    if global_cookie:
        # 创建请求头
        global_headers = create_headers(global_cookie)
        print("Cookie加载成功")
    else:
        print("Cookie加载失败，请检查cookie.txt文件")

def run_web_api():
    """
    启动Web服务器
    """
    global global_cookie, global_headers
    
    print("=" * 50)
    print("B站用户数据查询Web API服务")
    print("=" * 50)
    
    # 加载Cookie
    global_cookie = load_cookie()
    if not global_cookie:
        print("无法启动服务：Cookie加载失败")
        return
    
    # 创建请求头
    global_headers = create_headers(global_cookie)
    
    # 初始化应用
    initialize()
    
    # 启动服务器
    print("正在启动Web服务器...")
    print("访问地址: http://127.0.0.1:12561")
    print("API接口:")
    print("  - 首页: http://127.0.0.1:12561/")
    print("  - 查询用户: http://127.0.0.1:12561/<mid>")
    print("  - 用户卡片: http://127.0.0.1:12561/card/<mid>")
    
    app.run(host='0.0.0.0', port=12561, debug=False, use_reloader=False)

if __name__ == "__main__":
    run_web_api()