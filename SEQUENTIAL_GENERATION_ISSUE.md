# 🔍 组图生成只生成1张图的问题分析

## 📋 问题

用户说 **"生成4张图，提示词：'可口可乐'"** 时:
1. ✅ 正确调用了 `seedream_sequential_generation` 工具
2. ❌ 但只生成了1张图,而不是4张

## 🔬 问题分析

### 测试结果

运行测试脚本 `test_sequential_api.py`:

```
提示词: '你好呀'
max_images: 4

API 返回了 1 张图片
usage: {'generated_images': 1, ...}
```

**API 确实只返回了1张图片!**

### 请求参数

```python
{
  'sequential_image_generation': 'auto',
  'sequential_image_generation_options': {'max_images': 4},
  'prompt': '你好呀',
  ...
}
```

参数传递是正确的,但 API 只返回了1张图。

## 💡 根本原因

根据 [jimeng-mcp-apicore](https://github.com/Ceeon/jimeng-mcp-apicore) 项目的文档:

> **组图生成使用 `auto` 模式，AI会根据prompt内容自动决定生成数量**

**重要提示:**
- ⭐ **在prompt中明确说明需要的数量**（如"生成3张"）
- ⭐ **详细描述每张图的内容**
- ⭐ `max_images` 参数设置为期望的数量

### 示例

**正确的 prompt:**
```python
prompt="生成3张不同时间段的城市风景：早晨的朝阳、中午的繁忙、夜晚的灯火"
max_images=3
```

**错误的 prompt:**
```python
prompt="你好呀"  # ❌ 没有说明要生成多张
max_images=4     # 即使设置了4,API也可能只生成1张
```

## 🎯 解决方案

### 方案 1: 修改 Prompt 格式化逻辑 (推荐)

当用户说 **"生成4张图，提示词：'可口可乐'"** 时,我们应该:

1. **提取数量**: 4张
2. **提取内容**: 可口可乐
3. **重新格式化 prompt**: "生成4张可口可乐的图片，每张展示不同的角度或场景"

**修改位置:** `seedream_mcp/tools/sequential_generation.py`

```python
async def handle_sequential_generation(arguments: Dict[str, Any]) -> List[TextContent]:
    prompt = arguments.get("prompt")
    max_images = arguments.get("max_images", 4)
    
    # ⭐ 新增: 格式化 prompt,明确说明数量
    if max_images > 1:
        # 检查 prompt 中是否已经包含数量信息
        if not any(str(i) in prompt for i in range(2, 16)):
            # 如果没有,添加数量信息
            prompt = f"生成{max_images}张{prompt}的图片，每张展示不同的角度、场景或风格"
    
    # 调用 API
    result = await client.sequential_generation(
        prompt=prompt,  # 使用格式化后的 prompt
        max_images=max_images,
        ...
    )
```

### 方案 2: 修改工具描述,引导用户

在工具描述中明确说明:

```python
description="""
使用Seedream 4.0【批量生成多张图像】（组图生成）。

⭐ 重要：prompt中必须明确说明要生成的数量和每张图的内容！

正确示例：
- "生成3张不同时间的城市风景：早晨、中午、夜晚"
- "生成4张可口可乐的产品图：正面、侧面、俯视、特写"

错误示例：
- "可口可乐" ❌ (没有说明数量和变化)
"""
```

## 📝 推荐实施

**立即实施方案 1:**

1. 在 `handle_sequential_generation()` 中添加 prompt 格式化逻辑
2. 自动为用户补充数量信息
3. 提高用户体验

**可选实施方案 2:**

1. 优化工具描述
2. 教育用户如何正确使用
3. 长期改善

## 🧪 测试验证

修改后,测试以下场景:

```python
# 场景 1: 用户说"生成4张图，提示词：'可口可乐'"
# 系统应该:
# - max_images = 4
# - prompt = "生成4张可口可乐的图片，每张展示不同的角度、场景或风格"
# - 预期: 生成4张图

# 场景 2: 用户说"生成3张不同风格的小猫"
# 系统应该:
# - max_images = 3
# - prompt = "生成3张不同风格的小猫" (已包含数量,不修改)
# - 预期: 生成3张图
```

## ✨ 总结

**问题根源:**
- Seedream API 的 `auto` 模式根据 prompt 内容决定生成数量
- 如果 prompt 中没有明确说明要生成多张,API 可能只生成1张
- `max_images` 参数只是上限,不是强制数量

**解决方案:**
- 自动格式化 prompt,添加数量信息
- 确保 prompt 明确说明要生成多张图片

**预期效果:**
- 用户说"生成4张图，提示词：'可口可乐'"
- 系统生成4张可口可乐的图片 ✅

