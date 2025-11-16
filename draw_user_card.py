# draw_user_card.py
from PIL import Image, ImageDraw, ImageFont
import json
import os
import textwrap

def draw_user_card(mid):
    """
    绘制用户信息卡片
    """
    # 检查数据文件是否存在
    data_file = f"data/{mid}_data.json"
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        return False
    
    # 加载数据
    with open(data_file, 'r', encoding='utf-8') as f:
        user_data = json.load(f)
    
    # 创建画布 (宽800px，高根据内容自适应)

    width = 800

    height = 1000  # 增加高度以适应更多内容
    
    # 创建白色背景
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体（使用系统字体作为后备）
    try:
        title_font = ImageFont.truetype("simhei.ttf", 28)  # 标题字体
        name_font = ImageFont.truetype("simhei.ttf", 24)   # 名字字体
        normal_font = ImageFont.truetype("simhei.ttf", 18) # 正文字体
        stat_font = ImageFont.truetype("simhei.ttf", 16)   # 统计数据字体，稍微调小
        small_font = ImageFont.truetype("simhei.ttf", 16)  # 小字体
    except:
        # 如果找不到字体，使用默认字体
        title_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
        normal_font = ImageFont.load_default()
        stat_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 绘制顶部背景（B站主题色 #FB7299）
    draw.rectangle([(0, 0), (width, 120)], fill=(251, 114, 153))
    
    # 绘制标题
    draw.text((width//2, 30), "B站用户信息卡片", fill=(255, 255, 255), 
              font=title_font, anchor="mm")
    
    # 加载并绘制头像
    avatar_path = None
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        if os.path.exists(f"img/{mid}_face{ext}"):
            avatar_path = f"img/{mid}_face{ext}"
            break
    
    avatar_size = 80
    if avatar_path:
        try:
            avatar = Image.open(avatar_path)
            avatar = avatar.resize((avatar_size, avatar_size), Image.LANCZOS)
            
            # 创建圆形遮罩
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([(0, 0), (avatar_size, avatar_size)], fill=255)
            
            # 应用圆形遮罩
            avatar_circle = Image.new('RGBA', (avatar_size, avatar_size), (0, 0, 0, 0))
            avatar_circle.paste(avatar, (0, 0), mask)
            
            # 绘制头像
            img.paste(avatar_circle, (50, 150), avatar_circle)
        except Exception as e:
            print(f"加载头像失败: {e}")
            # 绘制默认头像
            draw.ellipse([(50, 150), (50+avatar_size, 150+avatar_size)], 
                        fill=(200, 200, 200))
    
    # 绘制用户名和ID
    name = user_data.get('name', '未知用户')
    
    # 处理长用户名 - 使用textwrap进行换行
    name_lines = textwrap.wrap(name, width=15)  # 每行最多15个字符
    name_lines = name_lines[:2]  # 最多显示2行
    
    name_y = 160
    for i, line in enumerate(name_lines):
        draw.text((150, name_y + i*25), line, fill=(0, 0, 0), font=name_font)
    
    draw.text((150, name_y + len(name_lines)*25), f"UID: {mid}", fill=(100, 100, 100), font=normal_font)
    
    # 绘制等级和会员信息（分两行显示）
    level = user_data.get('level', 0)
    vip_text = user_data.get('vip_text', '')
    
    level_text = f"等级: Lv.{level}"
    draw.text((150, name_y + len(name_lines)*25 + 30), level_text, fill=(251, 114, 153), font=normal_font)
    
    if vip_text:
        vip_text_display = f"会员: {vip_text}"
        draw.text((150, name_y + len(name_lines)*25 + 55), vip_text_display, fill=(251, 114, 153), font=normal_font)
    
    # 绘制基本信息区域
    y_offset = name_y + len(name_lines)*25 + 85
    
    # 性别
    sex = user_data.get('sex', '未知')
    draw.text((50, y_offset), f"性别: {sex}", fill=(0, 0, 0), font=normal_font)
    
    # 签名（处理长签名）
    sign = user_data.get('sign', '')
    if not sign:
        sign = "这个用户还没有签名~"
    
    # 添加"签名："前缀
    sign_with_prefix = f"签名: {sign}"
    
    # 使用textwrap处理长签名
    max_chars_per_line = 40  # 每行最多字符数
    sign_lines = textwrap.wrap(sign_with_prefix, width=max_chars_per_line)
    sign_lines = sign_lines[:3]  # 最多显示3行
    
    for i, line in enumerate(sign_lines):
        draw.text((50, y_offset + 30 + i*25), line, fill=(100, 100, 100), font=normal_font)
    
    # 更新y_offset位置
    y_offset += 30 + len(sign_lines)*25 + 10
    
    # 绘制头衔和认证信息
    official_title = user_data.get('official_title', '')
    if official_title:
        # 处理头衔显示 - 使用淡金黄色 (255, 215, 0)
        title_with_prefix = f"头衔: {official_title}"
        title_lines = textwrap.wrap(title_with_prefix, width=max_chars_per_line)
        title_lines = title_lines[:2]  # 最多显示2行
        
        for i, line in enumerate(title_lines):
            draw.text((50, y_offset + i*25), line, fill=(255, 215, 0), font=normal_font)
        
        y_offset += len(title_lines)*25
    
    attestation_title = user_data.get('attestation_title', '')
    if attestation_title:
        # 处理认证信息显示 - 使用淡蓝色 (100, 150, 255)
        attestation_with_prefix = f"认证: {attestation_title}"
        attestation_lines = textwrap.wrap(attestation_with_prefix, width=max_chars_per_line)
        attestation_lines = attestation_lines[:2]  # 最多显示2行
        
        for i, line in enumerate(attestation_lines):
            draw.text((50, y_offset + i*25), line, fill=(100, 150, 255), font=normal_font)
        
        y_offset += len(attestation_lines)*25
    
    # 绘制勋章信息
    nameplate_name = user_data.get('nameplate_name', '')
    if nameplate_name:
        draw.text((50, y_offset), f"勋章: {nameplate_name}", fill=(0, 0, 0), font=normal_font)
        y_offset += 25
    
    # 现在绘制头像框 - 在所有文字绘制完成后
    pendant_path = None
    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
        if os.path.exists(f"img/{mid}_pendant{ext}"):
            pendant_path = f"img/{mid}_pendant{ext}"
            break
    
    if pendant_path:
        try:
            pendant = Image.open(pendant_path)
            # 确保头像框是RGBA模式以保留透明度
            if pendant.mode != 'RGBA':
                pendant = pendant.convert('RGBA')
                
            # 调整头像框大小，使其比头像稍大
            pendant_size = avatar_size + 40  # 增加更多空间
            pendant = pendant.resize((pendant_size, pendant_size), Image.LANCZOS)
            
            # 计算头像框位置，使其居中于头像
            pendant_x = 50 - (pendant_size - avatar_size) // 2
            pendant_y = 150 - (pendant_size - avatar_size) // 2
            
            # 创建临时图像用于合成
            temp_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            temp_img.paste(pendant, (pendant_x, pendant_y), pendant)
            
            # 将头像框合成到主图像
            img = Image.alpha_composite(img.convert('RGBA'), temp_img).convert('RGB')
            
            # 重新创建draw对象
            draw = ImageDraw.Draw(img)
            
        except Exception as e:
            print(f"加载头像框失败: {e}")
    
    # 加载并绘制勋章图片

    nameplate_path = None

    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:

        if os.path.exists(f"img/{mid}_nameplate{ext}"):

            nameplate_path = f"img/{mid}_nameplate{ext}"

            break

    

    # 创建一个列表来存储需要显示的图片

    images_to_show = []

    

    # 添加勋章图片到列表

    if nameplate_path:

        try:

            nameplate = Image.open(nameplate_path)

            # 确保勋章是RGBA模式以保留透明度

            if nameplate.mode != 'RGBA':

                nameplate = nameplate.convert('RGBA')

            # 调整勋章图片大小

            nameplate_size = 100

            nameplate = nameplate.resize((nameplate_size, nameplate_size), Image.LANCZOS)

            images_to_show.append(('nameplate', nameplate))

        except Exception as e:

            print(f"加载勋章图片失败: {e}")



    # 加载并添加头像到列表

    avatar_path = None

    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:

        if os.path.exists(f"img/{mid}_face{ext}"):

            avatar_path = f"img/{mid}_face{ext}"

            break

    

    if avatar_path:

        try:

            avatar = Image.open(avatar_path)

            # 确保头像是RGBA模式以保留透明度

            if avatar.mode != 'RGBA':

                avatar = avatar.convert('RGBA')

            # 调整头像大小

            avatar_size = 100

            avatar = avatar.resize((avatar_size, avatar_size), Image.LANCZOS)

            images_to_show.append(('avatar', avatar))

        except Exception as e:

            print(f"加载头像失败: {e}")



    # 加载并添加头像框到列表

    pendant_path = None

    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:

        if os.path.exists(f"img/{mid}_pendant{ext}"):

            pendant_path = f"img/{mid}_pendant{ext}"

            break

    

    if pendant_path:

        try:

            pendant = Image.open(pendant_path)

            # 确保头像框是RGBA模式以保留透明度

            if pendant.mode != 'RGBA':

                pendant = pendant.convert('RGBA')

            # 调整头像框大小

            pendant_size = 100

            pendant = pendant.resize((pendant_size, pendant_size), Image.LANCZOS)

            images_to_show.append(('pendant', pendant))

        except Exception as e:

            print(f"加载头像框失败: {e}")



    # 按顺序绘制图片（勋章、头像、头像框）- 每行显示最多3个图片

    images_per_row = 3

    for i in range(0, len(images_to_show), images_per_row):

        row_images = images_to_show[i:i+images_per_row]

        row_y = y_offset + 20 + (i // images_per_row) * 110  # 每行间距为110px，增加20px的顶部间距

        

        # 计算该行图片的总宽度，以便居中

        total_width = len(row_images) * 100 + (len(row_images) - 1) * 20  # 每张图片100px，间距20px

        start_x = (width - total_width) // 2

        

        for j, (img_type, img_data) in enumerate(row_images):

            x_pos = start_x + j * 120  # 每张图片加上间距

            

            # 创建临时图像用于合成

            temp_img = Image.new('RGBA', img.size, (0, 0, 0, 0))

            temp_img.paste(img_data, (x_pos, row_y), img_data)

            

            # 将图片合成到主图像

            img = Image.alpha_composite(img.convert('RGBA'), temp_img).convert('RGB')

            

            # 重新创建draw对象

            draw = ImageDraw.Draw(img)



    # 增加y_offset以容纳所有图片行

    rows_needed = (len(images_to_show) + images_per_row - 1) // images_per_row  # 向上取整

    y_offset += rows_needed * 110

    

    # 如果有图片被加载，添加标题

    if images_to_show:

        # 绘制图片标题

        draw.text((width//2, y_offset + 10), " ", fill=(0, 0, 0), 

                  font=normal_font, anchor="mm")

        y_offset += 30
    
        # 绘制统计数据区域（使用卡片式布局）

    stat_y = y_offset + 30  # 增加间距以避免重叠
    
    # 统计数据背景 - 扩大边框
    stat_bg_color = (245, 245, 245)
    draw.rectangle([(30, stat_y), (width-30, stat_y+160)], 
                  fill=stat_bg_color, outline=(220, 220, 220), width=2)
    
    # 统计数据标题
    draw.text((width//2, stat_y+15), "账号数据", fill=(0, 0, 0), 
              font=normal_font, anchor="mm")
    
    # 统计数据（4个卡片）- 扩大卡片尺寸
    card_width = (width - 100) // 2  # 增加宽度
    card_height = 50  # 增加高度
    card_margin = 20
    
    # 不使用数字格式化，显示具体数字
    stats = [
        {"label": "粉丝数", "value": str(user_data.get('follower', 0)), "color": (251, 114, 153)},
        {"label": "关注数", "value": str(user_data.get('following', 0)), "color": (0, 160, 220)},
        {"label": "播放量", "value": str(user_data.get('view', 0)), "color": (255, 150, 0)},
        {"label": "获赞数", "value": str(user_data.get('likes', 0)), "color": (0, 180, 120)}
    ]
    
    for i, stat in enumerate(stats):
        row = i // 2
        col = i % 2
        
        x = 50 + col * (card_width + card_margin)
        y = stat_y + 45 + row * (card_height + 15)
        
        # 绘制统计卡片 - 扩大卡片
        draw.rectangle([(x, y), (x+card_width, y+card_height)], 
                      fill=(255, 255, 255), outline=(230, 230, 230), width=1)
        
        # 绘制数值（居中）- 使用更小的字体确保数字不超出边界
        value = stat["value"]
        
        # 如果数字太长，自动缩小字体
        current_font_size = 16
        while current_font_size >= 10:
            try:
                current_font = ImageFont.truetype("simhei.ttf", current_font_size)
            except:
                current_font = ImageFont.load_default()
                
            value_bbox = draw.textbbox((0, 0), value, font=current_font)
            value_width = value_bbox[2] - value_bbox[0]
            
            if value_width <= card_width - 20:  # 留出边距
                break
            current_font_size -= 1
        
        # 计算位置
        value_bbox = draw.textbbox((0, 0), value, font=current_font)
        value_width = value_bbox[2] - value_bbox[0]
        value_x = x + (card_width - value_width) // 2
        
        draw.text((value_x, y+10), value, fill=stat["color"], font=current_font)
        
        # 绘制标签
        label_bbox = draw.textbbox((0, 0), stat["label"], font=normal_font)
        label_width = label_bbox[2] - label_bbox[0]
        label_x = x + (card_width - label_width) // 2
        
        draw.text((label_x, y+30), stat["label"], fill=(100, 100, 100), font=normal_font)
    
    # 绘制底部信息

    draw.text((width//2, height-30), "来源 by 兆孽的B站用户查询", 

              fill=(150, 150, 150), font=small_font, anchor="mm")
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    # 保存图片
    output_path = f"output/{mid}.png"
    img.save(output_path, "PNG")
    print(f"用户信息卡片已生成: {output_path}")
    
    return True

if __name__ == "__main__":
    """
    单独运行时的主程序
    """
    print("=" * 50)
    print("B站用户信息卡片生成器")
    print("=" * 50)
    
    while True:
        try:
            mid_input = input("\n请输入B站用户MID（输入'quit'退出）: ").strip()
            
            if mid_input.lower() == 'quit':
                print("程序退出，再见！")
                break
            
            # 验证MID是否为数字
            if not mid_input.isdigit():
                print("错误: MID必须是数字")
                continue
            
            mid = int(mid_input)
            
            # 生成信息卡片
            success = draw_user_card(mid)
            if not success:
                print("生成信息卡片失败，请检查数据是否存在")
            
        except KeyboardInterrupt:
            print("\n\n程序被用户中断")
            break
        except Exception as e:
            print(f"发生未知错误: {e}")