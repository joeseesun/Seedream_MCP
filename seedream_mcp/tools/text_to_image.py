"""
Seedream 4.0 MCP工具 - 文生图工具

实现文本到图像生成功能，支持自动保存。
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from mcp.types import Tool, TextContent, ImageContent

from ..client import SeedreamClient
from ..config import SeedreamConfig, get_global_config
from ..utils.logging import get_logger
from ..utils.auto_save import AutoSaveManager
from ..prompt_templates import process_user_input
from .image_helpers import create_image_content_response


# 工具定义
text_to_image_tool = Tool(
    name="seedream_text_to_image",
    description="使用Seedream 4.0根据文本提示词生成【单张】图像。如果需要生成多张图片，请使用 seedream_sequential_generation 工具",
    inputSchema={
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "图像生成的文本提示词。可以是简单的几个字（如'一只小猫'）或详细的描述（如'一只可爱的橘色小猫咪，坐在窗台上，阳光洒在身上，卡通风格，高清画质'）。建议不超过600个字符",
                "maxLength": 600
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
                "description": "响应格式：url返回图像URL，b64_json返回base64编码，image返回MCP ImageContent（直接显示图片）",
                "enum": ["url", "b64_json", "image"],
                "default": "image"
            },
            "auto_save": {
                "type": "boolean",
                "description": "是否自动保存图片到本地（默认使用全局配置）",
                "default": None
            },
            "save_path": {
                "type": "string",
                "description": "自定义保存目录路径（可选）"
            },
            "custom_name": {
                "type": "string",
                "description": "自定义文件名前缀（可选）"
            }
        },
        "required": ["prompt"]
    }
)


async def handle_text_to_image(arguments: Dict[str, Any]) -> List[Union[TextContent, ImageContent]]:
    """处理文生图请求

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
        size = arguments.get("size") or config.default_size
        watermark = arguments.get("watermark")
        if watermark is None:
            watermark = config.default_watermark
        response_format = arguments.get("response_format", "image")
        auto_save = arguments.get("auto_save")
        save_path = arguments.get("save_path")
        custom_name = arguments.get("custom_name")

        # ⭐ 处理提示词模板
        original_prompt = prompt
        processed_prompt, template_size, template_applied = process_user_input(prompt)

        if template_applied:
            logger.info(f"✨ 应用了提示词模板")
            logger.info(f"原始输入: '{original_prompt}'")
            logger.info(f"处理后提示词: '{processed_prompt[:100]}...'")
            prompt = processed_prompt

            # 如果模板指定了默认尺寸且用户没有指定,使用模板的默认尺寸
            if template_size and not arguments.get("size"):
                size = template_size
                logger.info(f"使用模板默认尺寸: {size}")

        logger.info(f"开始处理文生图请求: prompt='{prompt[:50]}...', size={size}, format={response_format}")

        # 确定是否启用自动保存
        enable_auto_save = auto_save if auto_save is not None else config.auto_save_enabled

        # 如果是 image 格式，需要从 API 获取 URL 然后下载
        api_format = "url" if response_format == "image" else response_format

        # 创建客户端并调用API
        async with SeedreamClient(config) as client:
            result = await client.text_to_image(
                prompt=prompt,
                size=size,
                watermark=watermark,
                response_format=api_format
            )

        # 处理自动保存
        auto_save_results = []
        if enable_auto_save and result.get("success"):
            if api_format == "url":
                auto_save_results = await _handle_auto_save(
                    result, prompt, config, save_path, custom_name
                )
                if auto_save_results:
                    result = _update_result_with_auto_save(result, auto_save_results)
            elif api_format == "b64_json":
                auto_save_results = await _handle_auto_save_base64(
                    result, prompt, config, save_path, custom_name
                )
                if auto_save_results:
                    result = _update_result_with_auto_save(result, auto_save_results)

        # 如果请求的是 image 格式，返回 ImageContent
        if response_format == "image" and result.get("success"):
            return await create_image_content_response(result, prompt, size)

        # 格式化响应
        response_text = _format_text_to_image_response(
            result, prompt, size, auto_save_results, enable_auto_save
        )

        logger.info("文生图请求处理完成")
        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"文生图请求处理失败: {str(e)}")
        error_msg = f"文生图生成失败: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def _handle_auto_save(
    result: Dict[str, Any],
    prompt: str,
    config: SeedreamConfig,
    save_path: Optional[str] = None,
    custom_name: Optional[str] = None
) -> List:
    """处理自动保存

    Args:
        result: API响应结果
        prompt: 提示词
        config: 配置对象
        save_path: 自定义保存路径
        custom_name: 自定义文件名

    Returns:
        自动保存结果列表
    """
    logger = get_logger(__name__)
    
    try:
        # 创建自动保存管理器
        base_dir = Path(save_path) if save_path else (
            Path(config.auto_save_base_dir) if config.auto_save_base_dir else None
        )
        
        auto_save_manager = AutoSaveManager(
            base_dir=base_dir,
            download_timeout=config.auto_save_download_timeout,
            max_retries=config.auto_save_max_retries,
            max_file_size=config.auto_save_max_file_size,
            max_concurrent=config.auto_save_max_concurrent
        )
        
        # 提取图片URL
        data = result.get("data", {})
        if isinstance(data, list):
            images = data
        elif isinstance(data, dict) and "data" in data:
            images = data["data"]
        else:
            images = [data]
        
        # 准备保存数据
        image_data = []
        for i, image in enumerate(images):
            if isinstance(image, dict) and "url" in image:
                image_data.append({
                    'url': image['url'],
                    'prompt': prompt,
                    'custom_name': f"{custom_name}_{i+1}" if custom_name else None,
                    'alt_text': f"Generated image {i+1}: {prompt[:50]}..."
                })
        
        if not image_data:
            logger.warning("未找到可保存的图片URL")
            return []
        
        # 执行批量保存
        auto_save_results = await auto_save_manager.save_multiple_images(
            image_data, tool_name="text_to_image"
        )
        
        logger.info(f"自动保存完成: {len(auto_save_results)} 个图片")
        return auto_save_results
        
    except Exception as e:
        logger.error(f"自动保存失败: {e}")
        return []


async def _handle_auto_save_base64(
    result: Dict[str, Any], 
    prompt: str, 
    config: SeedreamConfig,
    save_path: Optional[str] = None,
    custom_name: Optional[str] = None
) -> List:
    """处理 base64 自动保存
    
    当 response_format 为 b64_json 时，从结果中提取 base64 并保存到本地。
    """
    logger = get_logger(__name__)
    try:
        base_dir = Path(save_path) if save_path else (
            Path(config.auto_save_base_dir) if config.auto_save_base_dir else None
        )

        auto_save_manager = AutoSaveManager(
            base_dir=base_dir,
            download_timeout=config.auto_save_download_timeout,
            max_retries=config.auto_save_max_retries,
            max_file_size=config.auto_save_max_file_size,
            max_concurrent=config.auto_save_max_concurrent
        )

        data = result.get("data", {})
        if isinstance(data, list):
            images = data
        elif isinstance(data, dict) and "data" in data:
            images = data["data"]
        else:
            images = [data]

        image_data = []
        for i, image in enumerate(images):
            if isinstance(image, dict) and "b64_json" in image:
                image_data.append({
                    'b64_json': image['b64_json'],
                    'prompt': prompt,
                    'custom_name': f"{custom_name}_{i+1}" if custom_name else None,
                    'alt_text': f"Generated image {i+1}: {prompt[:50]}..."
                })

        if not image_data:
            logger.warning("未找到可保存的Base64图片数据")
            return []

        auto_save_results = await auto_save_manager.save_multiple_base64_images(
            image_data, tool_name="text_to_image"
        )
        logger.info(f"Base64 自动保存完成: {len(auto_save_results)} 个图片")
        return auto_save_results
    except Exception as e:
        logger.error(f"Base64 自动保存失败: {e}")
        return []


def _update_result_with_auto_save(result: Dict[str, Any], auto_save_results: List) -> Dict[str, Any]:
    """更新结果以包含自动保存信息
    
    Args:
        result: 原始结果
        auto_save_results: 自动保存结果
        
    Returns:
        更新后的结果
    """
    # 创建结果副本
    updated_result = result.copy()
    
    # 添加自动保存信息
    auto_save_info = {
        'enabled': True,
        'total_images': len(auto_save_results),
        'successful_saves': sum(1 for r in auto_save_results if r.success),
        'failed_saves': sum(1 for r in auto_save_results if not r.success),
        'results': [r.to_dict() for r in auto_save_results]
    }
    
    updated_result['auto_save'] = auto_save_info
    
    # 更新图片信息
    data = updated_result.get("data", {})
    if isinstance(data, list):
        images = data
    elif isinstance(data, dict) and "data" in data:
        images = data["data"]
    else:
        images = [data]
    
    for i, (image, save_result) in enumerate(zip(images, auto_save_results)):
        if isinstance(image, dict) and save_result.success:
            image['local_path'] = save_result.local_path
            image['markdown_ref'] = save_result.markdown_ref
    
    return updated_result


def _format_text_to_image_response(
    result: Dict[str, Any], 
    prompt: str, 
    size: str,
    auto_save_results: List = None,
    auto_save_enabled: bool = False
) -> str:
    """格式化文生图响应
    
    Args:
        result: API响应结果
        prompt: 提示词
        size: 图片尺寸
        auto_save_results: 自动保存结果列表
        auto_save_enabled: 是否启用自动保存
        
    Returns:
        格式化的响应字符串
    """
    logger = get_logger(__name__)
    
    try:
        if not result.get("success"):
            return f"图像生成失败: {result.get('error', '未知错误')}"
        
        # 提取基本信息
        data = result.get("data", {})
        usage = result.get("usage", {})
        
        # 构建响应
        response_parts = []
        
        # 添加标题
        response_parts.append(f"文生图任务完成")
        response_parts.append(f"提示词: {prompt}")
        response_parts.append(f"尺寸: {size}")
        response_parts.append("")
        
        # 处理图片数据
        if isinstance(data, list):
            images = data
        elif isinstance(data, dict) and "data" in data:
            images = data["data"]
        else:
            images = [data]
        
        # 收集七牛云 URL 用于 Markdown 预览
        qiniu_urls = []
        for image in images:
            if isinstance(image, dict) and "markdown_ref" in image:
                # 从 markdown_ref 中提取 URL
                # markdown_ref 格式: ![图片](https://...)
                import re
                match = re.search(r'!\[.*?\]\((https://.*?)\)', image["markdown_ref"])
                if match:
                    qiniu_urls.append(match.group(1))

        # 如果有七牛云 URL,显示 Markdown 图片预览
        if qiniu_urls:
            response_parts.append("---")
            response_parts.append("")
            response_parts.append("**📸 图片预览:**")
            response_parts.append("")
            for i, url in enumerate(qiniu_urls, 1):
                response_parts.append(f"![图片{i}]({url})")
            response_parts.append("")
            response_parts.append("---")
            response_parts.append("")

        # 显示图片信息
        for i, image in enumerate(images, 1):
            if isinstance(image, dict):
                response_parts.append(f"**图片 {i}:**")

                # URL信息
                if "url" in image:
                    response_parts.append(f"- API URL: {image['url']}")

                # 本地路径信息（如果有自动保存）
                if "local_path" in image:
                    response_parts.append(f"- 本地路径: `{image['local_path']}`")

                # 七牛云链接（如果有）
                if "markdown_ref" in image:
                    import re
                    match = re.search(r'!\[.*?\]\((https://.*?)\)', image["markdown_ref"])
                    if match:
                        response_parts.append(f"- 七牛云链接: {match.group(1)}")

                # Base64信息
                if "b64_json" in image:
                    b64_data = image["b64_json"]
                    response_parts.append(f"- Base64数据: {len(b64_data)} 字符")

                response_parts.append("")
        
        # 显示自动保存信息
        if auto_save_enabled and auto_save_results:
            response_parts.append("自动保存信息:")
            successful_saves = sum(1 for r in auto_save_results if r.success)
            failed_saves = len(auto_save_results) - successful_saves
            
            response_parts.append(f"   总图片数: {len(auto_save_results)}")
            response_parts.append(f"   成功保存: {successful_saves}")
            if failed_saves > 0:
                response_parts.append(f"   保存失败: {failed_saves}")
            
            # 显示保存详情
            for i, save_result in enumerate(auto_save_results, 1):
                if save_result.success:
                    response_parts.append(f"   图片 {i}: 已保存到 {save_result.local_path}")
                else:
                    response_parts.append(f"   图片 {i}: 保存失败 - {save_result.error}")
            
            response_parts.append("")
        elif auto_save_enabled:
            response_parts.append("自动保存: 已启用但未保存图片")
            response_parts.append("")
        
        # 显示使用统计
        if usage:
            response_parts.append("使用统计:")
            if "prompt_tokens" in usage:
                response_parts.append(f"   提示词令牌: {usage['prompt_tokens']}")
            if "completion_tokens" in usage:
                response_parts.append(f"   完成令牌: {usage['completion_tokens']}")
            if "total_tokens" in usage:
                response_parts.append(f"   总令牌: {usage['total_tokens']}")
            if "cost" in usage:
                response_parts.append(f"   费用: {usage['cost']}")
            response_parts.append("")
        
        return "\n".join(response_parts)
        
    except Exception as e:
        logger.error(f"格式化响应失败: {e}")
        return f"格式化响应时发生错误: {str(e)}"