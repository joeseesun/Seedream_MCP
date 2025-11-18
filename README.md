# Seedream 4.0 MCP 工具

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![MCP](https://img.shields.io/badge/MCP-compatible-orange.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

基于火山引擎 Seedream 4.0 API 的 MCP（Model Context Protocol）工具集，提供文生图、图生图、多图融合和组图生成等功能。

## 功能特性

- 🎨 **文生图**：根据文本描述生成高质量图像
- 🖼️ **图生图**：基于参考图像和文本指令生成新图像
- 🎭 **多图融合**：融合多张参考图的特征生成新图像
- 📚 **组图生成**：生成一组内容关联的图像序列
- 💾 **自动保存**：自动下载并保存生成的图片到本地，解决 URL 过期问题
- ☁️ **七牛云上传**：可选的七牛云存储集成，自动上传图片并生成公网可访问的 URL
- 📝 **Markdown 支持**：自动生成图片的 Markdown 引用格式（支持七牛云 URL 和本地路径）
- 🔧 **完整的 MCP 协议支持**：符合 MCP 标准，可与支持 MCP 的客户端无缝集成
- 🖼️ **直接图片显示**：支持 MCP ImageContent 类型，可在客户端中直接预览图片

## 安装要求

- Python 3.8+
- 火山引擎 Seedream 4.0 API 密钥

## 安装方法

### 1. 克隆项目

```bash
git clone <repository-url>
cd Seedream_MCP
```

### 2. 安装依赖

```bash
pip install -e .
```

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# 必需配置
ARK_API_KEY=your_api_key_here

# 可选配置
ARK_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
SEEDREAM_MODEL_ID=doubao-seedream-4-0-250828
SEEDREAM_DEFAULT_SIZE=2K
SEEDREAM_DEFAULT_WATERMARK=true
SEEDREAM_TIMEOUT=60
SEEDREAM_API_TIMEOUT=60
SEEDREAM_MAX_RETRIES=3
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

# 七牛云配置（可选，用于上传图片到七牛云存储）
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_DOMAIN=https://your-domain.com
```

**注意**: 配置七牛云后,生成的图片会自动上传到七牛云,并在返回结果中提供公网可访问的 Markdown 图片链接。详见 [七牛云集成文档](docs/QINIU_UPLOAD.md)。

### 4. 配置 MCP 客户端

在你的 MCP 客户端配置文件中添加以下配置:

**Raycast AI / Claude Desktop / Cline 等:**

```json
{
  "mcpServers": {
    "seedream": {
      "command": "python",
      "args": [
        "/你的路径/Seedream_MCP/main.py"
      ],
      "env": {
        "ARK_BASE_URL": "https://ark.cn-beijing.volces.com/api/v3"
      }
    }
  }
}
```

**配置文件位置:**
- **Raycast AI**: `~/Library/Application Support/com.raycast.macos/mcp.json`
- **Claude Desktop**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Cline (VSCode)**: `.vscode/settings.json` 或用户设置

**重要提示:**
- 将 `/你的路径/Seedream_MCP/main.py` 替换为你的实际项目路径
- 确保 Python 环境已安装所有依赖
- 配置完成后重启 MCP 客户端

## 使用方法

### 作为 MCP 服务器运行

```bash
python -m seedream_mcp.server
```

### 在代码中使用

```python
import asyncio
from seedream_mcp import SeedreamClient, SeedreamConfig

async def main():
    # 加载配置
    config = SeedreamConfig.from_env()

    # 创建客户端
    client = SeedreamClient(config)

    try:
        # 文生图（启用自动保存）
        result = await client.text_to_image(
            prompt="一只可爱的小猫咪，卡通风格",
            size="2K",
            watermark=True,
            auto_save=True,
            custom_name="cute_cat"
        )
        print(f"生成的图像URL: {result['image_url']}")
        print(f"本地保存路径: {result['local_path']}")
        print(f"Markdown引用: {result['markdown']}")

        # 图生图
        result = await client.image_to_image(
            prompt="将这张图片转换为油画风格",
            image="path/to/image.jpg",
            size="2K",
            auto_save=True
        )
        print(f"转换后的图像URL: {result['image_url']}")
        print(f"本地保存路径: {result['local_path']}")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

## 响应格式说明

所有图片生成工具都支持三种响应格式:

### 1. image 格式(推荐,默认)

返回 MCP ImageContent 类型,可在支持的客户端中直接显示图片。

```json
{
  "prompt": "一只可爱的小猫咪",
  "response_format": "image"
}
```

**优点**:
- ✅ 直接在 MCP 客户端中预览图片
- ✅ 最佳用户体验
- ✅ 无需手动打开 URL

**缺点**:
- ⚠️ 需要下载图片,响应时间稍长
- ⚠️ 数据量较大

### 2. url 格式

返回图片 URL 链接。

```json
{
  "prompt": "一只可爱的小猫咪",
  "response_format": "url"
}
```

**优点**:
- ✅ 响应速度快
- ✅ 数据量小
- ✅ 可以分享链接

**缺点**:
- ⚠️ URL 在 24 小时后过期
- ⚠️ 需要手动打开链接查看

### 3. b64_json 格式

返回 base64 编码的图片数据。

```json
{
  "prompt": "一只可爱的小猫咪",
  "response_format": "b64_json"
}
```

**优点**:
- ✅ 适合程序处理
- ✅ 不依赖外部 URL

**缺点**:
- ⚠️ 数据量非常大
- ⚠️ 不便于直接查看

## 工具说明

### 1. seedream_text_to_image

根据文本描述生成图像。

**参数：**

- `prompt` (必需): 文本描述，建议不超过 300 汉字或 600 英文单词
- `size` (可选): 图像尺寸，可选值：1K、2K、4K，默认 2K
- `watermark` (可选): 是否添加水印，默认 true
- `response_format` (可选): 响应格式，可选值：image、url、b64_json，默认 image
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "一只可爱的小猫咪，卡通风格",
  "size": "2K",
  "watermark": true,
  "response_format": "image",
  "auto_save": true,
  "custom_name": "cute_cat"
}
```

### 2. seedream_image_to_image

基于参考图像和文本指令生成新图像。

**参数：**

- `prompt` (必需): 图像编辑指令
- `image` (必需): 参考图像 URL 或本地文件路径
- `size` (可选): 输出图像尺寸，默认 2K
- `watermark` (可选): 是否添加水印，默认 true
- `response_format` (可选): 响应格式，可选值：image、url、b64_json，默认 image
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "将这张图片转换为油画风格",
  "image": "https://example.com/image.jpg",
  "size": "2K",
  "watermark": false,
  "auto_save": true,
  "custom_name": "oil_painting"
}
```

### 3. seedream_multi_image_fusion

融合多张参考图的特征生成新图像。

**参数：**

- `prompt` (必需): 融合指令描述
- `images` (必需): 多张参考图像 URL 或文件路径数组（2-5 张）
- `size` (可选): 输出图像尺寸，默认 2K
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "将这些图片融合成一个艺术作品",
  "images": [
    "https://example.com/image1.jpg",
    "https://example.com/image2.jpg",
    "https://example.com/image3.jpg"
  ],
  "size": "4K",
  "auto_save": true,
  "custom_name": "fusion_art"
}
```

### 4. seedream_sequential_generation

生成一组内容关联的图像序列。

**参数：**

- `prompt` (必需): 组图生成描述
- `max_images` (可选): 最大图像数量（1-10），默认 3
- `images` (可选): 参考图像数组
- `size` (可选): 图像尺寸，默认 2K
- `auto_save` (可选): 是否自动保存图片到本地，默认使用全局配置
- `save_path` (可选): 自定义保存路径，不指定则使用默认路径
- `custom_name` (可选): 自定义文件名前缀

**示例：**

```json
{
  "prompt": "科幻城市景观，未来主义风格",
  "max_images": 4,
  "size": "2K",
  "auto_save": true,
  "custom_name": "sci_fi_city"
}
```

## 配置选项

| 环境变量                              | 描述                 | 默认值                                     | 必需 |
| ------------------------------------- | -------------------- | ------------------------------------------ | ---- |
| `ARK_API_KEY`                         | 火山引擎 API 密钥    | -                                          | ✅   |
| `ARK_BASE_URL`                        | API 基础 URL         | <https://ark.cn-beijing.volces.com/api/v3> | ❌   |
| `SEEDREAM_MODEL_ID`                   | 模型 ID              | doubao-seedream-4-0-250828                 | ❌   |
| `SEEDREAM_DEFAULT_SIZE`               | 默认图像尺寸         | 2K                                         | ❌   |
| `SEEDREAM_DEFAULT_WATERMARK`          | 默认水印设置         | true                                       | ❌   |
| `SEEDREAM_TIMEOUT`                    | 请求超时时间（秒）   | 60                                         | ❌   |
| `SEEDREAM_API_TIMEOUT`                | API 超时时间（秒）   | 60                                         | ❌   |
| `SEEDREAM_MAX_RETRIES`                | 最大重试次数         | 3                                          | ❌   |
| `LOG_LEVEL`                           | 日志级别             | INFO                                       | ❌   |
| `LOG_FILE`                            | 日志文件路径         | logs/seedream_mcp.log                      | ❌   |
| `SEEDREAM_AUTO_SAVE_ENABLED`          | 是否启用自动保存     | true                                       | ❌   |
| `SEEDREAM_AUTO_SAVE_BASE_DIR`         | 自动保存基础目录     | ./seedream_images                          | ❌   |
| `SEEDREAM_AUTO_SAVE_DOWNLOAD_TIMEOUT` | 下载超时时间（秒）   | 30                                         | ❌   |
| `SEEDREAM_AUTO_SAVE_MAX_RETRIES`      | 下载最大重试次数     | 3                                          | ❌   |
| `SEEDREAM_AUTO_SAVE_MAX_FILE_SIZE`    | 最大文件大小（字节） | 52428800                                   | ❌   |
| `SEEDREAM_AUTO_SAVE_MAX_CONCURRENT`   | 最大并发下载数       | 5                                          | ❌   |
| `SEEDREAM_AUTO_SAVE_DATE_FOLDER`      | 是否创建日期文件夹   | true                                       | ❌   |
| `SEEDREAM_AUTO_SAVE_CLEANUP_DAYS`     | 自动清理天数         | 30                                         | ❌   |

## 自动保存功能

自动保存功能解决了生成图片 URL 在 24 小时后过期的问题，提供永久可用的本地图片存储。

### 核心特性

- **自动下载**：生成图片后自动下载到本地指定目录
- **智能命名**：使用时间戳 + 内容哈希 + 尺寸信息的命名规则
- **目录管理**：按工具类型和日期自动分类存储
- **Markdown 支持**：自动生成本地图片的 Markdown 引用格式
- **错误恢复**：下载失败时提供原始 URL 作为备选
- **并发下载**：支持批量图片的并发下载处理

### 使用示例

```python
# 启用自动保存的文生图
result = await client.text_to_image(
    prompt="美丽的风景画",
    auto_save=True,
    custom_name="landscape"
)

# 返回结果包含：
# - image_url: 原始图片URL
# - local_path: 本地保存路径
# - markdown: Markdown引用格式
# - save_result: 保存操作的详细信息
```

### 文件组织结构

```markdown
images/
├── 2024-01-15/
│ ├── text_to_image/
│ │ ├── landscape_20240115_143022_abc123_2K.png
│ │ └── portrait_20240115_143045_def456_4K.png
│ ├── image_to_image/
│ │ └── style_transfer_20240115_144001_ghi789_2K.png
│ └── multi_image_fusion/
│ └── fusion_art_20240115_145030_jkl012_4K.png
└── 2024-01-16/
└── ...
```

### 配置说明

- **SEEDREAM_AUTO_SAVE_ENABLED**: 全局启用/禁用自动保存
- **SEEDREAM_AUTO_SAVE_BASE_DIR**: 图片保存的根目录
- **SEEDREAM_AUTO_SAVE_DATE_FOLDER**: 是否按日期创建子文件夹
- **SEEDREAM_AUTO_SAVE_MAX_FILE_SIZE**: 限制下载的最大文件大小
- **SEEDREAM_AUTO_SAVE_MAX_CONCURRENT**: 控制并发下载数量
- **SEEDREAM_AUTO_SAVE_CLEANUP_DAYS**: 自动清理超过指定天数的旧文件

## 错误处理

工具提供完整的错误处理机制：

- **参数验证错误**：检查必需参数和参数格式
- **API 调用错误**：处理网络错误、超时等问题
- **认证错误**：API 密钥无效或过期
- **配额错误**：API 调用次数超限
- **服务器错误**：火山引擎服务异常

## 日志记录

工具支持详细的日志记录：

- 函数调用日志
- API 请求和响应日志
- 错误和异常日志
- 性能监控日志

日志级别可通过 `LOG_LEVEL` 环境变量配置。

## 开发和测试

### 运行测试

```bash
# 运行集成测试
python tests/test_mcp_integration.py

# 运行验证脚本
python verify_installation.py
```

### 项目结构

```text
Seedream_MCP/
├── seedream_mcp/           # 主要代码
│   ├── __init__.py
│   ├── client.py           # API客户端
│   ├── config.py           # 配置管理
│   ├── server.py           # MCP服务器
│   ├── tools/              # 工具实现
│   └── utils/              # 工具函数
├── docs/                   # 文档目录
├── tests/                  # 测试文件
├── examples/               # 使用示例
├── verifys/                # 验证脚本
├── .env.example           # 环境变量示例
├── main.py                # 主程序入口
├── requirements.txt       # 依赖列表
└── README.md             # 说明文档
```

## 许可证

本项目采用 MIT 许可证。

## 支持

如有问题或建议，请提交 Issue 或 Pull Request。
