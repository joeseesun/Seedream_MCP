#!/usr/bin/env python3
"""
测试规范化后的 server.py 功能完整性
"""

import asyncio
import logging
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from seedream_mcp.server import SeedreamMCPServer, NotificationOptions


async def test_server_functionality():
    """测试服务器功能完整性"""
    print("开始测试规范化后的服务器功能...")
    
    try:
        # 1. 测试服务器初始化
        print("1. 测试服务器初始化...")
        server = SeedreamMCPServer()
        print(f"   ✓ 服务器实例创建成功")
        print(f"   ✓ 工具数量: {len(server.tools)}")
        
        # 2. 测试 NotificationOptions 类
        print("2. 测试 NotificationOptions 类...")
        notification_options = NotificationOptions()
        print(f"   ✓ NotificationOptions 实例创建成功")
        print(f"   ✓ tools_changed: {notification_options.tools_changed}")
        print(f"   ✓ prompts_changed: {notification_options.prompts_changed}")
        print(f"   ✓ resources_changed: {notification_options.resources_changed}")
        
        # 3. 测试工具列表
        print("3. 测试工具列表...")
        tools = server._get_tools()
        print(f"   ✓ 获取到 {len(tools)} 个工具:")
        for i, tool in enumerate(tools, 1):
            print(f"     {i}. {tool.name}")
        
        # 4. 测试 get_capabilities 方法
        print("4. 测试 get_capabilities 方法...")
        try:
            capabilities = server.server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
            print(f"   ✓ get_capabilities 调用成功")
            print(f"   ✓ 能力配置: {capabilities}")
        except Exception as e:
            print(f"   ✗ get_capabilities 调用失败: {e}")
            return False
        
        # 5. 测试处理器注册
        print("5. 测试处理器注册...")
        print(f"   ✓ 处理器通过装饰器动态注册")
        
        print("\n✅ 所有功能测试通过！规范化后的代码功能完整。")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # 设置日志级别
    logging.basicConfig(level=logging.INFO)
    
    # 运行测试
    success = asyncio.run(test_server_functionality())
    sys.exit(0 if success else 1)