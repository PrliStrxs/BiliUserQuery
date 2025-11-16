import requests
import time
import os

def get_user_info(mid, headers):
    """
    获取用户基本信息
    API: https://api.bilibili.com/x/space/acc/info?mid={mid}
    """
    url = f"https://api.bilibili.com/x/space/acc/info"
    params = {
        'mid': mid
    }
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # 检查API返回状态
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

def download_image(url, filepath, headers):
    """
    下载图片到指定路径
    """
    try:
        if not url:
            print(f"图片URL为空，跳过下载")
            return False
            
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"图片已下载: {filepath}")
        return True
        
    except Exception as e:
        print(f"下载图片失败 {url}: {e}")
        return False

def extract_user_info(user_data):
    """
    从用户数据中提取指定信息（不包含图片URL）
    """
    if not user_data or 'data' not in user_data:
        return None
    
    data = user_data['data']
    
    # 提取指定的字段（不包含图片URL）
    extracted_info = {
        'mid': data.get('mid'),  # 用户ID
        'name': data.get('name'),  # 用户名
        'sex': data.get('sex'),  # 性别
        'sign': data.get('sign'),  # 签名
        'level': data.get('level'),  # 等级
        'vip_text': data.get('vip', {}).get('label', {}).get('text', ''),  # 会员信息
        'official_title': data.get('official', {}).get('title', ''),  # 标识
        'attestation_title': data.get('attestation', {}).get('common_info', {}).get('prefix_title', ''),  # 认证信息
        'nameplate_name': data.get('nameplate', {}).get('name', ''),  # 勋章名字
        'pendant_name': data.get('pendant', {}).get('name', '')  # 头像框
    }
    
    return extracted_info

def download_user_images(mid, user_data, headers):
    """
    下载用户头像、头像框和勋章图片
    """
    if not user_data or 'data' not in user_data:
        return
    
    data = user_data['data']
    
    # 下载头像
    face_url = data.get('face')
    if face_url:
        # 从URL中提取文件扩展名
        file_extension = '.jpg'  # 默认使用jpg
        if '.' in face_url:
            ext = face_url.split('.')[-1].split('?')[0]
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                file_extension = f'.{ext}'
        
        face_path = f"img/{mid}_face{file_extension}"
        download_image(face_url, face_path, headers)
    
    # 下载头像框
    pendant_image_url = data.get('pendant', {}).get('image')
    if pendant_image_url:
        # 从URL中提取文件扩展名
        file_extension = '.png'  # 默认使用png
        if '.' in pendant_image_url:
            ext = pendant_image_url.split('.')[-1].split('?')[0]
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                file_extension = f'.{ext}'
        
        pendant_path = f"img/{mid}_pendant{file_extension}"
        download_image(pendant_image_url, pendant_path, headers)
    
    # 下载勋章
    nameplate_image_url = data.get('nameplate', {}).get('image')
    if nameplate_image_url:
        # 从URL中提取文件扩展名
        file_extension = '.png'  # 默认使用png
        if '.' in nameplate_image_url:
            ext = nameplate_image_url.split('.')[-1].split('?')[0]
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                file_extension = f'.{ext}'
        
        nameplate_path = f"img/{mid}_nameplate{file_extension}"
        download_image(nameplate_image_url, nameplate_path, headers)

def get_user_info_with_retry(mid, headers, max_retries=3, delay=3):
    """
    带重试功能的用户信息查询，返回提取后的数据
    """
    for attempt in range(max_retries):
        result = get_user_info(mid, headers)
        if result:
            # 下载用户图片
            download_user_images(mid, result, headers)
            
            # 提取指定数据（不包含图片URL）
            extracted_data = extract_user_info(result)
            if extracted_data:
                return extracted_data
        
        # 如果不是最后一次尝试，则等待后重试
        if attempt < max_retries - 1:
            print(f"等待 {delay} 秒后重试... ({attempt + 1}/{max_retries})")
            time.sleep(delay)
        else:
            print(f"经过 {max_retries} 次尝试后仍失败，放弃查询")
    
    return None