"""
Seedream 4.0 MCP工具 - 参数验证模块

提供各种参数验证函数。
"""

import re
import os
from typing import List, Optional, Union
from urllib.parse import urlparse
from pathlib import Path

from .errors import SeedreamValidationError


def validate_prompt(prompt: str, max_length: int = 600) -> str:
    """验证文本提示词
    
    Args:
        prompt: 文本提示词
        max_length: 最大长度（英文单词数或汉字数）
        
    Returns:
        验证后的提示词
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    if not prompt or not isinstance(prompt, str):
        raise SeedreamValidationError("提示词不能为空", field="prompt", value=prompt)
    
    prompt = prompt.strip()
    if not prompt:
        raise SeedreamValidationError("提示词不能为空", field="prompt", value=prompt)
    
    # 检查长度（简单的字符数检查）
    if len(prompt) > max_length:
        raise SeedreamValidationError(
            f"提示词过长，建议不超过{max_length}个字符（当前{len(prompt)}个字符）",
            field="prompt",
            value=prompt
        )
    
    return prompt


def validate_size(size: str) -> str:
    """验证图像尺寸参数
    
    Args:
        size: 图像尺寸
        
    Returns:
        验证后的尺寸
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    valid_sizes = ["1K", "2K", "4K"]
    
    if not size or not isinstance(size, str):
        raise SeedreamValidationError("图像尺寸不能为空", field="size", value=size)
    
    size = size.strip().upper()
    if size not in valid_sizes:
        raise SeedreamValidationError(
            f"图像尺寸必须是以下值之一: {valid_sizes}",
            field="size",
            value=size
        )
    
    return size


def validate_image_url(image: str) -> str:
    """验证图像URL或文件路径
    
    Args:
        image: 图像URL或文件路径
        
    Returns:
        验证后的图像路径
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    if not image or not isinstance(image, str):
        raise SeedreamValidationError("图像路径不能为空", field="image", value=image)
    
    image = image.strip()
    if not image:
        raise SeedreamValidationError("图像路径不能为空", field="image", value=image)
    
    # 检查是否为URL
    if image.startswith(("http://", "https://")):
        return _validate_url(image)
    else:
        return _validate_file_path(image)


def validate_image_list(images: List[str], min_count: int = 1, max_count: int = 5) -> List[str]:
    """验证图像列表
    
    Args:
        images: 图像URL或文件路径列表
        min_count: 最小数量
        max_count: 最大数量
        
    Returns:
        验证后的图像路径列表
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    if not images or not isinstance(images, list):
        raise SeedreamValidationError("图像列表不能为空", field="images", value=images)
    
    if len(images) < min_count:
        raise SeedreamValidationError(
            f"图像数量不能少于{min_count}张",
            field="images",
            value=images
        )
    
    if len(images) > max_count:
        raise SeedreamValidationError(
            f"图像数量不能超过{max_count}张",
            field="images",
            value=images
        )
    
    # 验证每个图像路径
    validated_images = []
    for i, image in enumerate(images):
        try:
            validated_image = validate_image_url(image)
            validated_images.append(validated_image)
        except SeedreamValidationError as e:
            raise SeedreamValidationError(
                f"第{i+1}张图像验证失败: {e.message}",
                field=f"images[{i}]",
                value=image
            )
    
    return validated_images


def validate_max_images(max_images: int) -> int:
    """验证最大图像数量
    
    Args:
        max_images: 最大图像数量
        
    Returns:
        验证后的数量
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    if not isinstance(max_images, int):
        try:
            max_images = int(max_images)
        except (ValueError, TypeError):
            raise SeedreamValidationError(
                "最大图像数量必须是整数",
                field="max_images",
                value=max_images
            )
    
    if max_images < 1:
        raise SeedreamValidationError(
            "最大图像数量不能小于1",
            field="max_images",
            value=max_images
        )
    
    if max_images > 10:
        raise SeedreamValidationError(
            "最大图像数量不能超过10",
            field="max_images",
            value=max_images
        )
    
    return max_images


def validate_watermark(watermark: Union[bool, str]) -> bool:
    """验证水印参数
    
    Args:
        watermark: 水印设置
        
    Returns:
        验证后的布尔值
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    if isinstance(watermark, bool):
        return watermark
    
    if isinstance(watermark, str):
        watermark_lower = watermark.lower().strip()
        if watermark_lower in ("true", "1", "yes", "on"):
            return True
        elif watermark_lower in ("false", "0", "no", "off"):
            return False
        else:
            raise SeedreamValidationError(
                "水印参数必须是布尔值或有效的字符串（true/false）",
                field="watermark",
                value=watermark
            )
    
    raise SeedreamValidationError(
        "水印参数必须是布尔值",
        field="watermark",
        value=watermark
    )


def validate_response_format(response_format: str) -> str:
    """验证响应格式
    
    Args:
        response_format: 响应格式
        
    Returns:
        验证后的格式
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    valid_formats = ["url", "b64_json"]
    
    if not response_format or not isinstance(response_format, str):
        raise SeedreamValidationError(
            "响应格式不能为空",
            field="response_format",
            value=response_format
        )
    
    response_format = response_format.strip().lower()
    if response_format not in valid_formats:
        raise SeedreamValidationError(
            f"响应格式必须是以下值之一: {valid_formats}",
            field="response_format",
            value=response_format
        )
    
    return response_format


def _validate_url(url: str) -> str:
    """验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        验证后的URL
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise SeedreamValidationError(
                "无效的URL格式",
                field="image",
                value=url
            )
        
        # 检查是否为图像URL（简单检查）
        if parsed.path:
            path_lower = parsed.path.lower()
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            if not any(path_lower.endswith(ext) for ext in image_extensions):
                # 如果没有明显的图像扩展名，给出警告但不阻止
                pass
        
        return url
        
    except Exception as e:
        raise SeedreamValidationError(
            f"URL验证失败: {str(e)}",
            field="image",
            value=url
        )


def _validate_file_path(file_path: str) -> str:
    """验证文件路径
    
    Args:
        file_path: 文件路径
        
    Returns:
        验证后的文件路径
        
    Raises:
        SeedreamValidationError: 验证失败时抛出
    """
    try:
        path = Path(file_path)
        
        # 检查文件是否存在
        if not path.exists():
            raise SeedreamValidationError(
                f"文件不存在: {file_path}",
                field="image",
                value=file_path
            )
        
        # 检查是否为文件
        if not path.is_file():
            raise SeedreamValidationError(
                f"路径不是文件: {file_path}",
                field="image",
                value=file_path
            )
        
        # 检查文件扩展名
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        if path.suffix.lower() not in image_extensions:
            raise SeedreamValidationError(
                f"不支持的图像格式: {path.suffix}，支持的格式: {image_extensions}",
                field="image",
                value=file_path
            )
        
        # 检查文件大小（限制为50MB）
        file_size = path.stat().st_size
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            raise SeedreamValidationError(
                f"文件过大: {file_size / 1024 / 1024:.1f}MB，最大支持50MB",
                field="image",
                value=file_path
            )
        
        return str(path.absolute())
        
    except SeedreamValidationError:
        raise
    except Exception as e:
        raise SeedreamValidationError(
            f"文件路径验证失败: {str(e)}",
            field="image",
            value=file_path
        )