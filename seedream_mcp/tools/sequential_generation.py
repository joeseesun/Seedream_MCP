"""
Seedream 4.0 MCP工具 - 组图生成工具

实现连续生成多张图像功能，支持自动保存到本地。
"""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path
from mcp.types import Tool, TextContent

from ..client import SeedreamClient
from ..config import SeedreamConfig, get_global_config
from ..utils.errors import SeedreamMCPError
from ..utils.logging import get_logger
from ..utils.auto_save import AutoSaveManager, AutoSaveResult


# 工具定义
sequential_generation_tool = Tool(
    name="seedream_sequential_generation",
    description="使用Seedream 4.0连续生成多张图像（组图生成），支持3种输入类型：文生组图、单图生组图、多图生组图，支持自动保存到本地",
    inputSchema={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "图像生成的文本提示词，建议不超过600个字符",
                "maxLength": 600
            },
            "max_images": {
                "type": "integer",
                "description": "最大生成图像数量",
                "minimum": 1,
                "maximum": 15,
                "default": 4
            },
            "size": {
                "type": "string",
                "description": "生成图像的尺寸",
                "enum": ["1K", "2K", "4K"],
                "default": "2K"
            },
            "watermark": {
                "type": "boolean",
                "description": "是否在生成的图像上添加水印",
                "default": True
            },
            "response_format": {
                "type": "string",
                "description": "响应格式：url返回图像URL，b64_json返回base64编码",
                "enum": ["url", "b64_json"],
                "default": "url"
            },
            "image": {
                "type": ["string", "array"],
                "description": "可选的参考图像。支持单张图片URL/路径（字符串）或多张图片URL/路径（字符串数组）。用于单图生组图或多图生组图",
                "items": {
                    "type": "string"
                },
                "maxItems": 10
            },
            "auto_save": {
                "type": "boolean",
                "description": "是否自动保存生成的图片到本地。如果未指定，将使用全局配置",
                "default": None
            },
            "save_path": {
                "type": "string",
                "description": "自定义保存目录路径。如果未指定，将使用默认配置路径"
            },
            "custom_name": {
                "type": "string",
                "description": "自定义文件名前缀。如果未指定，将根据提示词自动生成"
            }
        },
        "required": ["prompt"]
    }
)


async def handle_sequential_generation(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理组图生成请求
    
    Args:
        arguments: 工具参数
        
    Returns:
        MCP响应内容
        
    Raises:
        SeedreamMCPError: 处理失败时抛出
    """
    logger = get_logger(__name__)
    
    try:
        # 提取基本参数
        prompt = arguments.get("prompt")
        max_images = arguments.get("max_images", 4)
        size = arguments.get("size", "2K")
        watermark = arguments.get("watermark", True)
        response_format = arguments.get("response_format", "url")
        image = arguments.get("image")
        
        # 提取自动保存参数
        auto_save = arguments.get("auto_save")
        save_path = arguments.get("save_path")
        custom_name = arguments.get("custom_name")
        
        # 验证参数
        if not prompt:
            return [TextContent(type="text", text="错误：prompt参数是必需的")]
        
        if max_images < 1 or max_images > 15:
            return [TextContent(type="text", text="错误：max_images必须在1-15之间")]
        
        if size not in ["1K", "2K", "4K"]:
            return [TextContent(type="text", text="错误：size必须是1K、2K或4K")]
        
        if response_format not in ["url", "b64_json"]:
            return [TextContent(type="text", text="错误：response_format必须是url或b64_json")]
        
        # 验证image参数
        if image is not None:
            if isinstance(image, str):
                # 单张图片
                if not image.strip():
                    return [TextContent(type="text", text="错误：image参数不能为空字符串")]
            elif isinstance(image, list):
                # 多张图片
                if len(image) == 0:
                    return [TextContent(type="text", text="错误：image数组不能为空")]
                if len(image) > 10:
                    return [TextContent(type="text", text="错误：最多支持10张参考图片")]
                for img in image:
                    if not isinstance(img, str) or not img.strip():
                        return [TextContent(type="text", text="错误：image数组中的每个元素都必须是非空字符串")]
            else:
                return [TextContent(type="text", text="错误：image参数必须是字符串或字符串数组")]
        
        logger.info(f"开始处理组图生成请求: prompt='{prompt[:50]}...', max_images={max_images}, size={size}")
        
        # 获取配置
        config = get_global_config()
        
        # 确定是否启用自动保存
        enable_auto_save = auto_save if auto_save is not None else config.auto_save_enabled
        
        # 创建客户端并调用API
        async with SeedreamClient(config) as client:
            result = await client.sequential_generation(
                prompt=prompt,
                max_images=max_images,
                size=size,
                watermark=watermark,
                response_format=response_format,
                image=image
            )
        
        # 初始化自动保存结果
        auto_save_results = []
        
        # 如果启用自动保存且API调用成功，执行自动保存
        if enable_auto_save and result.get("success") and response_format == "url":
            try:
                auto_save_results = await _handle_auto_save(
                    result, prompt, config, save_path, custom_name
                )
                
                # 更新结果以包含自动保存信息
                if auto_save_results:
                    result = _update_result_with_auto_save(result, auto_save_results)
                    
            except Exception as e:
                logger.warning(f"自动保存失败，但继续返回原始结果: {e}")
        
        # 格式化响应
        response_text = _format_sequential_generation_response(
            result, prompt, max_images, size, auto_save_results, enable_auto_save
        )
        
        logger.info("组图生成请求处理完成")
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"组图生成请求处理失败: {str(e)}")
        error_msg = f"组图生成失败: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def _handle_auto_save(
    result: Dict[str, Any],
    prompt: str,
    config: SeedreamConfig,
    save_path: Optional[str] = None,
    custom_name: Optional[str] = None
) -> List[AutoSaveResult]:
    """处理自动保存逻辑
    
    Args:
        result: API响应结果
        prompt: 生成提示词
        config: 配置对象
        save_path: 自定义保存路径
        custom_name: 自定义文件名前缀
        
    Returns:
        自动保存结果列表
    """
    # 初始化自动保存管理器
    auto_save_manager = AutoSaveManager(config)
    
    # 提取图片URL
    image_urls = []
    if result.get("data"):
        for item in result["data"]:
            if item.get("url"):
                image_urls.append(item["url"])
    
    if not image_urls:
        return []
    
    # 准备图片数据
    image_data = []
    for i, url in enumerate(image_urls):
        data = {
            "url": url,
            "prompt": prompt,
            "custom_name": custom_name
        }
        image_data.append(data)
    
    # 执行批量保存
    return await auto_save_manager.save_multiple_images(
        image_data, save_path
    )


def _update_result_with_auto_save(
    result: Dict[str, Any],
    auto_save_results: List[AutoSaveResult]
) -> Dict[str, Any]:
    """更新结果以包含自动保存信息
    
    Args:
        result: 原始API结果
        auto_save_results: 自动保存结果列表
        
    Returns:
        更新后的结果
    """
    # 创建结果副本
    updated_result = result.copy()
    
    # 统计保存结果
    successful_saves = sum(1 for r in auto_save_results if r.success)
    failed_saves = len(auto_save_results) - successful_saves
    
    # 添加自动保存统计信息
    updated_result["auto_save_summary"] = {
        "total": len(auto_save_results),
        "successful": successful_saves,
        "failed": failed_saves
    }
    
    # 为成功保存的图片添加本地路径信息
    if updated_result.get("data") and auto_save_results:
        for i, (item, save_result) in enumerate(zip(updated_result["data"], auto_save_results)):
            if save_result.success:
                item["local_path"] = str(save_result.local_path)
                item["markdown_ref"] = save_result.markdown_ref
    
    return updated_result


def _format_sequential_generation_response(
    result: Dict[str, Any], 
    prompt: str, 
    max_images: int, 
    size: str,
    auto_save_results: Optional[List[AutoSaveResult]] = None,
    auto_save_enabled: bool = False
) -> str:
    """格式化组图生成响应
    
    Args:
        result: API响应结果
        prompt: 原始提示词
        max_images: 最大图像数量
        size: 图像尺寸
        
    Returns:
        格式化的响应文本
    """
    if not result.get("success"):
        return f"图像生成失败: {result.get('error', '未知错误')}"
    
    data = result.get("data", {})
    usage = result.get("usage", {})
    
    # 构建响应文本
    response_lines = [
        "✅ 组图生成任务完成",
        "",
        f"📝 提示词: {prompt}",
        f"🔢 请求生成数量: {max_images}张",
        f"📏 尺寸: {size}",
        ""
    ]
    
    # 处理生成的图像
    if isinstance(data, list):
        images = data
    elif isinstance(data, dict) and "data" in data:
        images = data["data"]
    else:
        images = [data]
    
    if images:
        actual_count = len(images)
        response_lines.append(f"🎨 实际生成图像: {actual_count}张")
        response_lines.append("")
        
        for i, image in enumerate(images, 1):
            response_lines.append(f"📷 图像 {i}:")
            if isinstance(image, dict):
                if "url" in image:
                    response_lines.append(f"  • URL: {image['url']}")
                    # 添加本地路径信息（如果有）
                    if "local_path" in image:
                        response_lines.append(f"  • 💾 本地路径: {image['local_path']}")
                    if "markdown_ref" in image:
                        response_lines.append(f"  • 📝 Markdown引用: {image['markdown_ref']}")
                elif "b64_json" in image:
                    response_lines.append(f"  • 数据: [Base64编码，长度: {len(image['b64_json'])}字符]")
                if "revised_prompt" in image:
                    response_lines.append(f"  • 修订提示词: {image['revised_prompt']}")
            else:
                response_lines.append(f"  • {str(image)}")
            response_lines.append("")
        
        # 生成数量统计
        if actual_count != max_images:
            response_lines.append(f"ℹ️ 注意: 请求生成{max_images}张，实际生成{actual_count}张")
            response_lines.append("")
    
    # 添加使用统计
    if usage:
        response_lines.extend([
            "📊 使用统计:"
        ])
        if "prompt_tokens" in usage:
            response_lines.append(f"  • 提示词令牌数: {usage['prompt_tokens']}")
        if "total_tokens" in usage:
            response_lines.append(f"  • 总令牌数: {usage['total_tokens']}")
        if "cost" in usage:
            response_lines.append(f"  • 费用: {usage['cost']}")
        response_lines.append("")
    
    # 添加自动保存摘要（如果启用）
    if auto_save_enabled and auto_save_results:
        successful_saves = sum(1 for r in auto_save_results if r.success)
        failed_saves = len(auto_save_results) - successful_saves
        
        response_lines.extend([
            "",
            "💾 自动保存摘要:",
            f"  • 总计: {len(auto_save_results)}张图片",
            f"  • 成功: {successful_saves}张",
            f"  • 失败: {failed_saves}张"
        ])
    
    # 添加组图生成说明
    response_lines.extend([
        "",
        "💡 组图生成说明:",
        "  • 组图生成会基于同一个提示词生成多张不同的图像",
        "  • 每张图像都是独立生成的，会有不同的视觉效果",
        "  • 适用于需要多个设计方案或创意选择的场景",
        "  • 可以从生成的多张图像中选择最满意的结果"
    ])
    
    return "\n".join(response_lines)