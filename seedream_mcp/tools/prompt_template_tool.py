"""
Seedream 4.0 MCP工具 - 提示词模板工具

提供查看和管理提示词模板的功能。
"""

from typing import Any, Dict, List
from mcp.types import Tool, TextContent

from ..prompt_templates import get_available_templates, PROMPT_TEMPLATES
from ..utils.logging import get_logger


# 工具定义
prompt_template_tool = Tool(
    name="seedream_prompt_templates",
    description="查看所有可用的提示词模板。提示词模板可以帮助用户快速应用专业的设计风格，如公众号封面、小红书封面、产品海报等",
    inputSchema={
        "type": "object",
        "properties": {
            "show_details": {
                "type": "boolean",
                "description": "是否显示模板的详细内容",
                "default": False
            }
        }
    }
)


async def handle_prompt_templates(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理提示词模板查询请求
    
    Args:
        arguments: 工具参数
        
    Returns:
        MCP响应内容
    """
    logger = get_logger(__name__)
    
    try:
        show_details = arguments.get("show_details", False)
        
        logger.info(f"查询提示词模板, show_details={show_details}")
        
        if show_details:
            # 显示详细内容
            lines = ["📋 提示词模板详细信息\n"]
            
            for i, (name, config) in enumerate(PROMPT_TEMPLATES.items(), 1):
                lines.append(f"## {i}. {name}")
                lines.append(f"**描述:** {config['description']}")
                lines.append(f"**默认尺寸:** {config.get('default_size', '2K')}")
                lines.append(f"\n**模板内容:**")
                lines.append("```")
                lines.append(config['template'])
                lines.append("```")
                lines.append("")
            
            lines.append("---")
            lines.append("💡 **使用方法:**")
            lines.append('- "公众号封面，关键词：可口可乐"')
            lines.append('- "小红书封面 美食"')
            lines.append('- "产品海报，主题：iPhone"')
            
            result_text = "\n".join(lines)
        else:
            # 显示简要列表
            result_text = get_available_templates()
        
        return [TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        logger.error(f"查询提示词模板失败: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ 查询提示词模板失败: {str(e)}"
        )]

