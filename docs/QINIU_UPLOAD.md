# 七牛云上传功能

## 📖 功能说明

Seedream MCP 工具现在支持将生成的图片自动上传到七牛云存储，并在返回结果中提供公网可访问的 Markdown 图片链接。

### ✨ 特性

- ✅ **自动上传**: 图片生成后自动上传到七牛云
- ✅ **本地备份**: 同时保存到本地目录
- ✅ **Markdown 链接**: 返回公网可访问的 Markdown 图片引用
- ✅ **可选功能**: 不配置七牛云时，仍可正常使用（仅本地保存）
- ✅ **智能降级**: 上传失败时自动降级为本地路径

## 🔧 配置方法

### 1. 安装七牛 SDK

```bash
pip install qiniu
```

或者重新安装所有依赖:

```bash
pip install -r requirements.txt
```

### 2. 配置七牛云凭证

在 `.env` 文件中添加以下配置:

```bash
# 七牛云配置（可选，用于上传图片到七牛云存储）
QINIU_ACCESS_KEY=your_access_key
QINIU_SECRET_KEY=your_secret_key
QINIU_BUCKET_NAME=your_bucket_name
QINIU_DOMAIN=https://your-domain.com
```

### 3. 获取七牛云凭证

1. 登录 [七牛云控制台](https://portal.qiniu.com/)
2. 进入 **个人中心** -> **密钥管理**，获取 `AccessKey` 和 `SecretKey`
3. 进入 **对象存储** -> **空间管理**，创建或选择一个存储空间（Bucket）
4. 在空间设置中绑定自定义域名，或使用七牛提供的测试域名

### 4. 配置示例

```bash
# 七牛云配置
QINIU_ACCESS_KEY=AbCdEfGhIjKlMnOpQrStUvWxYz123456
QINIU_SECRET_KEY=1234567890abcdefghijklmnopqrstuvwxyz1234
QINIU_BUCKET_NAME=joemarkdown
QINIU_DOMAIN=https://img.t5t6.com
```

## 📊 使用效果

### 配置七牛云后

当你在 MCP 客户端中说 "生成个小猫" 时，会返回:

```
✅ 图片生成成功！
提示词: 小猫
尺寸: 2K

![图片1](https://img.t5t6.com/seedream/20251118_100045_小猫.jpeg)

---
**详细信息:**
💾 本地保存 1: `/Users/joe/Dropbox/code/Seedream_MCP/seedream_images/2025-11-18/text_to_image/小猫_20251118_100045.jpeg`
☁️  七牛云 1: https://img.t5t6.com/seedream/20251118_100045_小猫.jpeg
```

**客户端显示效果:**
- 如果客户端支持 Markdown 渲染，会直接显示七牛云的图片
- 图片下方显示本地保存路径和七牛云 URL
- 七牛云 URL 是公网可访问的，可以分享给他人

### 未配置七牛云时

```
✅ 图片生成成功！
提示词: 小猫
尺寸: 2K


---
**详细信息:**
💾 本地保存 1: `/Users/joe/Dropbox/code/Seedream_MCP/seedream_images/2025-11-18/text_to_image/小猫_20251118_100045.jpeg`
💡 提示: 配置七牛云后可自动上传并生成公网访问链接
```

**客户端显示效果:**
- 只显示本地保存路径
- 提示可以配置七牛云获得公网访问链接

## 🎯 优势对比

| 特性 | 配置七牛云 | 未配置七牛云 |
|------|-----------|-------------|
| Markdown 图片显示 | ✅ 是（公网 URL） | ❌ 否 |
| 公网访问 | ✅ 可以 | ❌ 不可以 |
| 分享给他人 | ✅ 可以 | ❌ 不可以 |
| 在线文档中使用 | ✅ 可以 | ❌ 不可以 |
| 本地保存 | ✅ 是 | ✅ 是 |
| 永久保存 | ✅ 双重保存 | ✅ 本地保存 |
| 需要配置 | ✅ 需要 | ❌ 不需要 |

## 🧪 测试

运行测试脚本验证七牛云上传功能:

```bash
python test_qiniu_upload.py
```

测试脚本会:
1. 检查七牛云配置状态
2. 生成一张测试图片
3. 自动上传到七牛云（如果已配置）
4. 显示完整的返回结果

## 🔍 技术细节

### 上传流程

1. 图片生成后，先保存到本地
2. 检查七牛云配置是否完整
3. 如果配置完整，自动上传到七牛云
4. 生成公网可访问的 URL
5. 在返回结果中同时提供本地路径和七牛云 URL

### 文件命名规则

上传到七牛云的文件名格式:

```
seedream/{timestamp}_{original_filename}
```

例如:
```
seedream/20251118_100045_小猫_20251118_100045.jpeg
```

### 错误处理

- 如果七牛云上传失败，不会影响图片生成
- 会在日志中记录错误信息
- 自动降级为本地路径的 Markdown 引用

## 📝 注意事项

1. **安全性**: 
   - 不要将 `.env` 文件提交到版本控制
   - 妥善保管 AccessKey 和 SecretKey

2. **存储空间**:
   - 确保七牛云存储空间有足够的容量
   - 定期清理不需要的图片

3. **域名配置**:
   - 必须使用已绑定的域名
   - 测试域名有访问限制，建议绑定自定义域名

4. **网络要求**:
   - 上传需要稳定的网络连接
   - 上传失败不会影响本地保存

## 🚀 最佳实践

1. **开发环境**: 不配置七牛云，使用本地路径
2. **生产环境**: 配置七牛云，方便分享和在线使用
3. **备份策略**: 本地和七牛云双重保存，确保数据安全

## 🆘 常见问题

### Q: 为什么上传失败？

A: 检查以下几点:
- 七牛云凭证是否正确
- 存储空间名称是否正确
- 域名是否已绑定
- 网络连接是否正常

### Q: 可以只上传到七牛云，不保存本地吗？

A: 目前不支持。为了数据安全，始终会保存本地副本。

### Q: 上传的图片可以删除吗？

A: 可以通过七牛云控制台或 API 删除。本地文件可以手动删除。

### Q: 支持其他云存储吗？

A: 目前只支持七牛云。如需其他云存储，可以参考 `seedream_mcp/utils/qiniu_uploader.py` 实现类似的上传器。

## 📚 相关文档

- [七牛云官方文档](https://developer.qiniu.com/)
- [七牛云 Python SDK](https://developer.qiniu.com/kodo/1242/python)
- [IMAGE_STORAGE.md](IMAGE_STORAGE.md) - 本地存储说明
- [QUICK_START.md](../QUICK_START.md) - 快速开始指南

