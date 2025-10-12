# Seedream 4.0 MCP 工具使用指南

## 概述

Seedream 4.0 MCP 工具是一个符合 MCP（Model Context Protocol）协议的 Python 工具，提供火山引擎 Seedream 4.0 API 的图像生成功能。该工具可以在支持 MCP 协议的 IDE（如 Cursor）中使用。

## 功能特性

- **文生图（Text-to-Image）**: 根据文本提示词生成图像
- **图生图（Image-to-Image）**: 基于输入图像和文本提示词生成新图像
- **多图融合（Multi-Image Fusion）**: 将多张图像融合生成新图像
- **组图生成（Sequential Generation）**: 连续生成多张图像

- **自动保存**: 自动将生成的图片保存到本地，解决 URL 过期问题
- **Markdown 支持**: 自动生成 Markdown 格式的图片引用

## 安装配置

### 1. 环境要求

- Python 3.8+
- 火山引擎 ARK API 密钥

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 环境配置

复制 `.env.example` 文件为 `.env` 并配置必要参数：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# 火山引擎ARK API配置
ARK_API_KEY=your_ark_api_key_here
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
SEEDREAM_MODEL_ID=ep-20241230140956-xxxxx

# 默认设置
SEEDREAM_DEFAULT_SIZE=2K
SEEDREAM_DEFAULT_WATERMARK=true
SEEDREAM_TIMEOUT=60
SEEDREAM_API_TIMEOUT=60
SEEDREAM_MAX_RETRIES=3

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/seedream_mcp.log

# 自动保存配置
SEEDREAM_AUTO_SAVE_ENABLED=true
SEEDREAM_AUTO_SAVE_BASE_DIR=./seedream_images
SEEDREAM_AUTO_SAVE_DOWNLOAD_TIMEOUT=30
SEEDREAM_AUTO_SAVE_MAX_RETRIES=3
SEEDREAM_AUTO_SAVE_MAX_FILE_SIZE=52428800
SEEDREAM_AUTO_SAVE_MAX_CONCURRENT=5
SEEDREAM_AUTO_SAVE_DATE_FOLDER=true
SEEDREAM_AUTO_SAVE_CLEANUP_DAYS=30
```

### 4. 在 Cursor 中配置

在 Cursor 的设置中添加 MCP 服务器配置：

```json
{
  "mcpServers": {
    "seedream": {
      "command": "python",
      "args": ["/path/to/Seedream_MCP/main.py"],
      "env": {
        "ARK_API_KEY": "your_ark_api_key_here"
      }
    }
  }
}
```

## 工具使用

### 1. 文生图（seedream_text_to_image）

根据文本提示词生成图像。

**参数：**

- `prompt` (必需): 文本提示词，建议不超过 600 个字符
- `size` (可选): 图像尺寸，可选值：1K、2K、4K，默认 1K
- `watermark` (可选): 是否添加水印，默认 true
- `response_format` (可选): 响应格式，可选值：url、b64_json，默认 url
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "一只可爱的小猫坐在花园里，阳光明媚，高清摄影",
  "size": "2K",
  "watermark": false,
  "response_format": "url",
  "auto_save": true,
  "custom_name": "cute_cat"
}
```

### 2. 图生图（seedream_image_to_image）

基于输入图像和文本提示词生成新图像。

**参数：**

- `prompt` (必需): 文本提示词
- `image` (必需): 输入图像的 URL 或本地文件路径
- `size` (可选): 图像尺寸，默认 1K
- `watermark` (可选): 是否添加水印，默认 true
- `response_format` (可选): 响应格式，默认 url
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "将这张图片转换为油画风格",
  "image": "/path/to/input/image.jpg",
  "size": "2K",
  "auto_save": true,
  "custom_name": "oil_painting"
}
```

### 3. 多图融合（seedream_multi_image_fusion）

将多张图像融合生成新图像。

**参数：**

- `prompt` (必需): 文本提示词
- `images` (必需): 输入图像列表（2-5 张），支持 URL 或本地文件路径
- `size` (可选): 图像尺寸，默认 1K
- `watermark` (可选): 是否添加水印，默认 true
- `response_format` (可选): 响应格式，默认 url
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "将这些图像融合成一个梦幻的场景",
  "images": [
    "/path/to/image1.jpg",
    "/path/to/image2.jpg",
    "https://example.com/image3.jpg"
  ],
  "size": "4K",
  "auto_save": true,
  "custom_name": "fusion_art"
}
```

### 4. 组图生成（seedream_sequential_generation）

连续生成多张图像。

**参数：**

- `prompt` (必需): 文本提示词
- `max_images` (可选): 最大生成图像数量（1-10），默认 4
- `size` (可选): 图像尺寸，默认 1K
- `watermark` (可选): 是否添加水印，默认 true
- `response_format` (可选): 响应格式，默认 url
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "科幻城市的未来景象",
  "max_images": 6,
  "size": "2K",
  "auto_save": true,
  "custom_name": "sci_fi_city"
}
```

## 最佳实践

### 1. 提示词编写

- **具体描述**: 使用具体、详细的描述而非抽象概念
- **风格指定**: 明确指定艺术风格、摄影风格等
- **质量关键词**: 添加"高清"、"4K"、"专业摄影"等质量关键词
- **避免冲突**: 避免相互矛盾的描述

**好的提示词示例：**

```text
一只橙色的小猫坐在木制窗台上，透过窗户看着外面的雨景，温暖的室内灯光，柔和的光影，高清摄影，景深效果
```

**避免的提示词：**

```text
猫，好看
```

### 2. 图像输入

- **支持格式**: JPG、PNG、GIF、BMP、WebP
- **文件大小**: 建议不超过 50MB
- **分辨率**: 建议使用高分辨率图像以获得更好效果
- **URL 访问**: 确保图像 URL 可以公开访问

### 3. 参数选择

- **尺寸选择**:
  - 1K: 适合快速预览和测试
  - 2K: 平衡质量和速度
  - 4K: 最高质量，适合最终输出
- **水印设置**: 商业用途建议保留水印
- **响应格式**: URL 适合直接查看，base64 适合程序处理

### 4. 自动保存功能

自动保存功能解决了生成图片 URL 在 24 小时后过期的问题：

- **启用自动保存**: 设置 `auto_save: true` 或配置全局环境变量
- **自定义文件名**: 使用 `custom_name` 参数为文件添加有意义的前缀
- **目录管理**: 系统会自动按日期和工具类型组织文件
- **Markdown 支持**: 自动生成 Markdown 格式的图片引用

**自动保存示例：**

```json
{
  "prompt": "美丽的日落风景",
  "auto_save": true,
  "custom_name": "sunset_landscape",
  "save_path": "./my_images"
}
```

**输出包含本地路径：**

```text
🖼️ 生成的图像:
  1. 图像URL: https://example.com/image.jpg
  2. 本地路径: ./images/2024-01-15/text_to_image/sunset_landscape_20240115_143022_abc123_2K.png
  3. Markdown引用: ![美丽的日落风景](./images/2024-01-15/text_to_image/sunset_landscape_20240115_143022_abc123_2K.png)
```

### 5. 错误处理

常见错误及解决方案：

- **API 密钥错误**: 检查 ARK_API_KEY 是否正确配置
- **网络超时**: 增加 SEEDREAM_API_TIMEOUT 值或检查网络连接
- **文件不存在**: 确认图像文件路径正确且文件存在
- **格式不支持**: 确认图像格式在支持列表中
- **提示词过长**: 将提示词控制在 600 字符以内

## 日志和调试

### 1. 日志配置

日志级别可以通过环境变量配置：

```env
LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=logs/seedream_mcp.log
```

### 2. 查看日志

```bash
# 查看实时日志
tail -f logs/seedream_mcp.log

# 查看错误日志
grep ERROR logs/seedream_mcp.log
```

### 3. 调试模式

启用调试模式获取详细信息：

```env
LOG_LEVEL=DEBUG
```

## 性能优化

### 1. 并发控制

- 避免同时发起过多请求
- 使用适当的超时设置
- 合理设置重试次数

### 2. 缓存策略

- 相同参数的请求可能返回相似结果
- 考虑在应用层实现结果缓存

### 3. 资源管理

- 及时清理临时文件
- 监控内存使用情况
- 定期清理日志文件

## 故障排除

### 1. 服务器无法启动

检查项：

- Python 版本是否符合要求
- 依赖包是否正确安装
- 环境变量是否正确配置
- 端口是否被占用

### 2. API 调用失败

检查项：

- API 密钥是否有效
- 网络连接是否正常
- 请求参数是否正确
- 服务器状态是否正常

### 3. 图像处理错误

检查项：

- 图像文件是否存在且可读
- 图像格式是否支持
- 文件大小是否超限
- 路径是否正确

### 4. 自动保存错误

检查项：

- 保存目录是否存在且有写入权限
- 磁盘空间是否充足
- 网络连接是否稳定（下载图片时）
- 自动保存相关环境变量是否正确配置
- 文件名是否包含非法字符

## 更新和维护

### 1. 版本更新

```bash
# 更新依赖
pip install -r requirements.txt --upgrade

# 检查配置文件
diff .env.example .env
```

### 2. 配置迁移

新版本可能需要更新配置文件，请参考 `.env.example` 文件中的最新配置项。

### 3. 数据备份

定期备份重要配置和日志文件：

```bash
# 备份配置
cp .env .env.backup

# 备份日志
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

## 技术支持

如遇到问题，请提供以下信息：

1. 错误信息和日志
2. 使用的参数和配置
3. Python 版本和操作系统
4. 复现步骤

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
