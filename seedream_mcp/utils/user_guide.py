"""
Seedream 4.0 MCP工具 - 用户指导模块

提供清晰的文件路径使用指导和错误提示。
"""

from typing import List, Dict, Any


def get_path_usage_guide() -> str:
    """
    获取文件路径使用指导
    
    Returns:
        包含详细使用指导的字符串
    """
    guide = """
📁 Seedream MCP工具 - 文件路径使用指导

支持的图片格式:
  • JPEG (.jpg, .jpeg)
  • PNG (.png)
  • GIF (.gif)
  • BMP (.bmp)
  • TIFF (.tiff, .tif)
  • WebP (.webp)
  • SVG (.svg)
  • ICO (.ico)

支持的路径格式:

1. 绝对路径:
   • Windows: C:\\Users\\用户名\\Pictures\\image.jpg
   • Windows: D:\\项目\\images\\photo.png
   
2. 相对路径:
   • 相对于当前工作目录: images/photo.jpg
   • 相对于当前工作目录: ./assets/image.png
   • 上级目录: ../images/photo.jpg

3. 网络URL:
   • https://example.com/image.jpg
   • http://example.com/photo.png

使用建议:
  • 使用正斜杠 (/) 或反斜杠 (\\) 都可以
  • 路径中包含空格时，无需添加引号
  • 推荐使用相对路径，便于项目移植

常见错误及解决方案:
  • 文件不存在: 检查路径是否正确，文件是否存在
  • 格式不支持: 确保文件是支持的图片格式
  • 权限不足: 确保有读取文件的权限
  • 路径过长: Windows系统路径长度限制为260字符

快速查找图片文件:
  使用 seedream_browse_images 工具浏览工作区中的图片文件
"""
    return guide.strip()


def get_error_solutions() -> Dict[str, str]:
    """
    获取常见错误的解决方案
    
    Returns:
        错误类型到解决方案的映射
    """
    return {
        "file_not_found": """
文件未找到解决方案:
1. 检查文件路径是否正确
2. 确认文件确实存在
3. 尝试使用绝对路径
4. 使用 seedream_browse_images 工具查找图片文件
""",
        "invalid_format": """
不支持的文件格式解决方案:
1. 确保文件是图片格式
2. 支持的格式: JPG, PNG, GIF, BMP, TIFF, WebP, SVG, ICO
3. 检查文件扩展名是否正确
4. 尝试转换为支持的格式
""",
        "permission_denied": """
权限不足解决方案:
1. 确保有读取文件的权限
2. 检查文件是否被其他程序占用
3. 尝试以管理员身份运行
4. 检查文件属性，取消只读属性
""",
        "path_too_long": """
路径过长解决方案:
1. 使用相对路径代替绝对路径
2. 移动文件到更短的路径
3. 重命名文件夹，使用更短的名称
4. 在Windows中启用长路径支持
""",
        "encoding_error": """
编码错误解决方案:
1. 确保文件路径不包含特殊字符
2. 避免使用非ASCII字符命名文件
3. 检查文件是否损坏
4. 尝试重新保存文件
"""
    }


def format_error_message(error_type: str, original_path: str, suggestions: List[str] = None) -> str:
    """
    格式化错误消息，提供有用的指导
    
    Args:
        error_type: 错误类型
        original_path: 原始路径
        suggestions: 路径建议列表
    
    Returns:
        格式化的错误消息
    """
    solutions = get_error_solutions()
    base_message = f"处理图片路径时出错: {original_path}"
    
    # 添加具体的解决方案
    if error_type in solutions:
        base_message += f"\n\n{solutions[error_type]}"
    
    # 添加路径建议
    if suggestions:
        base_message += f"\n\n💡 建议的相似路径:\n"
        for i, suggestion in enumerate(suggestions[:3], 1):
            base_message += f"  {i}. {suggestion}\n"
    
    # 添加通用指导
    base_message += f"\n\n📖 获取完整使用指导，请使用: seedream_browse_images 工具"
    
    return base_message


def get_quick_tips() -> List[str]:
    """
    获取快速使用技巧
    
    Returns:
        技巧列表
    """
    return [
        "💡 使用 seedream_browse_images 工具快速查找工作区中的图片文件",
        "💡 相对路径更便于项目移植，推荐使用",
        "💡 支持网络图片URL，可直接使用在线图片",
        "💡 路径中的正斜杠和反斜杠都可以使用",
        "💡 文件名包含空格时无需添加引号",
        "💡 支持多种图片格式，包括 JPG、PNG、GIF、WebP 等"
    ]


def validate_and_suggest_path(path: str) -> Dict[str, Any]:
    """
    验证路径并提供建议
    
    Args:
        path: 要验证的路径
    
    Returns:
        包含验证结果和建议的字典
    """
    from .path_utils import validate_image_path, suggest_similar_paths
    
    is_valid, error_msg, normalized_path = validate_image_path(path)
    
    result = {
        "is_valid": is_valid,
        "error_message": error_msg,
        "normalized_path": str(normalized_path) if normalized_path else None,
        "suggestions": [],
        "tips": []
    }
    
    if not is_valid:
        # 获取路径建议
        suggestions = suggest_similar_paths(path)
        result["suggestions"] = suggestions
        
        # 根据错误类型提供特定建议
        if "不存在" in error_msg:
            result["tips"].extend([
                "检查文件路径是否正确",
                "确认文件确实存在",
                "尝试使用绝对路径",
                "使用 seedream_browse_images 工具查找图片"
            ])
        elif "格式" in error_msg:
            result["tips"].extend([
                "确保文件是图片格式",
                "检查文件扩展名是否正确",
                "支持的格式: JPG, PNG, GIF, BMP, TIFF, WebP, SVG, ICO"
            ])
        elif "权限" in error_msg:
            result["tips"].extend([
                "确保有读取文件的权限",
                "检查文件是否被占用",
                "尝试以管理员身份运行"
            ])
    
    return result