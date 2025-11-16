# common.py
import os
from collections import deque
import threading

# 全局查询历史记录，最多保存3个用户
query_history = deque(maxlen=3)
history_lock = threading.Lock()

def delete_user_data(mid):
    """
    删除指定用户的所有数据
    """
    # 删除JSON数据文件
    data_file = f"data/{mid}_data.json"
    if os.path.exists(data_file):
        try:
            os.remove(data_file)
            print(f"已删除用户数据文件: {data_file}")
        except Exception as e:
            print(f"删除数据文件失败: {e}")
    
    # 删除图片文件
    img_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    for ext in img_extensions:
        img_file = f"img/{mid}_face{ext}"
        if os.path.exists(img_file):
            try:
                os.remove(img_file)
                print(f"已删除用户头像: {img_file}")
            except Exception as e:
                print(f"删除头像文件失败: {e}")
        
        img_file = f"img/{mid}_pendant{ext}"
        if os.path.exists(img_file):
            try:
                os.remove(img_file)
                print(f"已删除用户头像框: {img_file}")
            except Exception as e:
                print(f"删除头像框文件失败: {e}")
        
        img_file = f"img/{mid}_nameplate{ext}"
        if os.path.exists(img_file):
            try:
                os.remove(img_file)
                print(f"已删除用户勋章: {img_file}")
            except Exception as e:
                print(f"删除勋章文件失败: {e}")
    
    # 删除生成的用户卡片
    card_file = f"output/{mid}.png"
    if os.path.exists(card_file):
        try:
            os.remove(card_file)
            print(f"已删除用户卡片: {card_file}")
        except Exception as e:
            print(f"删除用户卡片失败: {e}")

def manage_query_history(mid):
    """
    管理查询历史记录，如果超过3个用户则删除最早的
    """
    with history_lock:
        # 检查是否是第四个查询，如果是则删除第一个查询的用户数据
        if len(query_history) >= 3:
            # 删除最早的用户数据
            oldest_mid = query_history[0]
            print(f"查询历史已满，正在删除最早的用户数据 (MID: {oldest_mid})...")
            delete_user_data(oldest_mid)
            query_history.popleft()
        
        # 添加到查询历史记录
        query_history.append(mid)
        print(f"当前查询历史: {list(query_history)}")