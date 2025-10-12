#!/usr/bin/env python3
"""
Seedream 4.0 MCP服务器使用示例

本示例展示如何启动和使用Seedream MCP服务器。
"""

import asyncio
import json
from typing import Dict, Any

from seedream_mcp.server import SeedreamMCPServer
from seedream_mcp.config import SeedreamConfig


class MCPServerExample:
    """MCP服务器示例类"""
    
    def __init__(self):
        self.server = None
    
    async def setup_server(self):
        """设置MCP服务器"""
        print("🔧 初始化MCP服务器...")
        
        # 创建服务器实例
        self.server = SeedreamMCPServer()
        
        # 初始化客户端
        await self.server._initialize_client()
        
        print("✅ MCP服务器初始化完成")
        return self.server
    
    async def list_available_tools(self):
        """列出可用工具"""
        print("\n📋 可用工具列表:")
        print("-" * 40)
        
        for i, tool in enumerate(self.server.tools, 1):
            print(f"{i}. {tool.name}")
            print(f"   描述: {tool.description}")
            print(f"   参数: {list(tool.inputSchema.get('properties', {}).keys())}")
            print()
    
    async def simulate_tool_call(self, tool_name: str, arguments: Dict[str, Any]):
        """模拟工具调用"""
        print(f"\n🔧 模拟调用工具: {tool_name}")
        print(f"参数: {json.dumps(arguments, ensure_ascii=False, indent=2)}")
        print("-" * 40)
        
        try:
            # 创建模拟请求
            class MockRequest:
                def __init__(self, name: str, args: Dict[str, Any]):
                    self.params = MockParams(name, args)
            
            class MockParams:
                def __init__(self, name: str, args: Dict[str, Any]):
                    self.name = name
                    self.arguments = args
            
            request = MockRequest(tool_name, arguments)
            
            # 调用工具处理器
            result = await self.server._handle_tool_call(request)
            
            print(f"✅ 调用成功!")
            print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
        except Exception as e:
            print(f"❌ 调用失败: {e}")
    
    async def run_examples(self):
        """运行示例"""
        print("🚀 Seedream MCP服务器示例")
        print("=" * 60)
        
        # 设置服务器
        await self.setup_server()
        
        # 列出工具
        await self.list_available_tools()
        
        # 示例1: 文生图
        await self.simulate_tool_call(
            "seedream_text_to_image",
            {
                "prompt": "一只可爱的小猫咪，卡通风格",
                "size": "2K",
                "watermark": True,
                "response_format": "url"
            }
        )
        
        # 示例2: 图生图
        await self.simulate_tool_call(
            "seedream_image_to_image",
            {
                "prompt": "将这张图片转换为油画风格",
                "image": "https://example.com/test.jpg",
                "size": "2K",
                "watermark": False
            }
        )
        
        # 示例3: 多图融合
        await self.simulate_tool_call(
            "seedream_multi_image_fusion",
            {
                "prompt": "将这些图片融合成一个艺术作品",
                "images": [
                    "https://example.com/image1.jpg",
                    "https://example.com/image2.jpg",
                    "https://example.com/image3.jpg"
                ],
                "size": "4K"
            }
        )
        
        # 示例4: 组图生成
        await self.simulate_tool_call(
            "seedream_sequential_generation",
            {
                "prompt": "科幻城市景观，未来主义风格",
                "max_images": 3,
                "size": "2K"
            }
        )
        
        print("\n🎉 所有示例执行完成！")


async def run_as_stdio_server():
    """作为标准输入输出服务器运行"""
    print("🚀 启动Seedream MCP标准输入输出服务器...")
    print("服务器将通过标准输入输出与客户端通信")
    print("按 Ctrl+C 停止服务器")
    print("-" * 60)
    
    try:
        # 创建服务器
        mcp_server = SeedreamMCPServer()
        
        # 运行服务器
        await mcp_server.run()
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器运行错误: {e}")


async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        # 作为服务器运行
        await run_as_stdio_server()
    else:
        # 运行示例
        example = MCPServerExample()
        await example.run_examples()


if __name__ == "__main__":
    asyncio.run(main())