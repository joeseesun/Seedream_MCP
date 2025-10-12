#!/usr/bin/env python3
"""验证服务器修复脚本"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from seedream_mcp.server import SeedreamMCPServer
import json

print('🔧 验证修复后的工具定义:')
print('='*60)

# 创建服务器实例
server = SeedreamMCPServer()
tools = server._get_tools()

# 查找sequential_generation工具
seq_tool = None
for tool in tools:
    if tool.name == 'seedream_sequential_generation':
        seq_tool = tool
        break

if seq_tool:
    print('✅ 找到sequential_generation工具')
    schema = seq_tool.inputSchema
    properties = schema.get('properties', {})
    
    print('\n📋 关键参数检查:')
    print('-' * 40)
    
    # 检查image参数
    if 'image' in properties:
        image_prop = properties['image']
        print('✅ image参数存在')
        print(f'   类型: {image_prop.get("type")}')
        print(f'   描述: {image_prop.get("description", "")}')
        if 'maxItems' in image_prop:
            print(f'   最大项目数: {image_prop["maxItems"]}')
    else:
        print('❌ image参数不存在')
    
    # 检查max_images参数
    if 'max_images' in properties:
        max_images_prop = properties['max_images']
        print('✅ max_images参数存在')
        print(f'   最小值: {max_images_prop.get("minimum")}')
        print(f'   最大值: {max_images_prop.get("maximum")}')
        print(f'   默认值: {max_images_prop.get("default")}')
    else:
        print('❌ max_images参数不存在')
    
    # 检查size参数
    if 'size' in properties:
        size_prop = properties['size']
        print('✅ size参数存在')
        print(f'   可选值: {size_prop.get("enum")}')
        print(f'   默认值: {size_prop.get("default")}')
    else:
        print('❌ size参数不存在')
    
    print('\n🎯 修复验证结果:')
    print('-' * 40)
    
    # 验证修复
    has_image = 'image' in properties
    max_val = properties.get('max_images', {}).get('maximum', 0)
    default_val = properties.get('max_images', {}).get('default', 0)
    
    print(f'参数名称: {"image" if has_image else "images (旧)"}')
    print(f'max_images最大值: {max_val} (应为15)')
    print(f'max_images默认值: {default_val} (应为4)')
    
    if has_image and max_val == 15 and default_val == 4:
        print('\n🎉 修复成功！工具定义已正确更新')
        print('现在重启MCP服务器后，客户端应该会看到正确的工具定义')
    else:
        print('\n⚠️ 修复未完全生效，请检查导入')
        
    print('\n📄 完整工具定义:')
    print('-' * 40)
    print(json.dumps(schema, indent=2, ensure_ascii=False))
        
else:
    print('❌ 未找到sequential_generation工具')

print('\n🔍 所有工具列表:')
print('-' * 40)
for i, tool in enumerate(tools, 1):
    print(f'{i}. {tool.name}: {tool.description}')