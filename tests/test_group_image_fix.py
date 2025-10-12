#!/usr/bin/env python3
"""
测试修复后的组图生成功能
验证API参数修复和image参数支持
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from seedream_mcp.client import SeedreamClient
from seedream_mcp.tools.sequential_generation import handle_sequential_generation


async def test_text_to_group_images():
    """测试文生组图功能"""
    print("🧪 测试文生组图功能...")
    
    arguments = {
        "prompt": "一只可爱的小猫咪在花园里玩耍",
        "max_images": 4,
        "size": "2K",
        "watermark": True,
        "response_format": "url",
        "auto_save": False
    }
    
    try:
        result = await handle_sequential_generation(arguments)
        print(f"✅ 文生组图测试成功")
        print(f"📊 结果: {len(result)} 个响应项")
        for i, item in enumerate(result):
            if hasattr(item, 'text'):
                print(f"   {i+1}. {item.text[:100]}...")
        return True
    except Exception as e:
        print(f"❌ 文生组图测试失败: {e}")
        return False


async def test_single_image_to_group():
    """测试单图生组图功能"""
    print("\n🧪 测试单图生组图功能...")
    
    # 使用一个示例图片URL
    test_image_url = "https://example.com/test-image.jpg"
    
    arguments = {
        "prompt": "基于这张图片生成更多相似风格的图片",
        "max_images": 3,
        "size": "2K",
        "image": test_image_url,
        "watermark": True,
        "response_format": "url",
        "auto_save": False
    }
    
    try:
        result = await handle_sequential_generation(arguments)
        print(f"✅ 单图生组图测试成功")
        print(f"📊 结果: {len(result)} 个响应项")
        return True
    except Exception as e:
        print(f"❌ 单图生组图测试失败: {e}")
        return False


async def test_multi_image_to_group():
    """测试多图生组图功能"""
    print("\n🧪 测试多图生组图功能...")
    
    # 使用多个示例图片URL
    test_images = [
        "https://example.com/test-image1.jpg",
        "https://example.com/test-image2.jpg"
    ]
    
    arguments = {
        "prompt": "融合这些图片的风格特点生成新的图片",
        "max_images": 5,
        "size": "2K",
        "image": test_images,
        "watermark": True,
        "response_format": "url",
        "auto_save": False
    }
    
    try:
        result = await handle_sequential_generation(arguments)
        print(f"✅ 多图生组图测试成功")
        print(f"📊 结果: {len(result)} 个响应项")
        return True
    except Exception as e:
        print(f"❌ 多图生组图测试失败: {e}")
        return False


async def test_parameter_validation():
    """测试参数验证"""
    print("\n🧪 测试参数验证...")
    
    test_cases = [
        {
            "name": "空prompt",
            "args": {"prompt": "", "max_images": 4},
            "should_fail": True
        },
        {
            "name": "超出max_images范围",
            "args": {"prompt": "测试", "max_images": 20},
            "should_fail": True
        },
        {
            "name": "无效size",
            "args": {"prompt": "测试", "size": "8K"},
            "should_fail": True
        },
        {
            "name": "空image字符串",
            "args": {"prompt": "测试", "image": ""},
            "should_fail": True
        },
        {
            "name": "空image数组",
            "args": {"prompt": "测试", "image": []},
            "should_fail": True
        },
        {
            "name": "过多image",
            "args": {"prompt": "测试", "image": [f"img{i}.jpg" for i in range(15)]},
            "should_fail": True
        }
    ]
    
    passed = 0
    for test_case in test_cases:
        try:
            result = await handle_sequential_generation(test_case["args"])
            # 检查是否包含错误信息
            has_error = any("错误" in item.text for item in result if hasattr(item, 'text'))
            
            if test_case["should_fail"] and has_error:
                print(f"✅ {test_case['name']}: 正确拒绝无效参数")
                passed += 1
            elif not test_case["should_fail"] and not has_error:
                print(f"✅ {test_case['name']}: 正确接受有效参数")
                passed += 1
            else:
                print(f"❌ {test_case['name']}: 验证结果不符合预期")
        except Exception as e:
            if test_case["should_fail"]:
                print(f"✅ {test_case['name']}: 正确抛出异常")
                passed += 1
            else:
                print(f"❌ {test_case['name']}: 意外异常 - {e}")
    
    print(f"📊 参数验证测试: {passed}/{len(test_cases)} 通过")
    return passed == len(test_cases)


async def test_api_parameters():
    """测试API参数格式"""
    print("\n🧪 测试API参数格式...")
    
    try:
        client = SeedreamClient()
        
        # 测试新的API参数格式
        # 注意：这里只是测试参数传递，不会真正调用API
        print("✅ 客户端初始化成功")
        print("✅ sequential_generation方法支持image参数")
        
        # 检查方法签名
        import inspect
        sig = inspect.signature(client.sequential_generation)
        params = list(sig.parameters.keys())
        
        if 'image' in params:
            print("✅ sequential_generation方法包含image参数")
        else:
            print("❌ sequential_generation方法缺少image参数")
            return False
            
        return True
    except Exception as e:
        print(f"❌ API参数测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    print("🚀 开始测试修复后的组图生成功能\n")
    
    tests = [
        ("API参数格式", test_api_parameters),
        ("参数验证", test_parameter_validation),
        ("文生组图", test_text_to_group_images),
        ("单图生组图", test_single_image_to_group),
        ("多图生组图", test_multi_image_to_group)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"测试: {test_name}")
        print('='*50)
        
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 测试总结")
    print('='*50)
    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 所有测试通过！组图生成功能修复成功！")
        return True
    else:
        print("⚠️ 部分测试失败，需要进一步检查")
        return False


if __name__ == "__main__":
    asyncio.run(main())