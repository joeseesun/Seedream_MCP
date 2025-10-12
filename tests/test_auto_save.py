#!/usr/bin/env python3
"""
Seedream MCP 自动保存功能测试脚本

该脚本测试自动保存功能的各个组件，包括：
1. 配置加载测试
2. 文件管理器测试
3. 下载管理器测试
4. 自动保存管理器测试
5. 端到端集成测试
6. 错误处理测试

使用方法：
python test_auto_save.py
"""

import asyncio
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import hashlib
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from seedream_mcp.config import SeedreamConfig
    from seedream_mcp.utils.file_manager import FileManager
    from seedream_mcp.utils.download_manager import DownloadManager
    from seedream_mcp.utils.auto_save import AutoSaveManager, AutoSaveResult
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保在项目根目录运行此脚本")
    sys.exit(1)


class TestColors:
    """测试输出颜色定义"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_test_header(title: str):
    """打印测试标题"""
    print(f"\n{TestColors.BOLD}{TestColors.BLUE}{'='*60}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.BLUE}{title:^60}{TestColors.END}")
    print(f"{TestColors.BOLD}{TestColors.BLUE}{'='*60}{TestColors.END}")


def print_test_result(test_name: str, success: bool, details: str = ""):
    """打印测试结果"""
    status = f"{TestColors.GREEN}✅ 通过{TestColors.END}" if success else f"{TestColors.RED}❌ 失败{TestColors.END}"
    print(f"{status} {test_name}")
    if details:
        print(f"   {TestColors.CYAN}详情: {details}{TestColors.END}")


def print_info(message: str):
    """打印信息"""
    print(f"{TestColors.YELLOW}ℹ️  {message}{TestColors.END}")


def print_error(message: str):
    """打印错误"""
    print(f"{TestColors.RED}❌ {message}{TestColors.END}")


class AutoSaveTestSuite:
    """自动保存功能测试套件"""
    
    def __init__(self):
        self.temp_dir = None
        self.test_results = []
        
    async def setup(self):
        """测试环境设置"""
        print_info("设置测试环境...")
        self.temp_dir = tempfile.mkdtemp(prefix="seedream_test_")
        print_info(f"临时测试目录: {self.temp_dir}")
        
    async def teardown(self):
        """清理测试环境"""
        print_info("清理测试环境...")
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print_info("临时目录已清理")
    
    def record_result(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        self.test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })
        print_test_result(test_name, success, details)
    
    async def test_config_loading(self):
        """测试配置加载功能"""
        print_test_header("配置加载测试")
        
        try:
            # 测试默认配置（提供测试用的API密钥）
            config = SeedreamConfig(api_key="test_api_key_for_testing")
            
            # 验证自动保存相关配置
            auto_save_configs = [
                'auto_save_enabled',
                'auto_save_base_dir',
                'auto_save_download_timeout',
                'auto_save_max_retries',
                'auto_save_max_file_size',
                'auto_save_max_concurrent',
                'auto_save_date_folder',
                'auto_save_cleanup_days'
            ]
            
            missing_configs = []
            for config_name in auto_save_configs:
                if not hasattr(config, config_name):
                    missing_configs.append(config_name)
            
            if missing_configs:
                self.record_result(
                    "默认配置加载",
                    False,
                    f"缺少配置项: {', '.join(missing_configs)}"
                )
            else:
                self.record_result(
                    "默认配置加载",
                    True,
                    f"所有自动保存配置项存在"
                )
            
            # 测试配置值类型
            type_tests = [
                ('auto_save_enabled', bool),
                ('auto_save_base_dir', (str, type(None))),  # 可以是字符串或None
                ('auto_save_download_timeout', int),
                ('auto_save_max_retries', int),
                ('auto_save_max_file_size', int),
                ('auto_save_max_concurrent', int),
                ('auto_save_date_folder', bool),
                ('auto_save_cleanup_days', int)
            ]
            
            type_errors = []
            for config_name, expected_type in type_tests:
                if hasattr(config, config_name):
                    actual_value = getattr(config, config_name)
                    if not isinstance(actual_value, expected_type):
                        type_errors.append(f"{config_name}: 期望{expected_type.__name__}, 实际{type(actual_value).__name__}")
            
            if type_errors:
                self.record_result(
                    "配置类型验证",
                    False,
                    f"类型错误: {'; '.join(type_errors)}"
                )
            else:
                self.record_result(
                    "配置类型验证",
                    True,
                    "所有配置类型正确"
                )
            
            # 测试环境变量加载
            test_env = {
                'ARK_API_KEY': 'test_api_key_from_env',
                'SEEDREAM_AUTO_SAVE_ENABLED': 'false',
                'SEEDREAM_AUTO_SAVE_BASE_DIR': '/custom/path',
                'SEEDREAM_AUTO_SAVE_DOWNLOAD_TIMEOUT': '60'
            }
            
            with patch.dict(os.environ, test_env):
                env_config = SeedreamConfig.from_env()
                
                env_tests = [
                    (env_config.auto_save_enabled, False, "auto_save_enabled"),
                    (env_config.auto_save_base_dir, '/custom/path', "auto_save_base_dir"),
                    (env_config.auto_save_download_timeout, 60, "auto_save_download_timeout")
                ]
                
                env_errors = []
                for actual, expected, name in env_tests:
                    if actual != expected:
                        env_errors.append(f"{name}: 期望{expected}, 实际{actual}")
                
                if env_errors:
                    self.record_result(
                        "环境变量加载",
                        False,
                        f"环境变量错误: {'; '.join(env_errors)}"
                    )
                else:
                    self.record_result(
                        "环境变量加载",
                        True,
                        "环境变量正确加载"
                    )
                    
        except Exception as e:
            self.record_result("配置加载测试", False, f"异常: {str(e)}")
    
    async def test_file_manager(self):
        """测试文件管理器功能"""
        print_test_header("文件管理器测试")
        
        try:
            config = SeedreamConfig(api_key="test_api_key_for_testing")
            # 修复：FileManager 期望 Path 对象而不是配置对象
            base_dir = config.auto_save_base_dir or self.temp_dir
            file_manager = FileManager(Path(base_dir))
            
            # 测试文件名清理
            test_names = [
                "normal_name",
                "name with spaces",
                "name/with\\invalid:chars",
                "very_long_name_" + "x" * 200,
                ""
            ]
            
            for name in test_names:
                clean_name = file_manager.sanitize_filename(name)
                if clean_name and len(clean_name) <= 200:
                    self.record_result(
                        f"文件名清理: {name[:20]}...",
                        True,
                        f"清理后: {clean_name[:30]}..."
                    )
                else:
                    self.record_result(
                        f"文件名清理: {name[:20]}...",
                        False,
                        f"清理失败: {clean_name}"
                    )
            
            # 测试路径创建
            test_prompt = "测试提示词"
            test_url = "https://example.com/test.jpg"
            save_path = file_manager.create_save_path(test_prompt, test_url)
            
            if save_path and isinstance(save_path, Path):
                self.record_result(
                    "路径创建",
                    True,
                    f"成功创建路径: {save_path.name}"
                )
            else:
                self.record_result(
                    "路径创建",
                    False,
                    f"路径创建失败: {save_path}"
                )
                
        except Exception as e:
            self.record_result(
                "文件管理器测试",
                False,
                f"测试失败: {str(e)}"
            )
                
        except Exception as e:
            self.record_result(
                "文件管理器测试",
                False,
                f"测试失败: {str(e)}"
            )

    async def test_download_manager(self):
        """测试下载管理器功能"""
        print_test_header("下载管理器测试")
        
        try:
            config = SeedreamConfig(api_key="test_api_key_for_testing")
            # 修复：DownloadManager 不需要配置对象，使用配置参数
            download_manager = DownloadManager(
                timeout=config.auto_save_download_timeout,
                max_retries=config.auto_save_max_retries,
                max_file_size=config.auto_save_max_file_size
            )
            
            # 测试URL验证
            valid_urls = [
                "https://example.com/image.jpg",
                "http://test.com/photo.png",
                "https://cdn.example.com/images/test.webp"
            ]
            
            invalid_urls = [
                "not_a_url",
                "ftp://example.com/file.jpg",
                "",
                "javascript:alert('xss')"
            ]
            
            # 测试有效URL
            valid_count = 0
            for url in valid_urls:
                # 修复：使用正确的方法名 validate_url 而不是 is_valid_url
                if download_manager.validate_url(url):
                    valid_count += 1
            
            if valid_count == len(valid_urls):
                self.record_result(
                    "有效URL验证",
                    True,
                    f"所有{len(valid_urls)}个有效URL通过验证"
                )
            else:
                self.record_result(
                    "有效URL验证",
                    False,
                    f"只有{valid_count}/{len(valid_urls)}个有效URL通过验证"
                )
            
            # 测试无效URL
            invalid_count = 0
            for url in invalid_urls:
                # 修复：使用正确的方法名 validate_url 而不是 is_valid_url
                if not download_manager.validate_url(url):
                    invalid_count += 1
            
            if invalid_count == len(invalid_urls):
                self.record_result(
                    "无效URL验证",
                    True,
                    f"所有{len(invalid_urls)}个无效URL被正确拒绝"
                )
            else:
                self.record_result(
                    "无效URL验证",
                    False,
                    f"只有{invalid_count}/{len(invalid_urls)}个无效URL被拒绝"
                )

            # 测试模拟下载（不实际下载）
            test_url = "https://example.com/test_image.jpg"
            test_path = Path(self.temp_dir) / "test_download.jpg"
            
            # 模拟成功下载
            mock_response = Mock()
            mock_response.status = 200
            mock_response.headers = {'content-length': '1024'}
            
            async def mock_read():
                return b"fake_image_data"
            
            mock_response.read = mock_read
            
            with patch('aiohttp.ClientSession.get') as mock_get:
                mock_get.return_value.__aenter__.return_value = mock_response
                
                try:
                    result = await download_manager.download_image(test_url, test_path)
                    
                    if result:
                        self.record_result(
                            "模拟下载测试",
                            True,
                            f"下载成功: {test_path}"
                        )
                    else:
                        self.record_result(
                            "模拟下载测试",
                            False,
                            "下载返回False"
                        )
                except Exception as e:
                    self.record_result(
                        "模拟下载测试",
                        False,
                        f"下载异常: {str(e)}"
                    )
                    
        except Exception as e:
            self.record_result("下载管理器测试", False, f"异常: {str(e)}")
    
    async def test_auto_save_manager(self):
        """测试自动保存管理器功能"""
        print_test_header("自动保存管理器测试")
        
        try:
            config = SeedreamConfig(api_key="test_api_key_for_testing")
            # 修复：AutoSaveManager 构造函数参数
            auto_save_manager = AutoSaveManager(
                base_dir=Path(config.auto_save_base_dir) if config.auto_save_base_dir else None,
                download_timeout=config.auto_save_download_timeout,
                max_retries=config.auto_save_max_retries,
                max_file_size=config.auto_save_max_file_size,
                max_concurrent=config.auto_save_max_concurrent
            )
            
            # 测试单图保存（模拟）
            test_url = 'https://example.com/test.jpg'
            test_prompt = '测试图像'
            test_custom_name = 'test_image'
            
            # 模拟下载成功
            mock_download_result = {
                'file_size': 1024,
                'download_time': 1.5,
                'content_type': 'image/jpeg',
                'attempts': 1
            }
            
            with patch.object(auto_save_manager.download_manager, 'download_image', return_value=mock_download_result):
                result = await auto_save_manager.save_image(
                    url=test_url,
                    prompt=test_prompt,
                    custom_name=test_custom_name
                )
                
                if isinstance(result, AutoSaveResult) and result.success:
                    self.record_result(
                        "单图保存测试",
                        True,
                        f"保存成功: {result.local_path}"
                    )
                else:
                    self.record_result(
                        "单图保存测试",
                        False,
                        f"保存失败: {result.error if hasattr(result, 'error') else '未知错误'}"
                    )
            
            # 测试多图保存
            test_images_data = [
                {
                    'url': 'https://example.com/test1.jpg',
                    'prompt': '测试图像1',
                    'custom_name': 'test_image_1'
                },
                {
                    'url': 'https://example.com/test2.jpg',
                    'prompt': '测试图像2',
                    'custom_name': 'test_image_2'
                }
            ]
            
            with patch.object(auto_save_manager.download_manager, 'download_image', return_value=mock_download_result):
                results = await auto_save_manager.save_multiple_images(
                    test_images_data,
                    'text_to_image'
                )
                
                success_count = sum(1 for r in results if r.success)
                
                if success_count == len(test_images_data):
                    self.record_result(
                        "多图保存测试",
                        True,
                        f"成功保存{success_count}张图片"
                    )
                else:
                    self.record_result(
                        "多图保存测试",
                        False,
                        f"只成功保存{success_count}/{len(test_images_data)}张图片"
                    )
            
            # 测试错误处理
            with patch.object(auto_save_manager.download_manager, 'download_image', side_effect=Exception("模拟下载错误")):
                error_result = await auto_save_manager.save_image(
                    url=test_url,
                    prompt=test_prompt
                )
                
                if isinstance(error_result, AutoSaveResult) and not error_result.success:
                    self.record_result(
                        "错误处理测试",
                        True,
                        f"正确处理错误: {error_result.error}"
                    )
                else:
                    self.record_result(
                        "错误处理测试",
                        False,
                        "错误处理不正确"
                    )
                     
        except Exception as e:
            self.record_result("自动保存管理器测试", False, f"异常: {str(e)}")

    async def test_integration(self):
        """测试端到端集成功能"""
        print_test_header("端到端集成测试")
        
        try:
            # 模拟完整的文生图流程
            config = SeedreamConfig(api_key="test_api_key_for_testing")
            
            # 模拟API响应
            mock_api_response = {
                'success': True,
                'data': {
                    'images': [
                        {
                            'url': 'https://example.com/generated_image_1.jpg',
                            'size': '2K'
                        }
                    ]
                }
            }
            
            # 模拟文生图工具的处理流程
            prompt = "星际穿越，黑洞，复古列车，电影大片风格"
            size = "2K"
            auto_save = True
            
            # 创建自动保存管理器
            auto_save_manager = AutoSaveManager(
                base_dir=Path(self.temp_dir),
                download_timeout=config.auto_save_download_timeout,
                max_retries=config.auto_save_max_retries,
                max_file_size=config.auto_save_max_file_size,
                max_concurrent=config.auto_save_max_concurrent
            )
            
            # 准备图像数据
            image_url = mock_api_response['data']['images'][0]['url']
            
            # 模拟保存过程
            mock_download_result = {
                'file_size': 2048,
                'download_time': 2.0,
                'content_type': 'image/jpeg',
                'attempts': 1
            }
            
            with patch.object(auto_save_manager.download_manager, 'download_image', return_value=mock_download_result):
                save_result = await auto_save_manager.save_image(
                    url=image_url,
                    prompt=prompt
                )
                
                # 构建完整响应
                response = {
                    'success': True,
                    'image_url': image_url,
                    'size': size,
                    'prompt': prompt
                }
                
                if save_result.success:
                    response.update({
                        'local_path': str(save_result.local_path),
                        'markdown_ref': save_result.markdown_ref,
                        'auto_save_success': True
                    })
                else:
                    response.update({
                        'auto_save_success': False,
                        'auto_save_error': save_result.error
                    })
                
                # 验证响应完整性
                required_fields = ['success', 'image_url', 'size', 'prompt']
                if save_result.success:
                    required_fields.extend(['local_path', 'markdown_ref'])
                
                missing_fields = [field for field in required_fields if field not in response]
                
                if not missing_fields:
                    self.record_result(
                        "端到端集成测试",
                        True,
                        f"完整流程成功，本地路径: {response.get('local_path', 'N/A')}"
                    )
                else:
                    self.record_result(
                        "端到端集成测试",
                        False,
                        f"缺少字段: {', '.join(missing_fields)}"
                    )
                     
        except Exception as e:
            self.record_result("端到端集成测试", False, f"异常: {str(e)}")

    async def test_error_handling(self):
        """测试错误处理场景"""
        print_test_header("错误处理测试")
        
        try:
            config = SeedreamConfig(api_key="test_api_key_for_testing")
            
            # 测试无效路径处理
            try:
                # 修复：使用无效路径测试
                invalid_path = Path("/invalid/path/that/does/not/exist")
                auto_save_manager = AutoSaveManager(
                    base_dir=invalid_path,
                    download_timeout=config.auto_save_download_timeout,
                    max_retries=config.auto_save_max_retries,
                    max_file_size=config.auto_save_max_file_size,
                    max_concurrent=config.auto_save_max_concurrent
                )
                
                test_data = {
                    'url': 'https://example.com/test.jpg',
                    'prompt': '测试'
                }
                
                result = await auto_save_manager.save_image(
                    url=test_data['url'],
                    prompt=test_data['prompt']
                )
                
                if not result.success:
                    self.record_result(
                        "无效路径处理",
                        True,
                        f"正确处理无效路径: {result.error}"
                    )
                else:
                    self.record_result(
                        "无效路径处理",
                        False,
                        "应该失败但却成功了"
                    )
            except Exception as e:
                self.record_result(
                    "无效路径处理",
                    True,
                    f"正确抛出异常: {str(e)[:50]}..."
                )
            
            # 测试网络错误处理
            auto_save_manager = AutoSaveManager(
                base_dir=Path(self.temp_dir),
                download_timeout=config.auto_save_download_timeout,
                max_retries=1  # 减少重试次数以加快测试
            )
            
            # 测试无效URL下载
            invalid_url = "https://invalid-domain-that-does-not-exist.com/image.jpg"
            
            try:
                result = await auto_save_manager.save_image(
                    url=invalid_url,
                    prompt="测试"
                )
                
                if not result.success:
                    self.record_result(
                        "网络错误处理",
                        True,
                        f"正确处理网络错误: {result.error[:50]}..."
                    )
                else:
                    self.record_result(
                        "网络错误处理",
                        False,
                        "应该失败但却成功了"
                    )
            except Exception as e:
                self.record_result(
                    "网络错误处理",
                    True,
                    f"正确处理网络错误: {str(e)[:50]}..."
                )
                
        except Exception as e:
            self.record_result("错误处理测试", False, f"测试异常: {str(e)}")

    def print_summary(self):
        """打印测试总结"""
        print_test_header("测试总结")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        print(f"{TestColors.BOLD}总测试数: {total_tests}{TestColors.END}")
        print(f"{TestColors.GREEN}通过: {passed_tests}{TestColors.END}")
        print(f"{TestColors.RED}失败: {failed_tests}{TestColors.END}")
        print(f"{TestColors.CYAN}成功率: {(passed_tests/total_tests*100):.1f}%{TestColors.END}")
        
        if failed_tests > 0:
            print(f"\n{TestColors.RED}失败的测试:{TestColors.END}")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print(f"\n{TestColors.BOLD}测试完成！{TestColors.END}")
        
        return failed_tests == 0


async def main():
    """主测试函数"""
    print_test_header("Seedream MCP 自动保存功能测试")
    print_info("开始运行自动保存功能测试套件...")
    
    test_suite = AutoSaveTestSuite()
    
    try:
        # 设置测试环境
        await test_suite.setup()
        
        # 运行所有测试
        await test_suite.test_config_loading()
        await test_suite.test_file_manager()
        await test_suite.test_download_manager()
        await test_suite.test_auto_save_manager()
        await test_suite.test_integration()
        await test_suite.test_error_handling()
        
        # 打印总结
        success = test_suite.print_summary()
        
        return 0 if success else 1
        
    except Exception as e:
        print_error(f"测试运行失败: {str(e)}")
        return 1
    
    finally:
        # 清理测试环境
        await test_suite.teardown()


if __name__ == "__main__":
    # 运行测试
    exit_code = asyncio.run(main())
    sys.exit(exit_code)