#!/usr/bin/env python3
"""
Seedream 4.0 MCP工具 - 服务器模块

实现MCP协议服务器，处理工具调用请求。
"""

import asyncio
import logging
from typing import List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import SeedreamClient
from .config import SeedreamConfig
from .tools import (
    browse_images_tool,
    image_to_image_tool,
    multi_image_fusion_tool,
    sequential_generation_tool,
    text_to_image_tool,
    prompt_template_tool,
)
from .tools.browse_images import handle_browse_images
from .tools.image_to_image import handle_image_to_image
from .tools.multi_image_fusion import handle_multi_image_fusion
from .tools.sequential_generation import handle_sequential_generation
from .tools.text_to_image import handle_text_to_image
from .tools.prompt_template_tool import handle_prompt_templates
from .utils.errors import SeedreamMCPError
from .utils.logging import setup_logging


class NotificationOptions:
    """通知选项配置类"""

    def __init__(self):
        """初始化通知选项"""
        self.tools_changed = False
        self.prompts_changed = False
        self.resources_changed = False


class SeedreamMCPServer:
    """Seedream 4.0 MCP服务器类
    
    提供MCP协议服务器实现，负责处理工具调用请求，管理配置和客户端实例。
    """

    def __init__(self):
        """初始化MCP服务器实例
        
        创建Server实例，初始化配置、客户端和日志记录器，并注册协议处理器。
        """
        self.server = Server("seedream-mcp")
        self.config: Optional[SeedreamConfig] = None
        self.client: Optional[SeedreamClient] = None
        self.logger = logging.getLogger(__name__)
        self.tools = self._get_tools()
        self._register_handlers()

    def _get_tools(self) -> List[Tool]:
        """获取可用工具列表
        
        Returns:
            List[Tool]: 包含所有注册工具的列表
        """
        return [
            browse_images_tool,
            text_to_image_tool,
            image_to_image_tool,
            multi_image_fusion_tool,
            sequential_generation_tool,
            prompt_template_tool,
        ]

    def _register_handlers(self):
        """注册MCP协议处理器
        
        注册list_tools和call_tool处理器，用于响应工具列表查询和工具调用请求。
        """

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """列出所有可用工具
            
            Returns:
                list[Tool]: 工具列表
            """
            return self.tools

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list:
            """处理工具调用请求
            
            根据工具名称路由到对应处理器，执行工具调用并返回结果。
            
            Args:
                name: 工具名称
                arguments: 工具参数字典
            
            Returns:
                list: 包含工具执行结果的内容列表
            """
            try:
                if not self.config or not self.client:
                    await self._initialize_client()

                tool_name = name
                arguments = arguments or {}

                self.logger.info(f"调用工具: {tool_name}, 参数: {arguments}")

                # 路由到对应工具处理器
                # 传递server的client实例给tools，实现连接复用
                if tool_name == "seedream_browse_images":
                    content = await handle_browse_images(arguments)
                elif tool_name == "seedream_text_to_image":
                    content = await handle_text_to_image(arguments, client=self.client)
                elif tool_name == "seedream_image_to_image":
                    content = await handle_image_to_image(arguments, client=self.client)
                elif tool_name == "seedream_multi_image_fusion":
                    content = await handle_multi_image_fusion(arguments, client=self.client)
                elif tool_name == "seedream_sequential_generation":
                    content = await handle_sequential_generation(arguments, client=self.client)
                elif tool_name == "seedream_prompt_templates":
                    content = await handle_prompt_templates(arguments)
                else:
                    raise SeedreamMCPError(f"未知的工具: {tool_name}")

                # 验证返回内容格式
                self.logger.debug(f"工具返回的原始content: {content}, 类型: {type(content)}")

                if content is None:
                    self.logger.error("工具返回的content为None")
                    raise SeedreamMCPError("工具返回格式错误: content不能为None")

                if not isinstance(content, list):
                    self.logger.error(
                        f"工具返回的content不是列表类型: {type(content)}, 值: {content}"
                    )
                    raise SeedreamMCPError(f"工具返回格式错误: 期望列表，得到 {type(content)}")

                # 验证列表元素格式
                for i, item in enumerate(content):
                    if not hasattr(item, "type"):
                        self.logger.error(f"content[{i}]缺少type属性: {item}")
                        raise SeedreamMCPError(f"content[{i}]格式错误: 缺少type属性")

                    if not isinstance(item.type, str):
                        self.logger.error(
                            f"content[{i}]的type属性无效: {getattr(item, 'type', 'MISSING')}"
                        )
                        raise SeedreamMCPError(f"content[{i}]格式错误: type属性必须是字符串")

                self.logger.debug(f"工具返回的content验证通过，直接返回: {content}")

                return content

            except Exception as e:
                self.logger.error(f"工具调用失败: {e}", exc_info=True)
                return [TextContent(type="text", text=f"工具调用失败: {str(e)}")]

    async def _initialize_client(self):
        """初始化配置和客户端
        
        从环境变量加载配置，创建Seedream客户端实例。
        
        Raises:
            SeedreamMCPError: 客户端初始化失败时抛出
        """
        try:
            self.config = SeedreamConfig.from_env()
            self.client = SeedreamClient(self.config)
            self.logger.info("Seedream客户端初始化成功")
        except Exception as e:
            self.logger.error(f"客户端初始化失败: {e}")
            raise SeedreamMCPError(f"客户端初始化失败: {e}")

    async def run(self):
        """运行MCP服务器
        
        启动服务器，初始化日志和客户端，运行stdio服务器处理请求。
        
        Raises:
            Exception: 服务器运行过程中发生的异常
        """
        try:
            setup_logging()
            self.logger.info("启动Seedream MCP服务器...")

            await self._initialize_client()

            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="seedream-mcp",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        except KeyboardInterrupt:
            self.logger.info("收到中断信号，正在关闭服务器...")
        except Exception as e:
            self.logger.error(f"服务器运行错误: {e}", exc_info=True)
            raise


async def main():
    """主入口函数
    
    创建并运行SeedreamMCPServer实例。
    """
    server = SeedreamMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())
