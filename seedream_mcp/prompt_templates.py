#!/usr/bin/env python3
"""
提示词模板系统

支持预定义的提示词模板,用户可以通过关键词快速应用专业的提示词风格。
"""

import logging
import re
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# 预定义的提示词模板
PROMPT_TEMPLATES = {
    "公众号封面": {
        "template": """主题内容：{keyword}

纸雕风格融合水彩层次美学，字体结构立体精致如水彩纸雕工艺，边缘细腻带水彩渐变与阴影效果，柔和红色与淡蓝水彩背景中营造纸艺空间，点缀立体几何图形与水彩装饰元素，文字表面呈现高级纸张与水彩光泽质感，字形排列层次分明如精美纸雕作品，整体营造出精致工艺与艺术学习的优雅层次，温和而富有艺术感的氛围中透出水彩的精致美感，高级水彩工艺视觉，横向延展构图""",
        "default_size": "2K",
        "aspect_ratio": "21:9",
        "description": "封面风格 - 纸雕水彩美学 (21:9超宽屏)"
    },

    "潮流派对": {
        "template": """中文"{keyword}"，潮流派对风格艺术字体，运营活动风格主题字体，字体大小变化明显，错落有致排版。部分笔画延长，字体笔画粗厚醒目，形态夸张变形，部分笔画带俏皮弧度或独特弯折，营造活波、肆意、充满活力的派对氛围，黄绿色点缀。黑色背景，背景干净。白色字体，大师作品。""",
        "default_size": "2K",
        "description": "潮流派对风格 - 活力字体设计"
    },
    
    "小红书封面": {
        "template": """小红书风格封面设计，主题：{keyword}

视觉风格：明亮清新、高饱和度色彩、年轻时尚
设计元素：简洁大字标题、吸睛配色、留白设计
氛围感：活力满满、精致生活、种草感强""",
        "default_size": "2K",
        "description": "小红书封面风格 - 清新时尚"
    },
    
    "产品海报": {
        "template": """商业产品海报设计，产品：{keyword}

设计风格：专业商业、高端大气、视觉冲击力强
核心元素：产品特写、光影效果、质感呈现
背景氛围：简约现代、突出主体、品牌调性
细节要求：高清画质、精致细节、专业摄影感""",
        "default_size": "4K",
        "description": "产品海报风格 - 商业专业"
    },
    
    "国潮风格": {
        "template": """中国风国潮设计，主题：{keyword}

艺术风格：传统与现代融合、东方美学、潮流感
色彩方案：中国红、墨色、金色、传统配色
设计元素：祥云纹样、水墨晕染、书法字体、传统图案
整体氛围：文化自信、时尚国风、年轻态度""",
        "default_size": "2K",
        "description": "国潮风格 - 东方美学"
    },
    
    "赛博朋克": {
        "template": """赛博朋克未来科技风格，主题：{keyword}

视觉风格：霓虹灯光、暗黑未来、高科技感
色彩方案：荧光蓝、紫红、电光绿、深色背景
设计元素：数字矩阵、全息投影、机械感、故障艺术
氛围营造：未来都市、科技感、神秘炫酷""",
        "default_size": "2K",
        "description": "赛博朋克风格 - 未来科技"
    },
    
    "极简主义": {
        "template": """极简主义设计，主题：{keyword}

设计理念：少即是多、克制优雅、留白艺术
色彩方案：黑白灰、莫兰迪色系、低饱和度
视觉元素：几何图形、简洁线条、负空间运用
整体感受：高级感、现代感、呼吸感""",
        "default_size": "2K",
        "description": "极简主义风格 - 克制优雅"
    },
    
    "水彩插画": {
        "template": """水彩插画艺术风格，主题：{keyword}

绘画技法：水彩晕染、色彩渐变、笔触自然
色彩特点：柔和温润、透明感、色彩流动
艺术氛围：清新文艺、手绘质感、温暖治愈
细节表现：水痕效果、颜料叠加、纸张纹理""",
        "default_size": "2K",
        "description": "水彩插画风格 - 温润治愈"
    },
}


def detect_template(user_input: str) -> Optional[str]:
    """检测用户输入中是否包含模板关键词
    
    Args:
        user_input: 用户输入的文本
        
    Returns:
        Optional[str]: 匹配的模板名称,如果没有匹配则返回None
    """
    user_input_lower = user_input.lower()
    
    # 检查是否包含模板关键词
    for template_name in PROMPT_TEMPLATES.keys():
        if template_name in user_input or template_name.lower() in user_input_lower:
            return template_name
    
    return None


def extract_keyword(user_input: str, template_name: str) -> Optional[str]:
    """从用户输入中提取关键词
    
    Args:
        user_input: 用户输入的文本
        template_name: 模板名称
        
    Returns:
        Optional[str]: 提取的关键词
    """
    # 尝试多种模式提取关键词
    patterns = [
        r'关键词[：:]\s*["\']?([^"\']+?)["\']?(?:\s|$)',  # 关键词："xxx"
        r'主题[：:]\s*["\']?([^"\']+?)["\']?(?:\s|$)',    # 主题："xxx"
        r'内容[：:]\s*["\']?([^"\']+?)["\']?(?:\s|$)',    # 内容："xxx"
        r'提示词[：:]\s*["\']?([^"\']+?)["\']?(?:\s|$)',  # 提示词："xxx"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_input)
        if match:
            keyword = match.group(1).strip()
            logger.info(f"提取到关键词: '{keyword}'")
            return keyword
    
    # 如果没有明确的关键词标记,尝试提取模板名称后的内容
    # 例如: "公众号封面 可口可乐"
    template_pattern = rf'{re.escape(template_name)}\s*[,，]?\s*(.+?)(?:\s|$)'
    match = re.search(template_pattern, user_input)
    if match:
        keyword = match.group(1).strip()
        # 移除可能的引号
        keyword = keyword.strip('"\'""''')
        logger.info(f"从模板名称后提取到关键词: '{keyword}'")
        return keyword
    
    return None


def apply_template(template_name: str, keyword: str) -> Tuple[str, Optional[str]]:
    """应用提示词模板
    
    Args:
        template_name: 模板名称
        keyword: 关键词
        
    Returns:
        Tuple[str, Optional[str]]: (格式化后的提示词, 默认尺寸)
    """
    if template_name not in PROMPT_TEMPLATES:
        logger.warning(f"未找到模板: {template_name}")
        return keyword, None
    
    template_config = PROMPT_TEMPLATES[template_name]
    template = template_config["template"]
    default_size = template_config.get("default_size")
    aspect_ratio = template_config.get("aspect_ratio")

    # 格式化模板
    formatted_prompt = template.format(keyword=keyword)

    # 如果模板指定了 aspect_ratio,在提示词末尾添加比例信息
    # 使用特殊格式,让 AI 理解这是参数而不是要渲染的文本
    if aspect_ratio:
        formatted_prompt = f"{formatted_prompt}\n\nratio: {aspect_ratio}"

    logger.info(f"应用模板 '{template_name}', 关键词: '{keyword}'")
    if aspect_ratio:
        logger.info(f"指定画面比例: {aspect_ratio}")
    logger.debug(f"格式化后的提示词: {formatted_prompt[:100]}...")

    return formatted_prompt, default_size


def process_user_input(user_input: str) -> Tuple[str, Optional[str], bool]:
    """处理用户输入,检测并应用模板
    
    Args:
        user_input: 用户输入的文本
        
    Returns:
        Tuple[str, Optional[str], bool]: (处理后的提示词, 默认尺寸, 是否应用了模板)
    """
    # 检测模板
    template_name = detect_template(user_input)
    
    if not template_name:
        # 没有检测到模板,返回原始输入
        return user_input, None, False
    
    # 提取关键词
    keyword = extract_keyword(user_input, template_name)
    
    if not keyword:
        logger.warning(f"检测到模板 '{template_name}' 但未能提取关键词")
        return user_input, None, False
    
    # 应用模板
    formatted_prompt, default_size = apply_template(template_name, keyword)
    
    return formatted_prompt, default_size, True


def get_available_templates() -> str:
    """获取所有可用模板的说明
    
    Returns:
        str: 模板列表的格式化文本
    """
    lines = ["📋 可用的提示词模板:\n"]
    
    for i, (name, config) in enumerate(PROMPT_TEMPLATES.items(), 1):
        lines.append(f"{i}. **{name}** - {config['description']}")
        lines.append(f"   默认尺寸: {config.get('default_size', '2K')}")
        lines.append("")
    
    lines.append("💡 使用方法:")
    lines.append('   "公众号封面，关键词：可口可乐"')
    lines.append('   "小红书封面 美食"')
    lines.append('   "产品海报，主题：iPhone"')
    
    return "\n".join(lines)

