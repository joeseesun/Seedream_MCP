# 图片存储说明

## 📁 存储位置

生成的图片会自动保存到以下位置:

```
/Users/joe/Dropbox/code/Seedream_MCP/seedream_images/
```

### 目录结构

如果启用了日期文件夹功能（默认启用），图片会按日期组织:

```
seedream_images/
├── 2025-11-18/
│   ├── text_to_image_20251118_094713_abc123.jpeg
│   ├── text_to_image_20251118_095234_def456.jpeg
│   └── image_to_image_20251118_100512_ghi789.jpeg
├── 2025-11-19/
│   └── ...
└── ...
```

如果禁用日期文件夹，所有图片会直接保存在 `seedream_images/` 目录下。

## ⚙️ 配置选项

在 `.env` 文件中可以配置以下选项:

```bash
# 是否启用自动保存
SEEDREAM_AUTO_SAVE_ENABLED=true

# 保存目录（相对或绝对路径）
SEEDREAM_AUTO_SAVE_BASE_DIR=./seedream_images

# 是否按日期创建子文件夹
SEEDREAM_AUTO_SAVE_DATE_FOLDER=true

# 自动清理天数（超过此天数的图片会被清理）
SEEDREAM_AUTO_SAVE_CLEANUP_DAYS=30
```

### 修改存储位置

如果想修改存储位置，可以:

**方式 1: 修改全局配置**

编辑 `.env` 文件:
```bash
# 使用绝对路径
SEEDREAM_AUTO_SAVE_BASE_DIR=/Users/joe/Pictures/Seedream

# 或使用相对路径
SEEDREAM_AUTO_SAVE_BASE_DIR=./my_images
```

**方式 2: 在调用时指定**

```json
{
  "prompt": "一只小猫",
  "save_path": "/Users/joe/Pictures/cats",
  "custom_name": "cute_cat"
}
```

## 🎯 使用示例

### 简单提示词

MCP 工具完全支持简单的提示词:

```json
{
  "prompt": "一只小猫"
}
```

```json
{
  "prompt": "生成个小猫"
}
```

```json
{
  "prompt": "猫"
}
```

### 详细提示词

也支持复杂的详细描述:

```json
{
  "prompt": "一只可爱的橘色小猫咪，坐在窗台上，阳光洒在身上，毛发蓬松柔软，眼睛明亮有神，背景是温馨的家居环境，卡通风格，高清画质，细节丰富"
}
```

### 完整参数示例

```json
{
  "prompt": "一只小猫",
  "size": "2K",
  "watermark": false,
  "response_format": "image",
  "auto_save": true,
  "save_path": "/Users/joe/Pictures/cats",
  "custom_name": "my_cat"
}
```

## 💡 提示

1. **简单提示词**: 适合快速生成，AI 会自动补充细节
2. **详细提示词**: 可以更精确地控制生成结果
3. **自动保存**: 默认启用，图片会自动保存到本地
4. **URL 过期**: API 返回的 URL 在 24 小时后会过期，建议启用自动保存
5. **本地路径**: 使用 `response_format="image"` 时，返回的文本中会显示本地保存路径

## 🔍 查看生成的图片

### 方式 1: 在 MCP 客户端中直接查看

使用 `response_format="image"` (默认)，图片会直接显示在客户端中。

### 方式 2: 在 Finder 中打开

```bash
open /Users/joe/Dropbox/code/Seedream_MCP/seedream_images
```

### 方式 3: 使用命令行查看

```bash
# 查看今天生成的图片
ls -lh seedream_images/$(date +%Y-%m-%d)/

# 查看所有图片
find seedream_images -name "*.jpeg" -type f
```

## 🗑️ 清理旧图片

系统会自动清理超过 30 天的图片（可配置）。

手动清理:
```bash
# 删除 30 天前的图片
find seedream_images -name "*.jpeg" -type f -mtime +30 -delete

# 删除所有图片
rm -rf seedream_images/*
```

## ❓ 常见问题

**Q: 为什么找不到生成的图片?**

A: 检查以下几点:
1. 确认 `SEEDREAM_AUTO_SAVE_ENABLED=true`
2. 检查 `seedream_images/` 目录是否存在
3. 如果启用了日期文件夹，检查对应日期的子目录
4. 查看日志文件 `logs/seedream_mcp.log` 了解详情

**Q: 可以修改文件名格式吗?**

A: 可以使用 `custom_name` 参数指定文件名前缀:
```json
{
  "prompt": "一只小猫",
  "custom_name": "my_cat"
}
```
生成的文件名会是: `my_cat_20251118_094713_abc123.jpeg`

**Q: 图片占用空间太大怎么办?**

A: 可以:
1. 减少 `SEEDREAM_AUTO_SAVE_CLEANUP_DAYS` 的值，更频繁地清理旧图片
2. 手动删除不需要的图片
3. 禁用自动保存，只在需要时手动保存

