# 组图生成功能修复总结

## 🐛 问题描述

用户报告当使用 "Seedream Sequential Generation" (组图生成) 功能时,会一直 loading,无法正常生成图片。

提示词示例: "生成4张图，4个小鳄鱼 16:9"

## 🔍 问题分析

经过调查,发现了两个主要问题:

### 1. API 超时问题

**原因:**
- 组图生成需要生成多张图片,耗时较长
- 原配置的 API 超时时间为 60 秒
- 生成 4 张图片通常需要 70-80 秒

**表现:**
```
2025-11-18 10:34:31.619 | WARNING  | seedream_mcp.client:_call_api:482 - sequential_generation API 调用超时 (尝试 1/3)
2025-11-18 10:35:32.663 | WARNING  | seedream_mcp.client:_call_api:482 - sequential_generation API 调用超时 (尝试 2/3)
2025-11-18 10:36:34.703 | WARNING  | seedream_mcp.client:_call_api:482 - sequential_generation API 调用超时 (尝试 3/3)
```

### 2. 缺少七牛云集成

**原因:**
- `sequential_generation.py` 没有集成七牛云上传功能
- 只返回本地路径,没有 Markdown 图片显示
- 与 `text_to_image.py` 的行为不一致

## ✅ 解决方案

### 1. 增加 API 超时时间

修改 `.env` 文件:

```bash
# 从 60 秒增加到 180 秒
SEEDREAM_TIMEOUT=180
SEEDREAM_API_TIMEOUT=180
```

**效果:**
- 组图生成不再超时
- 可以成功生成 4 张图片

### 2. 集成七牛云上传

修改 `seedream_mcp/tools/sequential_generation.py`:

#### 2.1 添加导入

```python
from ..utils.qiniu_uploader import get_qiniu_uploader
```

#### 2.2 添加上传函数

```python
async def _upload_to_qiniu(
    auto_save_results: List[AutoSaveResult],
    result: Dict[str, Any]
) -> None:
    """上传图片到七牛云"""
    logger = get_logger(__name__)
    uploader = get_qiniu_uploader()
    
    if not uploader.enabled:
        logger.debug("七牛云未配置，跳过上传")
        return
    
    # 上传每个成功保存的图片
    for i, save_result in enumerate(auto_save_results):
        if save_result.success and save_result.local_path:
            try:
                qiniu_url = uploader.upload_file(str(save_result.local_path))
                if qiniu_url and result.get("data") and i < len(result["data"]):
                    result["data"][i]["qiniu_url"] = qiniu_url
                    logger.info(f"图片 {i+1} 已上传到七牛云: {qiniu_url}")
            except Exception as e:
                logger.warning(f"图片 {i+1} 上传到七牛云失败: {e}")
```

#### 2.3 修改响应格式

修改 `_format_sequential_generation_response()` 函数:
- 显示 Markdown 图片引用(使用七牛云 URL)
- 显示详细信息(本地路径 + 七牛云 URL)
- 如果没有七牛云,提示配置

#### 2.4 修复文件名重复问题

修改 `_handle_auto_save()` 函数,为每张图片生成唯一文件名:

```python
# 为每张图片生成唯一的文件名
unique_name = f"{custom_name}_{i+1}" if custom_name else f"{prompt}_{i+1}"
```

## 📊 修复后的效果

### 输入

```
提示词: "生成4张图，4个小鳄鱼 16:9"
max_images: 4
size: 2K
```

### 输出

```
✅ 组图生成任务完成

📝 提示词: 请生成4张不同的小鳄鱼图片，每张图片展示不同的姿态和场景
🔢 请求生成数量: 4张
📏 尺寸: 2K

🎨 实际生成图像: 4张

![图片1](https://newimg.t5t6.com/seedream/20251118_104000_小鳄鱼_1_20251118_103959.jpeg)
![图片2](https://newimg.t5t6.com/seedream/20251118_104000_小鳄鱼_2_20251118_103959.jpeg)
![图片3](https://newimg.t5t6.com/seedream/20251118_104001_小鳄鱼_3_20251118_103959.jpeg)
![图片4](https://newimg.t5t6.com/seedream/20251118_104001_小鳄鱼_4_20251118_103959.jpeg)

---
**详细信息:**

📷 图像 1:
  💾 本地保存: `/Users/joe/Dropbox/code/Seedream_MCP/seedream_images/2025-11-18/sequential_generation/小鳄鱼_1_20251118_103959.jpeg`
  ☁️  七牛云: https://newimg.t5t6.com/seedream/20251118_104000_小鳄鱼_1_20251118_103959.jpeg

📷 图像 2:
  💾 本地保存: `/Users/joe/Dropbox/code/Seedream_MCP/seedream_images/2025-11-18/sequential_generation/小鳄鱼_2_20251118_103959.jpeg`
  ☁️  七牛云: https://newimg.t5t6.com/seedream/20251118_104000_小鳄鱼_2_20251118_103959.jpeg

... (图像 3 和 4 类似)

📊 使用统计:
  • 总令牌数: 64896

💾 自动保存摘要:
  • 总计: 4张图片
  • 成功: 4张
  • 失败: 0张
```

## 🎯 关键改进

1. ✅ **不再超时**: API 超时时间从 60 秒增加到 180 秒
2. ✅ **七牛云上传**: 自动上传所有生成的图片到七牛云
3. ✅ **Markdown 显示**: 使用七牛云 URL 生成 Markdown 图片引用
4. ✅ **唯一文件名**: 每张图片有唯一的文件名 (`_1`, `_2`, `_3`, `_4`)
5. ✅ **详细信息**: 显示本地路径和七牛云 URL
6. ✅ **一致性**: 与 `text_to_image` 工具的行为保持一致

## 📝 使用建议

### 简单提示词

虽然可以使用简单提示词如 "4个小鳄鱼",但建议使用更详细的描述:

```
"请生成4张不同的小鳄鱼图片，每张图片展示不同的姿态和场景"
```

### 超时时间

- 生成 1-2 张图片: 60 秒通常足够
- 生成 3-4 张图片: 建议 120-180 秒
- 生成 5+ 张图片: 建议 180-300 秒

当前配置: 180 秒,适合大多数场景

## 🔧 相关文件

- `.env` - 增加超时时间配置
- `seedream_mcp/tools/sequential_generation.py` - 添加七牛云集成
- `seedream_mcp/utils/qiniu_uploader.py` - 七牛云上传器(已存在)

## 📚 相关文档

- [QINIU_INTEGRATION_SUMMARY.md](QINIU_INTEGRATION_SUMMARY.md) - 七牛云集成总结
- [docs/QINIU_UPLOAD.md](docs/QINIU_UPLOAD.md) - 七牛云功能文档
- [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - 使用示例

