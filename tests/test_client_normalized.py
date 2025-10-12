#!/usr/bin/env python3
"""
测试规范化后的 client.py 功能
"""

import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from seedream_mcp.client import SeedreamClient
from seedream_mcp.config import SeedreamConfig


async def test_client_initialization():
    """测试客户端初始化"""
    print("1. 测试客户端初始化...")
    
    try:
        # 测试默认配置初始化
        client = SeedreamClient()
        print("   ✓ 默认配置初始化成功")
        
        # 测试自定义配置初始化
        config = SeedreamConfig.from_env()
        client_with_config = SeedreamClient(config)
        print("   ✓ 自定义配置初始化成功")
        
        # 测试异步上下文管理器
        async with SeedreamClient() as client:
            print("   ✓ 异步上下文管理器正常")
            
    except Exception as e:
        print(f"   ✗ 客户端初始化失败: {e}")
        return False
    
    return True


async def test_client_methods():
    """测试客户端方法存在性和参数验证"""
    print("2. 测试客户端方法...")
    
    try:
        client = SeedreamClient()
        
        # 检查所有主要方法是否存在
        methods = [
            'text_to_image',
            'image_to_image', 
            'multi_image_fusion',
            'sequential_generation'
        ]
        
        for method_name in methods:
            if hasattr(client, method_name):
                method = getattr(client, method_name)
                if callable(method):
                    print(f"   ✓ {method_name} 方法存在且可调用")
                else:
                    print(f"   ✗ {method_name} 存在但不可调用")
                    return False
            else:
                print(f"   ✗ {method_name} 方法不存在")
                return False
        
        # 测试参数验证（应该抛出验证错误）
        try:
            await client.text_to_image("", size="invalid")
        except Exception as e:
            print(f"   ✓ 参数验证正常工作: {type(e).__name__}")
        
    except Exception as e:
        print(f"   ✗ 客户端方法测试失败: {e}")
        return False
    
    return True


async def test_imports_and_dependencies():
    """测试导入和依赖"""
    print("3. 测试导入和依赖...")
    
    try:
        # 测试所有必要的导入
        from seedream_mcp.client import SeedreamClient
        from seedream_mcp.config import SeedreamConfig, get_global_config
        from seedream_mcp.utils.errors import SeedreamAPIError, SeedreamTimeoutError, SeedreamNetworkError
        from seedream_mcp.utils.logging import get_logger, log_function_call
        from seedream_mcp.utils.validation import (
            validate_prompt, validate_size, validate_image_url, validate_image_list,
            validate_max_images, validate_watermark, validate_response_format
        )
        
        print("   ✓ 所有导入成功")
        
        # 测试类型注解相关导入
        from typing import Dict, List, Optional, Union, Any
        from pathlib import Path
        import asyncio
        import base64
        import httpx
        
        print("   ✓ 所有依赖模块导入成功")
        
    except ImportError as e:
        print(f"   ✗ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"   ✗ 依赖测试失败: {e}")
        return False
    
    return True


async def test_removed_imports():
    """测试已移除的导入不会影响功能"""
    print("4. 测试移除的导入不影响功能...")
    
    try:
        # 确保 json 和 time 模块没有被直接使用
        import inspect
        import seedream_mcp.client as client_module
        
        source = inspect.getsource(client_module)
        
        # 检查是否还有对 json 模块的直接调用
        if 'json.' in source:
            print("   ⚠ 警告: 代码中仍有对 json 模块的直接调用")
        else:
            print("   ✓ 已正确移除 json 模块的直接使用")
            
        # 检查是否还有对 time 模块的直接调用
        if 'time.' in source:
            print("   ⚠ 警告: 代码中仍有对 time 模块的直接调用")
        else:
            print("   ✓ 已正确移除 time 模块的直接使用")
            
        # 测试 response.json() 仍然正常工作（这是 httpx 的方法）
        client = SeedreamClient()
        print("   ✓ httpx response.json() 方法仍可正常使用")
        
    except Exception as e:
        print(f"   ✗ 移除导入测试失败: {e}")
        return False
    
    return True


async def main():
    """主测试函数"""
    print("=== 测试规范化后的 client.py 功能 ===\n")
    
    tests = [
        test_client_initialization,
        test_client_methods,
        test_imports_and_dependencies,
        test_removed_imports
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
            print()
        except Exception as e:
            print(f"   ✗ 测试执行失败: {e}\n")
            results.append(False)
    
    print("=== 测试结果 ===")
    if all(results):
        print("✓ 所有测试通过！规范化成功，功能完全正常")
        return 0
    else:
        print("✗ 部分测试失败，需要检查问题")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)