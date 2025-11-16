import requests
import time

def get_relation_stat(mid, headers):
    """
    获取用户的关注和粉丝数量
    API: https://api.bilibili.com/x/relation/stat?vmid={mid}
    """
    url = f"https://api.bilibili.com/x/relation/stat"
    params = {
        'vmid': mid
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('code') == 0:
            return data
        else:
            error_msg = data.get('message', '未知错误')
            print(f"API返回错误: {error_msg}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}")
        return None
    except Exception as e:
        print(f"处理数据时出错: {e}")
        return None

def extract_relation_stat(relation_data):
    """
    从关系数据中提取指定信息
    """
    if not relation_data or 'data' not in relation_data:
        return None
    
    data = relation_data['data']
    
    # 提取指定的字段
    extracted_info = {
        'following': data.get('following'),  # 关注数量
        'follower': data.get('follower')     # 粉丝数量
    }
    
    return extracted_info

def get_relation_stat_with_retry(mid, headers, max_retries=3, delay=3):
    """
    带重试功能的关注粉丝数量查询，返回提取后的数据
    """
    for attempt in range(max_retries):
        result = get_relation_stat(mid, headers)
        if result:
            # 提取指定数据
            extracted_data = extract_relation_stat(result)
            if extracted_data:
                return extracted_data
        
        # 如果不是最后一次尝试，则等待后重试
        if attempt < max_retries - 1:
            print(f"等待 {delay} 秒后重试... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
        else:
            print(f"经过 {max_retries} 次尝试后仍失败，放弃查询")
    
    return None