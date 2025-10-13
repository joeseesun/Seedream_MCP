"""
测试配置优先级逻辑

验证参数优先级：调用参数 > 客户端配置 > .env配置 > 方法默认值
"""

import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from seedream_mcp.config import SeedreamConfig
from seedream_mcp.tools.text_to_image import handle_text_to_image


class TestConfigPriority(unittest.TestCase):
    """测试配置优先级"""

    def setUp(self):
        """设置测试环境"""
        # 创建临时.env文件
        self.temp_env = tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False)
        self.temp_env.write("""
ARK_API_KEY=test_api_key
SEEDREAM_DEFAULT_SIZE=4K
SEEDREAM_DEFAULT_WATERMARK=false
""")
        self.temp_env.close()

    def tearDown(self):
        """清理测试环境"""
        os.unlink(self.temp_env.name)

    def test_parameter_priority_with_call_arguments(self):
        """测试调用参数优先级最高"""
        # 创建配置，默认值为2K和true
        config = SeedreamConfig(
            api_key="test_key",
            default_size="2K",
            default_watermark=True
        )
        
        # 模拟调用参数
        arguments = {
            "prompt": "test prompt",
            "size": "1K",  # 调用参数
            "watermark": False  # 调用参数
        }
        
        with patch('seedream_mcp.tools.text_to_image.get_global_config', return_value=config):
            with patch('seedream_mcp.tools.text_to_image.SeedreamClient') as mock_client:
                # 模拟客户端响应
                mock_instance = MagicMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.text_to_image.return_value = {
                    "data": [{"url": "http://example.com/image.jpg"}],
                    "usage": {"total_tokens": 100}
                }
                
                # 验证参数传递
                async def run_test():
                    await handle_text_to_image(arguments)
                    # 验证调用时使用的是调用参数，而不是配置默认值
                    mock_instance.text_to_image.assert_called_once()
                    call_args = mock_instance.text_to_image.call_args
                    self.assertEqual(call_args[1]['size'], "1K")  # 调用参数优先
                    self.assertEqual(call_args[1]['watermark'], False)  # 调用参数优先
                
                import asyncio
                asyncio.run(run_test())

    def test_parameter_priority_with_config_defaults(self):
        """测试配置默认值优先级"""
        # 创建配置，默认值为4K和false
        config = SeedreamConfig(
            api_key="test_key",
            default_size="4K",
            default_watermark=False
        )
        
        # 模拟调用参数（不包含size和watermark）
        arguments = {
            "prompt": "test prompt"
            # 没有size和watermark参数
        }
        
        with patch('seedream_mcp.tools.text_to_image.get_global_config', return_value=config):
            with patch('seedream_mcp.tools.text_to_image.SeedreamClient') as mock_client:
                # 模拟客户端响应
                mock_instance = MagicMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.text_to_image.return_value = {
                    "data": [{"url": "http://example.com/image.jpg"}],
                    "usage": {"total_tokens": 100}
                }
                
                # 验证参数传递
                async def run_test():
                    await handle_text_to_image(arguments)
                    # 验证调用时使用的是配置默认值
                    mock_instance.text_to_image.assert_called_once()
                    call_args = mock_instance.text_to_image.call_args
                    self.assertEqual(call_args[1]['size'], "4K")  # 配置默认值
                    self.assertEqual(call_args[1]['watermark'], False)  # 配置默认值
                
                import asyncio
                asyncio.run(run_test())

    def test_parameter_priority_mixed(self):
        """测试混合参数优先级"""
        # 创建配置
        config = SeedreamConfig(
            api_key="test_key",
            default_size="2K",
            default_watermark=True
        )
        
        # 模拟调用参数（只指定size，不指定watermark）
        arguments = {
            "prompt": "test prompt",
            "size": "1K"  # 只指定size
            # 没有watermark参数，应该使用配置默认值
        }
        
        with patch('seedream_mcp.tools.text_to_image.get_global_config', return_value=config):
            with patch('seedream_mcp.tools.text_to_image.SeedreamClient') as mock_client:
                # 模拟客户端响应
                mock_instance = MagicMock()
                mock_client.return_value.__aenter__.return_value = mock_instance
                mock_instance.text_to_image.return_value = {
                    "data": [{"url": "http://example.com/image.jpg"}],
                    "usage": {"total_tokens": 100}
                }
                
                # 验证参数传递
                async def run_test():
                    await handle_text_to_image(arguments)
                    # 验证调用时的参数优先级
                    mock_instance.text_to_image.assert_called_once()
                    call_args = mock_instance.text_to_image.call_args
                    self.assertEqual(call_args[1]['size'], "1K")  # 调用参数优先
                    self.assertEqual(call_args[1]['watermark'], True)  # 配置默认值
                
                import asyncio
                asyncio.run(run_test())

    def test_config_from_env_priority(self):
        """测试从环境变量加载配置的优先级"""
        with patch.dict(os.environ, {
            'ARK_API_KEY': 'test_key',
            'SEEDREAM_DEFAULT_SIZE': '4K',
            'SEEDREAM_DEFAULT_WATERMARK': 'false'
        }):
            config = SeedreamConfig.from_env()
            
            # 验证从环境变量加载的配置
            self.assertEqual(config.default_size, "4K")
            self.assertEqual(config.default_watermark, False)


if __name__ == '__main__':
    unittest.main()