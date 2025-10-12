#!/usr/bin/env python3
"""
Seedream 4.0 MCP工具基础使用示例

本示例展示如何使用Seedream MCP工具进行各种图像生成操作。
"""

import asyncio
import os
from pathlib import Path

from seedream_mcp import SeedreamClient, SeedreamConfig
from seedream_mcp.utils.errors import SeedreamMCPError


async def example_text_to_image():
    """文生图示例"""
    print("🎨 文生图示例")
    print("-" * 40)
    
    config = SeedreamConfig.from_env()
    client = SeedreamClient(config)
    
    try:
        # 基础文生图
        result = await client.text_to_image(
            prompt="一只可爱的小猫咪，卡通风格，高质量",
            size="2K",
            watermark=True,
            response_format="url"
        )
        
        print(f"✅ 生成成功！")
        print(f"图像URL: {result.get('image_url', 'N/A')}")
        print(f"任务ID: {result.get('task_id', 'N/A')}")
        
    except SeedreamMCPError as e:
        print(f"❌ 生成失败: {e}")
    finally:
        await client.close()


async def example_image_to_image():
    """图生图示例"""
    print("\n🖼️ 图生图示例")
    print("-" * 40)
    
    config = SeedreamConfig.from_env()
    client = SeedreamClient(config)
    
    try:
        # 假设有一张参考图像
        image_path = "https://example.com/reference.jpg"  # 替换为实际图像URL
        
        result = await client.image_to_image(
            prompt="将这张图片转换为油画风格，增加艺术感",
            image=image_path,
            size="2K",
            watermark=False
        )
        
        print(f"✅ 转换成功！")
        print(f"图像URL: {result.get('image_url', 'N/A')}")
        print(f"任务ID: {result.get('task_id', 'N/A')}")
        
    except SeedreamMCPError as e:
        print(f"❌ 转换失败: {e}")
    finally:
        await client.close()


async def example_multi_image_fusion():
    """多图融合示例"""
    print("\n🎭 多图融合示例")
    print("-" * 40)
    
    config = SeedreamConfig.from_env()
    client = SeedreamClient(config)
    
    try:
        # 多张参考图像
        images = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.jpg",
            "https://example.com/image3.jpg"
        ]
        
        result = await client.multi_image_fusion(
            prompt="将这些图片融合成一个梦幻的艺术作品，保持和谐的色彩搭配",
            images=images,
            size="4K"
        )
        
        print(f"✅ 融合成功！")
        print(f"图像URL: {result.get('image_url', 'N/A')}")
        print(f"任务ID: {result.get('task_id', 'N/A')}")
        
    except SeedreamMCPError as e:
        print(f"❌ 融合失败: {e}")
    finally:
        await client.close()


async def example_sequential_generation():
    """组图生成示例"""
    print("\n📚 组图生成示例")
    print("-" * 40)
    
    config = SeedreamConfig.from_env()
    client = SeedreamClient(config)
    
    try:
        result = await client.sequential_generation(
            prompt="科幻城市景观系列：未来主义建筑、飞行汽车、霓虹灯光",
            max_images=4,
            size="2K"
        )
        
        print(f"✅ 生成成功！")
        print(f"生成图像数量: {len(result.get('images', []))}")
        
        for i, image_info in enumerate(result.get('images', []), 1):
            print(f"  图像 {i}: {image_info.get('url', 'N/A')}")
        
        print(f"任务ID: {result.get('task_id', 'N/A')}")
        
    except SeedreamMCPError as e:
        print(f"❌ 生成失败: {e}")
    finally:
        await client.close()


async def example_error_handling():
    """错误处理示例"""
    print("\n⚠️ 错误处理示例")
    print("-" * 40)
    
    # 使用无效配置
    config = SeedreamConfig(
        api_key="invalid_key",
        base_url="https://invalid-url.com"
    )
    client = SeedreamClient(config)
    
    try:
        result = await client.text_to_image(
            prompt="测试错误处理",
            size="2K"
        )
        print("这行不应该被执行")
        
    except SeedreamMCPError as e:
        print(f"✅ 成功捕获错误: {e}")
        print(f"错误类型: {type(e).__name__}")
        
    finally:
        await client.close()


async def example_configuration():
    """配置管理示例"""
    print("\n🔧 配置管理示例")
    print("-" * 40)
    
    # 从环境变量加载配置
    config = SeedreamConfig.from_env()
    print(f"API密钥: {config.api_key[:10]}..." if config.api_key else "未设置")
    print(f"基础URL: {config.base_url}")
    print(f"模型ID: {config.model_id}")
    print(f"默认尺寸: {config.default_size}")
    print(f"默认水印: {config.default_watermark}")
    print(f"超时时间: {config.timeout}秒")
    print(f"最大重试: {config.max_retries}次")
    print(f"日志级别: {config.log_level}")
    
    # 验证配置
    try:
        config.validate()
        print("✅ 配置验证通过")
    except ValueError as e:
        print(f"❌ 配置验证失败: {e}")


async def main():
    """主函数"""
    print("🚀 Seedream 4.0 MCP工具使用示例")
    print("=" * 60)
    
    # 检查环境变量
    if not os.getenv('ARK_API_KEY'):
        print("⚠️ 警告：未设置ARK_API_KEY环境变量")
        print("请创建.env文件并设置API密钥，或者设置环境变量")
        print("示例：ARK_API_KEY=your_api_key_here")
        return
    
    # 运行示例
    examples = [
        example_configuration,
        example_text_to_image,
        example_image_to_image,
        example_multi_image_fusion,
        example_sequential_generation,
        example_error_handling
    ]
    
    for example in examples:
        try:
            await example()
        except Exception as e:
            print(f"❌ 示例执行失败: {e}")
        
        # 添加分隔符
        print()
    
    print("🎉 所有示例执行完成！")


if __name__ == "__main__":
    asyncio.run(main())