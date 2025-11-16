import requests
import time

def get_upstat(mid, headers):
    """
    获取用户的播放量和点赞数量
    API: https://api.bilibili.com/x/space/upstat?mid={mid}
    """
    url = f"https://api.bilibili.com/x/space/upstat"
    params = {
        'mid': mid
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

def extract_upstat(upstat_data):
    """
    从播放点赞数据中提取指定信息
    """
    if not upstat_data or 'data' not in upstat_data:
        return None
    
    data = upstat_data['data']
    
    # 提取指定的字段
    extracted_info = {
        'view': data.get('archive', {}).get('view', 0),  # 播放量
        'likes': data.get('likes', 0)  # 点赞总数
    }
    
    return extracted_info

def get_upstat_with_retry(mid, headers, max_retries=3, delay=3):
    """
    带重试功能的播放点赞数量查询，返回提取后的数据
    """
    for attempt in range(max_retries):
        result = get_upstat(mid, headers)
        if result:
            # 提取指定数据
            extracted_data = extract_upstat(result)
            if extracted_data:
                return extracted_data
        
        # 如果不是最后一次尝试，则等待后重试
        if attempt < max_retries - 1:
            print(f"等待 {delay} 秒后重试... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
        else:
            print(f"经过 {max_retries} 次尝试后仍失败，放弃查询")
    
    return None