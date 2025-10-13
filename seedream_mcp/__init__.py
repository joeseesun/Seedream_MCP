"""
Seedream 4.0 MCP工具包

基于火山引擎Seedream 4.0 API的模型上下文协议（MCP）工具，
为开发者提供在IDE中直接调用AI图像生成功能的能力。

支持功能：
- 文生图：根据文本描述生成图像
- 图生图：基于参考图像和文本生成新图像  
- 多图融合：融合多张参考图特征生成图像
- 组图生成：生成一组关联图像

"""

__version__ = "1.0.0"
__author__ = "Seedream MCP Team"
__email__ = "tengmmvp@qq.com"

from .config import SeedreamConfig
from .client import SeedreamClient
from .server import SeedreamMCPServer

__all__ = [
    "SeedreamConfig",
    "SeedreamClient", 
    "SeedreamMCPServer",
]