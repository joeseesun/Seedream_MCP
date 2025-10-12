#!/usr/bin/env python3
"""
用户用例测试 - 验证原始问题是否已解决
测试用户提供的具体参数，确认不再出现 'NoneType' object is not callable 错误
"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from seedream_mcp.config import SeedreamConfig
from seedream_mcp.client import SeedreamClient


async def test_user_case():
    """测试用户的具体用例"""
    print("=== 用户用例测试 ===")
    print("测试参数:")
    print('  prompt: "一只可爱的小猫，毛茸茸的，大眼睛，可爱的表情，自然光线，高清细节"')
    print('  size: "2K"')
    print('  watermark: false')
    print()
    
    try:
        # 1. 配置加载
        print("1. 加载配置...")
        config = SeedreamConfig.from_env()
        print("   ✓ 配置加载成功")
        
        # 2. 创建客户端
        print("\n2. 创建客户端...")
        client = SeedreamClient(config)
        print("   ✓ 客户端创建成功")
        
        # 3. 测试用户的具体用例
        print("\n3. 执行文生图任务...")
        async with client:
            result = await client.text_to_image(
                prompt="一只可爱的小猫，毛茸茸的，大眼睛，可爱的表情，自然光线，高清细节",
                size="2K",
                watermark=False
            )
            
            if result.get('success') and result.get('data'):
                image_url = result['data'][0]['url']
                print("   ✅ 文生图成功！")
                print(f"   📸 图像URL: {image_url[:80]}...")
                print(f"   📊 图像尺寸: {result['data'][0].get('size', 'N/A')}")
                print(f"   💰 使用情况: {result.get('usage', {})}")
                print()
                print("🎉 用户原始问题已完全解决！")
                print("✅ 不再出现 'NoneType' object is not callable 错误")
                print("✅ API调用正常工作")
                print("✅ 返回有效的图像URL")
            else:
                print("   ❌ 文生图失败: 响应格式异常")
                print(f"   响应内容: {result}")
                
    except Exception as e:
        print(f"\n❌ 测试失败: {type(e).__name__}: {str(e)}")
        
        # 检查是否是原始的 NoneType 错误
        if "'NoneType' object is not callable" in str(e):
            print("⚠️  原始的 'NoneType' object is not callable 错误仍然存在！")
        else:
            print("ℹ️  这是一个不同的错误，原始问题可能已解决")
        
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_user_case())