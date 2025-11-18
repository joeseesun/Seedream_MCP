# Seedream MCP 快速开始指南

## ✅ 问题已解决

你的 MCP 工具**完全正常工作**!之前的"问题"其实不是问题,只是返回格式的优化空间。

现在已经完成以下优化:

1. ✅ **添加了直接图片显示功能** - 使用 `response_format="image"` 可以在 MCP 客户端中直接看到图片
2. ✅ **显示本地保存路径** - 返回结果中会显示图片保存在哪里
3. ✅ **支持简单提示词** - "小猫"、"生成个小猫" 这样的简单描述完全支持
4. ✅ **支持复杂提示词** - 详细的描述也完全支持

## 📁 图片保存位置

所有生成的图片都保存在:

```
/Users/joe/Dropbox/code/Seedream_MCP/seedream_images/
```

按日期和工具类型组织:
```
seedream_images/
└── 2025-11-18/
    ├── text_to_image/
    │   ├── 小猫_20251118_095341.jpeg
    │   ├── test_cat_1_20251118_095346.jpeg
    │   └── 一只可爱的橘色小猫咪坐在窗台上阳光洒在身上卡通风格_20251118_095353.jpeg
    └── image_to_image/
        └── ...
```

## 🎯 使用示例

### 最简单的用法

在 MCP 客户端中,你只需要说:

```
"生成个小猫"
```

或者:

```
"画一只小猫"
```

工具会自动:
1. 生成图片
2. 保存到本地
3. 在客户端中直接显示图片
4. 告诉你保存在哪里

### 完整的 JSON 调用

```json
{
  "prompt": "小猫"
}
```

或者带更多参数:

```json
{
  "prompt": "一只可爱的小猫咪",
  "size": "2K",
  "watermark": false,
  "response_format": "image"
}
```

### 自定义保存位置和文件名

```json
{
  "prompt": "小猫",
  "save_path": "/Users/joe/Pictures/cats",
  "custom_name": "my_cute_cat"
}
```

## 📊 返回结果示例

使用 `response_format="image"` (默认) 时,你会收到:

```
✅ 图片生成成功！
提示词: 小猫
尺寸: 2K
💾 本地保存 1: /Users/joe/Dropbox/code/Seedream_MCP/seedream_images/2025-11-18/text_to_image/小猫_20251118_095341.jpeg

📸 Markdown 引用:
![图片1](file:///Users/joe/Dropbox/code/Seedream_MCP/seedream_images/2025-11-18/text_to_image/小猫_20251118_095341.jpeg)

[图片直接显示在这里]
```

**说明**:
- 💾 显示图片的本地保存路径(绝对路径)
- 📸 提供 Markdown 格式的图片引用,在支持 Markdown 的客户端中可以直接显示
- 图片以 MCP ImageContent 格式返回,在支持的客户端中直接显示

## 🔧 三种响应格式对比

| 格式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **image** (推荐) | 直接显示图片,最佳体验 | 响应稍慢,数据量大 | MCP 客户端使用 |
| **url** | 响应快,数据量小 | URL 24小时后过期,需手动打开 | 快速生成,分享链接 |
| **b64_json** | 适合程序处理 | 数据量很大,不便查看 | 程序集成 |

## 💡 提示词技巧

### 简单提示词 (完全支持!)

- "小猫"
- "生成个小猫"
- "画一只狗"
- "风景"
- "美女"

AI 会自动补充细节,生成高质量图片。

### 详细提示词 (更精确控制)

```
一只可爱的橘色小猫咪，坐在窗台上，阳光洒在身上，毛发蓬松柔软，眼睛明亮有神，背景是温馨的家居环境，卡通风格，高清画质，细节丰富
```

### 提示词建议

1. **风格**: 卡通、写实、油画、水彩、赛博朋克等
2. **光线**: 阳光、柔和光线、戏剧性光线等
3. **细节**: 高清、4K、细节丰富等
4. **情绪**: 温馨、欢快、神秘、宁静等

## 🔍 查看生成的图片

### 方式 1: 在 MCP 客户端中直接查看 (推荐)

使用默认的 `response_format="image"`,图片会直接显示。

### 方式 2: 在 Finder 中打开

```bash
open /Users/joe/Dropbox/code/Seedream_MCP/seedream_images
```

### 方式 3: 使用命令行

```bash
# 查看今天生成的图片
ls -lh seedream_images/$(date +%Y-%m-%d)/text_to_image/

# 打开最新的图片
open "$(find seedream_images -name "*.jpeg" -type f | tail -1)"
```

## ⚙️ 配置说明

在 `.env` 文件中可以修改:

```bash
# 修改保存位置
SEEDREAM_AUTO_SAVE_BASE_DIR=/Users/joe/Pictures/Seedream

# 禁用自动保存
SEEDREAM_AUTO_SAVE_ENABLED=false

# 修改默认尺寸
SEEDREAM_DEFAULT_SIZE=4K

# 禁用水印
SEEDREAM_DEFAULT_WATERMARK=false
```

## 📚 更多文档

- [完整使用文档](docs/USAGE.md)
- [图片存储详细说明](docs/IMAGE_STORAGE.md)
- [API 文档](docs/API.md)
- [修复总结](FIXES_SUMMARY.md)

## ❓ 常见问题

**Q: 为什么我看不到图片?**

A: 确保使用 `response_format="image"` (这是默认值)。如果 MCP 客户端不支持 ImageContent,可以使用 `response_format="url"` 然后手动打开链接。

**Q: 图片保存在哪里?**

A: 默认保存在 `/Users/joe/Dropbox/code/Seedream_MCP/seedream_images/`,返回结果中会显示完整路径。

**Q: 可以用简单的提示词吗?**

A: 完全可以!"小猫"、"生成个小猫" 这样的简单描述都支持,AI 会自动补充细节。

**Q: 如何修改保存位置?**

A: 在 `.env` 文件中修改 `SEEDREAM_AUTO_SAVE_BASE_DIR`,或在调用时指定 `save_path` 参数。

## 🎉 开始使用

现在你可以直接在 MCP 客户端中使用了!

最简单的方式:
```
"生成个小猫"
```

就这么简单! 🚀

