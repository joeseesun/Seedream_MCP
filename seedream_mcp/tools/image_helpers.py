"""
Seedream 4.0 MCP工具 - 图片处理辅助函数

提供图片下载、转换等通用功能。
"""

from typing import Any, Dict, List, Union
import base64
import httpx
from mcp.types import TextContent, ImageContent

from ..utils.logging import get_logger


async def create_image_content_response(
    result: Dict[str, Any],
    prompt: str,
    size: str,
    extra_info: str = ""
) -> List[Union[TextContent, ImageContent]]:
    """创建包含图片的响应

    Args:
        result: API响应结果
        prompt: 提示词
        size: 图片尺寸
        extra_info: 额外信息（可选）

    Returns:
        包含文本和图片的响应列表
    """
    logger = get_logger(__name__)

    try:
        data = result.get("data", [])
        if not data:
            return [TextContent(type="text", text="未生成图片")]

        # 添加文本说明
        text_parts = [
            "✅ 图片生成成功！",
            f"提示词: {prompt}",
            f"尺寸: {size}"
        ]
        if extra_info:
            text_parts.append(extra_info)

        # 如果有本地保存路径,上传到七牛云并生成 Markdown
        local_paths = []
        qiniu_urls = []

        if data and isinstance(data, list) and isinstance(data[0], dict) and "local_path" in data[0]:
            from pathlib import Path
            from ..utils.qiniu_uploader import get_qiniu_uploader

            # 获取七牛云上传器
            uploader = get_qiniu_uploader()

            for i, image_info in enumerate(data, 1):
                if isinstance(image_info, dict) and "local_path" in image_info:
                    local_path = image_info["local_path"]
                    abs_path = Path(local_path).absolute()
                    local_paths.append(abs_path)

                    # 尝试上传到七牛云
                    if uploader.enabled:
                        qiniu_url = uploader.upload_file(str(abs_path))
                        if qiniu_url:
                            qiniu_urls.append(qiniu_url)
                            logger.info(f"图片 {i} 上传成功: {qiniu_url}")
                        else:
                            logger.warning(f"图片 {i} 上传失败")

        # 添加 Markdown 图片显示
        text_parts.append("")  # 空行
        text_parts.append("---")
        text_parts.append("")  # 空行
        if qiniu_urls:
            # 使用七牛云 URL 的 Markdown（公网可访问，客户端可以直接显示）
            text_parts.append("**📸 图片预览:**")
            text_parts.append("")  # 空行
            for i, url in enumerate(qiniu_urls, 1):
                text_parts.append(f"![图片{i}]({url})")
                text_parts.append("")  # 空行

        # 添加详细信息
        text_parts.append("---")
        text_parts.append("")  # 空行
        text_parts.append("**📋 详细信息:**")
        text_parts.append("")  # 空行

        # 七牛云 URL (放在前面,更显眼)
        if qiniu_urls:
            text_parts.append("**☁️  七牛云链接:**")
            for i, url in enumerate(qiniu_urls, 1):
                text_parts.append(f"- 图片 {i}: {url}")
            text_parts.append("")  # 空行

        # 本地保存路径
        if local_paths:
            text_parts.append("**💾 本地保存:**")
            for i, path in enumerate(local_paths, 1):
                text_parts.append(f"- 图片 {i}: `{path}`")

        if not qiniu_urls:
            text_parts.append("")  # 空行
            text_parts.append("💡 提示: 配置七牛云后可自动上传并生成公网访问链接")

        # 只返回 TextContent (Raycast AI 支持 Markdown 渲染)
        return [TextContent(
            type="text",
            text="\n".join(text_parts)
        )]

    except Exception as e:
        logger.error(f"创建图片响应失败: {e}")
        return [TextContent(type="text", text=f"创建图片响应失败: {str(e)}")]


async def download_image_as_base64(url: str, timeout: int = 30) -> str:
    """下载图片并转换为 base64
    
    Args:
        url: 图片 URL
        timeout: 超时时间（秒）
        
    Returns:
        base64 编码的图片数据
        
    Raises:
        Exception: 下载或转换失败时抛出
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=timeout)
        response.raise_for_status()
        image_bytes = response.content
        return base64.b64encode(image_bytes).decode('utf-8')

