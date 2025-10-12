#!/usr/bin/env python3
"""
详细测试API参数格式和图片生成数量
"""

import asyncio
import sys
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from seedream_mcp.client import SeedreamClient
from seedream_mcp.tools.sequential_generation import handle_sequential_generation


async def test_api_parameters_format():
    """测试API参数格式是否正确"""
    print("🧪 测试API参数格式...")
    
    # 模拟API响应
    mock_response = {
        "model": "doubao-seedream-4-0-250828",
        "created": 1760260000,
        "data": [
            {"url": f"https://example.com/image{i}.jpg"} 
            for i in range(1, 5)  # 4张图片
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 0,
            "total_tokens": 10
        }
    }
    
    captured_request_data = {}
    
    async def mock_call_api(self, endpoint, data):
        """捕获API调用参数"""
        nonlocal captured_request_data
        captured_request_data = data.copy()
        return mock_response
    
    # 使用mock来捕获API调用参数
    with patch.object(SeedreamClient, '_call_api', mock_call_api):
        client = SeedreamClient()
        
        # 测试文生组图
        await client.sequential_generation(
            prompt="测试提示词",
            max_images=4,
            size="2K",
            watermark=True,
            response_format="url"
        )
    
    # 验证API参数格式
    print(f"📋 捕获的API请求参数:")
    print(json.dumps(captured_request_data, indent=2, ensure_ascii=False))
    
    # 检查关键参数
    checks = []
    
    # 检查是否使用了正确的参数名
    if "sequential_image_generation" in captured_request_data:
        if captured_request_data["sequential_image_generation"] == "auto":
            checks.append("✅ sequential_image_generation 参数正确")
        else:
            checks.append("❌ sequential_image_generation 值不正确")
    else:
        checks.append("❌ 缺少 sequential_image_generation 参数")
    
    if "sequential_image_generation_options" in captured_request_data:
        options = captured_request_data["sequential_image_generation_options"]
        if isinstance(options, dict) and "max_images" in options:
            if options["max_images"] == 4:
                checks.append("✅ sequential_image_generation_options.max_images 正确")
            else:
                checks.append("❌ sequential_image_generation_options.max_images 值不正确")
        else:
            checks.append("❌ sequential_image_generation_options 格式不正确")
    else:
        checks.append("❌ 缺少 sequential_image_generation_options 参数")
    
    # 检查是否移除了旧的 "n" 参数
    if "n" not in captured_request_data:
        checks.append("✅ 已移除旧的 'n' 参数")
    else:
        checks.append("❌ 仍然包含旧的 'n' 参数")
    
    # 检查其他必要参数
    if captured_request_data.get("prompt") == "测试提示词":
        checks.append("✅ prompt 参数正确")
    else:
        checks.append("❌ prompt 参数不正确")
    
    if captured_request_data.get("size") == "2K":
        checks.append("✅ size 参数正确")
    else:
        checks.append("❌ size 参数不正确")
    
    print("\n📊 API参数检查结果:")
    for check in checks:
        print(f"   {check}")
    
    success_count = sum(1 for check in checks if check.startswith("✅"))
    total_count = len(checks)
    
    print(f"\n📈 API参数验证: {success_count}/{total_count} 通过")
    return success_count == total_count


async def main():
    """主测试函数"""
    print("🚀 开始详细测试API参数格式\n")
    
    tests = [
        ("API参数格式", test_api_parameters_format)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"{'='*60}")
        print(f"测试: {test_name}")
        print('='*60)
        
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} 测试通过")
            else:
                print(f"❌ {test_name} 测试失败")
        except Exception as e:
            print(f"❌ {test_name} 测试异常: {e}")
    
    print(f"\n{'='*60}")
    print(f"📊 详细测试总结")
    print('='*60)
    print(f"总测试数: {total}")
    print(f"通过数: {passed}")
    print(f"失败数: {total - passed}")
    print(f"成功率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("🎉 API参数格式测试通过！")
        return True
    else:
        print("⚠️ API参数格式测试失败")
        return False


if __name__ == "__main__":
    asyncio.run(main())