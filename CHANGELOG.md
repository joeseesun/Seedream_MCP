# 更新日志

本文档记录了 Seedream 4.0 MCP 工具的所有重要更改。

## [1.1.1] - 2025-10-12

### 修复问题

- 🔧 **功能优化**: 移除不支持的状态查询功能，简化工具集
- 📚 **文档更新**: 更新所有文档以反映 Seedream 4.0 API 的实际能力
- ⚠️ **用户体验改进**: 移除可能导致混淆的功能，专注于核心图像生成能力
- 🧪 **测试完善**: 更新测试用例以匹配当前支持的功能

### 技术改进

- 移除了不支持的状态查询相关代码
- 简化 API 客户端，专注于同步图像生成操作
- 改进错误处理机制，提供更友好的用户提示
- 更新所有相关文档以反映 API 的实际能力

## [1.1.0] - 2025-10-12

### 新增功能

- 🎉 **自动保存功能**: 解决生成图片 URL 在 24 小时后过期的问题
- 💾 **本地存储**: 自动将生成的图片下载并保存到本地文件系统
- 📝 **Markdown 支持**: 自动生成 Markdown 格式的图片引用，便于文档编写
- 🗂️ **智能文件管理**: 按日期和工具类型自动组织文件目录结构
- 🔄 **并发下载**: 支持多图片并发下载，提高处理效率
- ⚙️ **灵活配置**: 提供丰富的环境变量配置选项
- 🛡️ **错误恢复**: 下载失败时提供重试机制和备选方案

### 技术细节

- 新增 8 个自动保存相关的环境变量配置
- 所有图像生成工具新增`auto_save`、`save_path`、`custom_name`参数
- 实现智能文件命名规则，包含时间戳和内容哈希
- 添加文件大小限制和并发控制机制
- 支持自动清理过期文件功能

### 配置新增

- `SEEDREAM_AUTO_SAVE_ENABLED`: 全局启用自动保存
- `SEEDREAM_AUTO_SAVE_BASE_DIR`: 保存基础目录
- `SEEDREAM_AUTO_SAVE_DOWNLOAD_TIMEOUT`: 下载超时时间
- `SEEDREAM_AUTO_SAVE_MAX_RETRIES`: 最大重试次数
- `SEEDREAM_AUTO_SAVE_MAX_FILE_SIZE`: 最大文件大小限制
- `SEEDREAM_AUTO_SAVE_MAX_CONCURRENT`: 最大并发下载数
- `SEEDREAM_AUTO_SAVE_DATE_FOLDER`: 是否创建日期文件夹
- `SEEDREAM_AUTO_SAVE_CLEANUP_DAYS`: 自动清理天数

### 文档更新

- 📖 更新 README.md，添加自动保存功能详细说明
- 🔧 更新 API.md，为所有工具添加自动保存参数文档
- 💡 更新 USAGE.md，提供自动保存功能使用示例
- ⚙️ 更新配置文件示例，包含所有新的环境变量

## [1.0.0] - 2025-10-11

### 初始功能

- 🎉 初始版本发布
- 🎨 实现文生图工具 (`seedream_text_to_image`)
- 🖼️ 实现图生图工具 (`seedream_image_to_image`)
- 🎭 实现多图融合工具 (`seedream_multi_image_fusion`)
- 📚 实现组图生成工具 (`seedream_sequential_generation`)

- 🔧 完整的 MCP 协议支持
- ⚙️ 灵活的配置管理系统
- 📝 详细的日志记录功能
- 🛡️ 完善的错误处理机制
- 🧪 全面的测试覆盖

### 技术特性

- 支持 Python 3.8+
- 基于火山引擎 Seedream 4.0 API
- 异步 HTTP 客户端（httpx）
- 环境变量配置支持
- 自动重试机制
- 参数验证和类型检查
- 结构化日志输出

### 工具功能

#### seedream_text_to_image

- 支持文本到图像生成
- 可配置图像尺寸（1K/2K/4K）
- 可选水印功能
- 多种响应格式（URL/Base64）

#### seedream_image_to_image

- 基于参考图像的图像编辑
- 支持风格转换
- 保持原图结构的同时应用新风格

#### seedream_multi_image_fusion

- 多图像特征融合
- 支持 2-5 张图像输入
- 智能特征提取和融合

#### seedream_sequential_generation

- 生成关联图像序列
- 支持 1-10 张图像生成
- 适用于故事板、品牌 VI 等场景

### 配置选项

- `ARK_API_KEY`: API 密钥（必需）
- `ARK_BASE_URL`: API 基础 URL
- `SEEDREAM_MODEL_ID`: 模型标识
- `SEEDREAM_DEFAULT_SIZE`: 默认图像尺寸
- `SEEDREAM_DEFAULT_WATERMARK`: 默认水印设置
- `SEEDREAM_TIMEOUT`: 请求超时时间
- `SEEDREAM_API_TIMEOUT`: API 超时时间
- `SEEDREAM_MAX_RETRIES`: 最大重试次数
- `LOG_LEVEL`: 日志级别
- `LOG_FILE`: 日志文件路径

### 文档和示例

- 📖 完整的 README 文档
- 🔧 配置示例文件（.env.example）
- 💡 基础使用示例（basic_usage.py）
- 🖥️ MCP 服务器示例（mcp_server_example.py）
- 🧪 集成测试套件
- ✅ 安装验证脚本

### 项目结构

```text
Seedream_MCP/
├── seedream_mcp/           # 核心代码
│   ├── __init__.py
│   ├── client.py           # API客户端
│   ├── config.py           # 配置管理
│   ├── server.py           # MCP服务器
│   ├── tools/              # 工具实现
│   │   ├── __init__.py
│   │   ├── text_to_image.py
│   │   ├── image_to_image.py
│   │   ├── multi_image_fusion.py
│   │   ├── sequential_generation.py

│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── errors.py       # 错误定义
│       ├── logging.py      # 日志工具
│       └── validation.py   # 参数验证
├── tests/                  # 测试文件
│   └── test_mcp_integration.py
├── examples/               # 使用示例
│   ├── basic_usage.py
│   └── mcp_server_example.py
├── .env.example           # 环境变量示例
├── requirements.txt       # 依赖列表
├── setup.py              # 安装脚本
├── verify_installation.py # 验证脚本
├── README.md             # 说明文档
└── CHANGELOG.md          # 更新日志
```

### 测试覆盖

- ✅ 服务器初始化测试
- ✅ 工具注册验证
- ✅ Schema 结构验证
- ✅ 各工具功能测试
- ✅ 配置管理测试
- ✅ 错误处理测试
- ✅ 集成测试套件

### 已知限制

- 需要有效的火山引擎 API 密钥
- 图像生成受 API 配额限制
- 大尺寸图像生成可能需要较长时间
- 网络连接质量影响 API 调用性能

### 下一步计划

- 添加更多图像处理选项
- 支持批量操作
- 增加缓存机制
- 优化性能和内存使用
- 添加更多示例和教程

---

## 版本说明

版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目！

### 提交 Issue

- 使用清晰的标题描述问题
- 提供详细的重现步骤
- 包含错误日志和环境信息

### 提交 Pull Request

- Fork 项目并创建功能分支
- 确保代码通过所有测试
- 添加必要的测试用例
- 更新相关文档
