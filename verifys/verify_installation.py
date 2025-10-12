#!/usr/bin/env python3
"""
Seedream 4.0 MCP工具安装验证脚本

本脚本用于验证Seedream 4.0 MCP工具的安装和配置是否正确。
运行此脚本可以快速检查所有依赖项、配置文件和核心功能。

使用方法:
    python verify_installation.py
"""

import sys
import os
import importlib
from pathlib import Path
from typing import List


class InstallationVerifier:
    """安装验证器"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    def print_header(self):
        """打印标题"""
        print("🔍 Seedream 4.0 MCP工具安装验证")
        print("=" * 50)
        print()
    
    def check_python_version(self) -> bool:
        """检查Python版本"""
        print("📋 检查Python版本...")
        
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            self.errors.append(f"Python版本过低: {version.major}.{version.minor}, 需要3.8+")
            print(f"❌ Python {version.major}.{version.minor}.{version.micro} (需要3.8+)")
            return False
        else:
            print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
            return True
    
    def check_required_packages(self) -> bool:
        """检查必需的包"""
        print("\n📋 检查必需的包...")
        
        required_packages = [
            'mcp',
            'httpx',
            'loguru',
            'pydantic',
            'python-dotenv'
        ]
        
        all_installed = True
        
        for package in required_packages:
            try:
                # 特殊处理某些包的导入名称
                if package == 'python-dotenv':
                    importlib.import_module('dotenv')
                else:
                    importlib.import_module(package.replace('-', '_'))
                print(f"✅ {package}")
            except ImportError:
                self.errors.append(f"缺少必需包: {package}")
                print(f"❌ {package}")
                all_installed = False
        
        return all_installed
    
    def check_project_structure(self) -> bool:
        """检查项目结构"""
        print("\n📋 检查项目结构...")
        
        required_files = [
            'seedream_mcp/__init__.py',
            'seedream_mcp/server.py',
            'seedream_mcp/client.py',
            'seedream_mcp/config.py',
            'seedream_mcp/tools/__init__.py',
            'seedream_mcp/tools/text_to_image.py',
            'seedream_mcp/tools/image_to_image.py',
            'seedream_mcp/tools/multi_image_fusion.py',
            'seedream_mcp/tools/sequential_generation.py',
            'seedream_mcp/utils/__init__.py',
            'seedream_mcp/utils/errors.py',
            'seedream_mcp/utils/logging.py',
            'seedream_mcp/utils/validation.py',
            'main.py',
            'setup.py',
            'README.md',
            '.env.example'
        ]
        
        all_exist = True
        
        for file_path in required_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                print(f"✅ {file_path}")
            else:
                self.errors.append(f"缺少文件: {file_path}")
                print(f"❌ {file_path}")
                all_exist = False
        
        return all_exist
    
    def check_environment_config(self) -> bool:
        """检查环境配置"""
        print("\n📋 检查环境配置...")
        
        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'
        
        if not env_example.exists():
            self.errors.append("缺少.env.example文件")
            print("❌ .env.example文件")
            return False
        else:
            print("✅ .env.example文件")
        
        if not env_file.exists():
            self.warnings.append("未找到.env文件，请复制.env.example并配置")
            print("⚠️  .env文件 (请复制.env.example并配置)")
            return True
        else:
            print("✅ .env文件")
        
        # 检查环境变量
        required_env_vars = [
            'ARK_API_KEY',
            'ARK_BASE_URL',
            'SEEDREAM_MODEL_ID'
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.warnings.append(f"缺少环境变量: {', '.join(missing_vars)}")
            print(f"⚠️  环境变量: 缺少 {', '.join(missing_vars)}")
        else:
            print("✅ 环境变量配置完整")
        
        return True
    
    def check_imports(self) -> bool:
        """检查模块导入"""
        print("\n📋 检查模块导入...")
        
        # 添加项目根目录到Python路径
        sys.path.insert(0, str(self.project_root))
        
        modules_to_test = [
            ('seedream_mcp', 'seedream_mcp'),
            ('seedream_mcp.config', 'SeedreamConfig'),
            ('seedream_mcp.client', 'SeedreamClient'),
            ('seedream_mcp.server', 'SeedreamMCPServer'),
            ('seedream_mcp.utils.errors', 'SeedreamMCPError'),
            ('seedream_mcp.utils.logging', 'setup_logging'),
            ('seedream_mcp.utils.validation', 'validate_prompt'),
        ]
        
        all_imported = True
        
        for module_name, class_name in modules_to_test:
            try:
                module = importlib.import_module(module_name)
                if hasattr(module, class_name):
                    print(f"✅ {module_name}.{class_name}")
                else:
                    self.errors.append(f"模块 {module_name} 中缺少 {class_name}")
                    print(f"❌ {module_name}.{class_name}")
                    all_imported = False
            except ImportError as e:
                self.errors.append(f"无法导入模块 {module_name}: {e}")
                print(f"❌ {module_name}: {e}")
                all_imported = False
        
        return all_imported
    
    def check_tools_registration(self) -> bool:
        """检查工具注册"""
        print("\n📋 检查工具注册...")
        
        try:
            # 设置测试环境变量
            os.environ.setdefault('ARK_API_KEY', 'test_key')
            os.environ.setdefault('ARK_BASE_URL', 'https://ark.cn-beijing.volces.com/api/v3')
            os.environ.setdefault('SEEDREAM_MODEL_ID', 'seedream-4.0')
            
            from seedream_mcp.server import SeedreamMCPServer
            
            server = SeedreamMCPServer()
            
            expected_tools = [
                'seedream_text_to_image',
                'seedream_image_to_image',
                'seedream_multi_image_fusion',
                'seedream_sequential_generation'
            ]
            
            registered_tools = [tool.name for tool in server.tools]
            
            all_registered = True
            for tool_name in expected_tools:
                if tool_name in registered_tools:
                    print(f"✅ {tool_name}")
                else:
                    self.errors.append(f"工具未注册: {tool_name}")
                    print(f"❌ {tool_name}")
                    all_registered = False
            
            return all_registered
            
        except Exception as e:
            self.errors.append(f"工具注册检查失败: {e}")
            print(f"❌ 工具注册检查失败: {e}")
            return False
    
    def check_documentation(self) -> bool:
        """检查文档"""
        print("\n📋 检查文档...")
        
        doc_files = [
            'README.md',
            'docs/USAGE.md',
            'docs/API.md',
            'docs/cursor_config.json'
        ]
        
        all_exist = True
        
        for doc_file in doc_files:
            full_path = self.project_root / doc_file
            if full_path.exists():
                print(f"✅ {doc_file}")
            else:
                self.warnings.append(f"缺少文档: {doc_file}")
                print(f"⚠️  {doc_file}")
                # 文档缺失不算错误，只是警告
        
        return True
    
    def print_summary(self):
        """打印总结"""
        print("\n" + "=" * 50)
        print("📊 验证结果汇总")
        
        if not self.errors and not self.warnings:
            print("🎉 所有检查通过！安装完成且配置正确。")
            print("\n📝 下一步:")
            print("1. 配置.env文件中的API密钥")
            print("2. 在Cursor中配置MCP服务器")
            print("3. 开始使用Seedream 4.0 MCP工具")
            
        elif not self.errors:
            print("✅ 基本安装正确，但有一些警告需要注意。")
            print("\n⚠️  警告:")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        else:
            print("❌ 发现错误，需要修复后才能正常使用。")
            print("\n🔧 需要修复的错误:")
            for error in self.errors:
                print(f"   • {error}")
            
            if self.warnings:
                print("\n⚠️  警告:")
                for warning in self.warnings:
                    print(f"   • {warning}")
    
    def run_verification(self) -> bool:
        """运行完整验证"""
        self.print_header()
        
        checks = [
            self.check_python_version,
            self.check_required_packages,
            self.check_project_structure,
            self.check_environment_config,
            self.check_imports,
            self.check_tools_registration,
            self.check_documentation
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.errors.append(f"验证过程中发生异常: {e}")
                print(f"❌ 验证异常: {e}")
        
        self.print_summary()
        
        return len(self.errors) == 0


def main():
    """主函数"""
    verifier = InstallationVerifier()
    success = verifier.run_verification()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())