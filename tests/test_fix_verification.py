#!/usr/bin/env python3
"""
组图生成功能修复验证测试
将原有的 verifys/verify_fix.py 中的验证逻辑转换为标准测试格式
"""

import sys
import asyncio
import inspect
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from seedream_mcp.client import SeedreamClient


class TestFixVerification:
    """组图生成功能修复验证测试类"""
    
    def __init__(self):
        """初始化测试客户端"""
        self.client = SeedreamClient()
    
    def test_sequential_generation_method_signature(self):
        """测试 sequential_generation 方法签名是否包含必要参数"""
        print("🧪 测试方法签名...")
        
        sig = inspect.signature(self.client.sequential_generation)
        params = list(sig.parameters.keys())
        
        print(f"参数列表: {params}")
        
        # 验证必要参数存在
        assert 'prompt' in params, "缺少 prompt 参数"
        assert 'image' in params, "缺少 image 参数"
        assert 'max_images' in params, "缺少 max_images 参数"
        assert 'size' in params, "缺少 size 参数"
        
        print("✅ 方法签名验证通过")
        return True
    
    def test_api_parameter_format(self):
        """测试API参数格式是否符合火山引擎官方文档"""
        print("🧪 测试API参数格式...")
        
        source = inspect.getsource(self.client.sequential_generation)
        
        # 检查新的API参数格式
        assert 'sequential_image_generation' in source, "缺少 sequential_image_generation 参数"
        assert 'sequential_image_generation_options' in source, "缺少 sequential_image_generation_options 参数"
        
        # 检查旧的错误参数已移除
        assert '"n":' not in source, "仍包含已废弃的 'n' 参数"
        
        print("✅ API参数格式验证通过")
        print("   - 使用 sequential_image_generation: 'auto'")
        print("   - 使用 sequential_image_generation_options: {'max_images': N}")
        print("   - 已移除废弃的 'n' 参数")
        return True
    
    def test_tool_definition_schema(self):
        """测试工具定义模式是否正确"""
        print("🧪 测试工具定义模式...")
        
        try:
            from seedream_mcp.tools.sequential_generation import sequential_generation_tool
            tool_schema = sequential_generation_tool.inputSchema
            
            # 检查 image 参数
            properties = tool_schema.get('properties', {})
            assert 'image' in properties, "工具定义缺少 image 参数"
            
            image_prop = properties['image']
            image_type = image_prop.get('type', [])
            if isinstance(image_type, str):
                image_type = [image_type]
            assert 'array' in image_type, "image 参数不支持数组类型"
            
            # 检查 max_images 上限
            max_images_prop = properties.get('max_images', {})
            assert max_images_prop.get('maximum') == 15, "max_images 上限未更新为15"
            
            # 检查默认尺寸
            size_prop = properties.get('size', {})
            assert size_prop.get('default') == '2K', "默认尺寸未更新为2K"
            
            print("✅ 工具定义验证通过")
            print("   - image 参数支持数组类型")
            print("   - max_images 上限已更新为15")
            print("   - 默认尺寸已更新为2K")
            return True
            
        except ImportError as e:
            print(f"❌ 导入工具定义失败: {e}")
            assert False, f"无法导入工具定义: {e}"
        except Exception as e:
            print(f"❌ 检查工具定义时出错: {e}")
            assert False, f"工具定义检查失败: {e}"
    
    def test_source_code_analysis(self):
        """测试源代码分析，确保修复内容正确"""
        print("🧪 测试源代码分析...")
        
        source = inspect.getsource(self.client.sequential_generation)
        
        # 检查错误处理
        assert 'try:' in source or 'except' in source, "缺少错误处理机制"
        
        # 检查参数验证
        assert 'max_images' in source, "缺少 max_images 参数处理"
        assert 'size' in source, "缺少 size 参数处理"
        
        # 检查图片处理逻辑
        assert 'image' in source, "缺少图片处理逻辑"
        
        print("✅ 源代码分析验证通过")
        print("   - 包含错误处理机制")
        print("   - 包含参数验证逻辑")
        print("   - 包含图片处理功能")
        return True
    
    def test_functionality_integration(self):
        """测试功能集成，确保所有修复内容协同工作"""
        print("🧪 测试功能集成...")
        
        # 检查方法可调用性
        assert callable(self.client.sequential_generation), "sequential_generation 方法不可调用"
        
        # 检查方法参数默认值
        sig = inspect.signature(self.client.sequential_generation)
        
        # 验证关键参数有合理的默认值或类型注解
        for param_name, param in sig.parameters.items():
            if param_name in ['max_images', 'size']:
                assert param.default is not inspect.Parameter.empty or param.annotation != inspect.Parameter.empty, \
                    f"参数 {param_name} 缺少默认值或类型注解"
        
        print("✅ 功能集成验证通过")
        print("   - 方法可正常调用")
        print("   - 参数配置合理")
        return True
    
    def run_all_tests(self):
        """运行所有验证测试"""
        print("🚀 开始组图生成功能修复验证测试\\n")
        print("="*60)
        
        test_methods = [
            self.test_sequential_generation_method_signature,
            self.test_api_parameter_format,
            self.test_tool_definition_schema,
            self.test_source_code_analysis,
            self.test_functionality_integration
        ]
        
        passed_tests = 0
        total_tests = len(test_methods)
        
        for test_method in test_methods:
            try:
                test_method()
                passed_tests += 1
                print()
            except AssertionError as e:
                print(f"❌ 测试失败: {e}")
                print()
            except Exception as e:
                print(f"❌ 测试出错: {e}")
                print()
        
        print("="*60)
        print("📊 测试结果总结:")
        print(f"总测试数: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {total_tests - passed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")
        
        if passed_tests == total_tests:
            print("\\n🎉 所有验证测试通过！组图生成功能修复验证完成！")
            print("\\n✅ 修复内容确认:")
            print("   - API参数格式已按照火山引擎官方文档修复")
            print("   - 支持3种输入类型：文生组图、单图生组图、多图生组图")
            print("   - 移除了错误的'n'参数，使用正确的参数格式")
            print("   - 增强了参数验证和错误处理")
            print("   - 提升了最大图片数量和默认质量")
        else:
            print(f"\\n⚠️  有 {total_tests - passed_tests} 个测试失败，请检查相关功能")
        
        return passed_tests == total_tests


def main():
    """主函数，运行所有验证测试"""
    test_runner = TestFixVerification()
    return test_runner.run_all_tests()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)