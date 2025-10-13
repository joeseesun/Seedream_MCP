"""
Seedream 4.0 MCP工具 - 多图融合工具

实现多张图像融合生成功能，支持自动保存生成的图片到本地。
"""

from typing import Any, Dict, List, Optional
from mcp.types import Tool, TextContent

from ..client import SeedreamClient
from ..config import SeedreamConfig, get_global_config
from ..utils.logging import get_logger
from ..utils.auto_save import AutoSaveManager, AutoSaveResult


# 工具定义
multi_image_fusion_tool = Tool(
    name="seedream_multi_image_fusion",
    description="使用Seedream 4.0将多张图像融合生成新图像，支持自动保存到本地",
    inputSchema={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "图像生成的文本提示词，建议不超过600个字符",
                "maxLength": 600
            },
            "images": {
                "type": "array",
                "description": "输入图像的URL或本地文件路径列表（2-5张图像）",
                "items": {
                    "type": "string",
                    "description": "图像URL或文件路径"
                },
                "minItems": 2,
                "maxItems": 5
            },
            "size": {
                "type": "string",
                "description": "生成图像的尺寸，如果不指定则使用配置文件中的默认值",
                "enum": ["1K", "2K", "4K"]
            },
            "watermark": {
                "type": "boolean",
                "description": "是否在生成的图像上添加水印，如果不指定则使用配置文件中的默认值"
            },
            "response_format": {
                "type": "string",
                "description": "响应格式：url返回图像URL，b64_json返回base64编码",
                "enum": ["url", "b64_json"],
                "default": "url"
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
        "required": ["prompt", "images"]
    }
)


async def handle_multi_image_fusion(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理多图融合请求
    
    Args:
        arguments: 工具参数
        
    Returns:
        MCP响应内容
    """
    logger = get_logger(__name__)
    
    try:
        # 获取配置
        config = get_global_config()
        
        # 提取参数，按优先级：调用参数 > 配置文件默认值 > 方法默认值
        prompt = arguments.get("prompt")
        images = arguments.get("images", [])
        size = arguments.get("size") or config.default_size
        watermark = arguments.get("watermark")
        if watermark is None:
            watermark = config.default_watermark
        response_format = arguments.get("response_format", "url")
        auto_save = arguments.get("auto_save")
        save_path = arguments.get("save_path")
        custom_name = arguments.get("custom_name")
        
        logger.info(f"开始处理多图融合请求: prompt='{prompt[:50]}...', size={size}, 图片数量={len(images)}")
        
        # 确定是否启用自动保存
        enable_auto_save = auto_save if auto_save is not None else config.auto_save_enabled
        
        # 创建客户端并调用API
        async with SeedreamClient(config) as client:
            result = await client.multi_image_fusion(
                prompt=prompt,
                images=images,
                size=size,
                watermark=watermark,
                response_format=response_format
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
        response_text = _format_multi_image_fusion_response(
            result, prompt, images, size, auto_save_results, enable_auto_save
        )
        
        logger.info("多图融合请求处理完成")
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"多图融合请求处理失败: {str(e)}")
        error_msg = f"多图融合生成失败: {str(e)}"
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


def _format_multi_image_fusion_response(
    result: Dict[str, Any], 
    prompt: str, 
    input_images: List[str], 
    size: str,
    auto_save_results: Optional[List[AutoSaveResult]] = None,
    auto_save_enabled: bool = False
) -> str:
    """格式化多图融合响应
    
    Args:
        result: API响应结果
        prompt: 原始提示词
        input_images: 输入图像路径列表
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
        "✅ 多图融合任务完成",
        "",
        f"📝 提示词: {prompt}",
        f"🖼️ 输入图像数量: {len(input_images)}张",
        f"📏 尺寸: {size}",
        ""
    ]
    
    # 显示输入图像信息
    response_lines.append("📥 输入图像:")
    for i, image in enumerate(input_images, 1):
        formatted_path = _format_image_path(image)
        response_lines.append(f"  {i}. {formatted_path}")
    
    response_lines.append("")
    
    # 处理生成的图像
    if isinstance(data, list):
        images = data
    elif isinstance(data, dict) and "data" in data:
        images = data["data"]
    else:
        images = [data]
    
    if images:
        response_lines.append("🎨 融合生成的图像:")
        for i, image in enumerate(images, 1):
            if isinstance(image, dict):
                if "url" in image:
                    response_lines.append(f"  {i}. 图像URL: {image['url']}")
                    # 添加本地路径信息（如果有）
                    if "local_path" in image:
                        response_lines.append(f"     💾 本地路径: {image['local_path']}")
                    if "markdown_ref" in image:
                        response_lines.append(f"     📝 Markdown引用: {image['markdown_ref']}")
                elif "b64_json" in image:
                    response_lines.append(f"  {i}. 图像数据: [Base64编码，长度: {len(image['b64_json'])}字符]")
                elif "revised_prompt" in image:
                    response_lines.append(f"  {i}. 修订提示词: {image['revised_prompt']}")
            else:
                response_lines.append(f"  {i}. {str(image)}")
    
    # 添加使用统计
    if usage:
        response_lines.extend([
            "",
            "📊 使用统计:"
        ])
        if "prompt_tokens" in usage:
            response_lines.append(f"  • 提示词令牌数: {usage['prompt_tokens']}")
        if "total_tokens" in usage:
            response_lines.append(f"  • 总令牌数: {usage['total_tokens']}")
        if "cost" in usage:
            response_lines.append(f"  • 费用: {usage['cost']}")
    
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
    
    # 添加融合提示
    response_lines.extend([
        "",
        "💡 融合说明:",
        "  • 多图融合将输入的多张图像进行智能融合",
        "  • 生成的图像会综合所有输入图像的特征",
        "  • 文本提示词用于指导融合的风格和内容"
    ])
    
    return "\n".join(response_lines)


def _format_image_path(image_path: str) -> str:
    """格式化图像路径显示
    
    Args:
        image_path: 图像路径
        
    Returns:
        格式化的路径字符串
    """
    if image_path.startswith(("http://", "https://")):
        return f"URL: {image_path}"
    else:
        # 只显示文件名，避免路径过长
        from pathlib import Path
        try:
            filename = Path(image_path).name
            return f"文件: {filename}"
        except:
            return f"文件: {image_path}"