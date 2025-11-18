#!/usr/bin/env python3
"""
Seedream 4.0 MCP工具 - 图片格式演示

演示三种不同的响应格式：image、url、b64_json
"""

import asyncio
import os
from pathlib import Path

from seedream_mcp import SeedreamClient, SeedreamConfig
from seedream_mcp.utils.errors import SeedreamMCPError


async def demo_image_format():
    """演示 image 格式 - 直接显示图片"""
    print("🖼️ 演示 image 格式（推荐）")
    print("-" * 60)
    
    config = SeedreamConfig.from_env()
    
    try:
        async with SeedreamClient(config) as client:
            result = await client.text_to_image(
                prompt="一只可爱的小猫咪，卡通风格",
                size="2K",
                watermark=False,
                response_format="url"  # 注意：客户端层面仍使用 url
            )
            
            print(f"✅ 生成成功！")
            print(f"说明：image 格式会自动下载图片并转换为 MCP ImageContent")
            print(f"在支持的 MCP 客户端中可以直接预览图片")
            
            if result.get("success") and result.get("data"):
                data = result["data"]
                if isinstance(data, list) and len(data) > 0:
                    print(f"\n图片 URL: {data[0].get('url', 'N/A')}")
            
    except SeedreamMCPError as e:
        print(f"❌ 生成失败: {e}")


async def demo_url_format():
    """演示 url 格式 - 返回 URL 链接"""
    print("\n\n📝 演示 url 格式")
    print("-" * 60)
    
    config = SeedreamConfig.from_env()
    
    try:
        async with SeedreamClient(config) as client:
            result = await client.text_to_image(
                prompt="一只可爱的小猫咪，卡通风格",
                size="2K",
                watermark=False,
                response_format="url"
            )
            
            print(f"✅ 生成成功！")
            print(f"说明：url 格式返回图片 URL，需要手动打开查看")
            print(f"注意：URL 在 24 小时后会过期")
            
            if result.get("success") and result.get("data"):
                data = result["data"]
                if isinstance(data, list) and len(data) > 0:
                    print(f"\n图片 URL: {data[0].get('url', 'N/A')}")
            
    except SeedreamMCPError as e:
        print(f"❌ 生成失败: {e}")


async def demo_b64_format():
    """演示 b64_json 格式 - 返回 base64 编码"""
    print("\n\n🔤 演示 b64_json 格式")
    print("-" * 60)
    
    config = SeedreamConfig.from_env()
    
    try:
        async with SeedreamClient(config) as client:
            result = await client.text_to_image(
                prompt="一只可爱的小猫咪，卡通风格",
                size="2K",
                watermark=False,
                response_format="b64_json"
            )
            
            print(f"✅ 生成成功！")
            print(f"说明：b64_json 格式返回 base64 编码的图片数据")
            print(f"适合程序处理，但数据量较大")
            
            if result.get("success") and result.get("data"):
                data = result["data"]
                if isinstance(data, list) and len(data) > 0:
                    b64_data = data[0].get('b64_json', '')
                    print(f"\nBase64 数据长度: {len(b64_data)} 字符")
                    print(f"Base64 数据预览: {b64_data[:100]}...")
            
    except SeedreamMCPError as e:
        print(f"❌ 生成失败: {e}")


async def main():
    """主函数"""
    print("=" * 60)
    print("Seedream 4.0 MCP 工具 - 图片格式演示")
    print("=" * 60)
    
    # 演示三种格式
    await demo_image_format()
    await demo_url_format()
    await demo_b64_format()
    
    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)
    print("\n推荐使用 image 格式以获得最佳体验")
    print("在 MCP 工具调用中，设置 response_format='image' 即可")


if __name__ == "__main__":
    asyncio.run(main())

