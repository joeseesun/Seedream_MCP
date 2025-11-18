# 🔧 工具描述优化 - 避免误调用

## 📋 问题描述

**用户反馈:**
当用户说 **"生成4个图，提示词：'可口可乐'"** 时，系统调用了4次 `text_to_image` 工具，而不是调用1次 `sequential_generation` 工具。

**根本原因:**
1. **工具描述不够明确** - Claude 不知道什么时候该用哪个工具
2. **参数定义不清晰** - 两个工具的必填参数都只有 `prompt`,难以区分
3. **参数顺序问题** - `max_images` 排在 `prompt` 后面,不够显眼

**原来的问题:**

- ❌ `text_to_image`: "使用Seedream 4.0根据文本提示词生成图像"
  - **问题:** 没有说明只生成"单张"图片
  - **结果:** Claude 认为可以调用多次来生成多张图

- ❌ `sequential_generation`: "使用Seedream 4.0连续生成多张图像（组图生成）"
  - **问题:** 没有明确说明"何时使用"
  - **结果:** Claude 不知道什么时候应该用这个工具

---

## ✅ 解决方案

### 修改后的工具描述

#### 1️⃣ 文生图 (text_to_image)
```python
description="使用Seedream 4.0根据文本提示词生成【单张】图像。如果需要生成多张图片，请使用 seedream_sequential_generation 工具"
```

**改进:**
- ✅ 明确说明生成"单张"图像
- ✅ 引导用户使用组图生成工具

#### 2️⃣ 图生图 (image_to_image)
```python
description="使用Seedream 4.0根据输入图像和文本提示词生成【单张】新图像（图生图）。如果需要基于一张图生成多张变体，请使用 seedream_sequential_generation 工具"
```

**改进:**
- ✅ 明确说明生成"单张"图像
- ✅ 说明功能是"图生图"
- ✅ 引导用户使用组图生成工具

#### 3️⃣ 多图融合 (multi_image_fusion)
```python
description="使用Seedream 4.0将多张图像融合生成【单张】新图像（多图融合）。需要提供2-10张输入图片。如果需要生成多张融合结果，请使用 seedream_sequential_generation 工具"
```

**改进:**
- ✅ 明确说明生成"单张"图像
- ✅ 说明功能是"多图融合"
- ✅ 说明输入要求(2-10张)
- ✅ 引导用户使用组图生成工具

#### 4️⃣ 组图生成 (sequential_generation) ⭐ 关键修改
```python
description="使用Seedream 4.0【批量生成多张图像】（组图生成）。当用户要求生成2张或更多图片时使用此工具。支持3种输入类型：文生组图、单图生组图、多图生组图。最多可生成15张图片"

# 参数定义优化
properties = {
    "max_images": {  # ⭐ 移到第一位,设为必填
        "type": "integer",
        "description": "要生成的图像数量（必填）。用户说'生成4张图'时，此参数应为4",
        "minimum": 1,
        "maximum": 15
    },
    "prompt": {
        "type": "string",
        "description": "图像内容的文本提示词（如'可口可乐'、'小猫'等）。不需要在提示词中包含数量信息，数量由 max_images 参数指定",
        "maxLength": 600
    },
    ...
}
required = ["prompt", "max_images"]  # ⭐ max_images 设为必填
```

**改进:**
- ✅ 明确说明"批量生成多张图像"
- ✅ **明确使用场景:** "当用户要求生成2张或更多图片时"
- ✅ 说明支持的输入类型
- ✅ 说明数量限制(最多15张)
- ✅ **`max_images` 移到第一位** - 更显眼
- ✅ **`max_images` 设为必填** - 强制 Claude 提供数量
- ✅ **优化参数描述** - 明确告诉 Claude 如何使用

---

## 🎯 预期效果

### 修改前
```
用户: "生成4个图，提示词：'可口可乐'"
系统: 调用 text_to_image 4次 ❌
```

### 修改后
```
用户: "生成4个图，提示词：'可口可乐'"
系统: 调用 sequential_generation 1次 ✅
参数: {
  "prompt": "可口可乐",
  "max_images": 4
}
```

---

## 📝 修改的文件

1. `seedream_mcp/tools/text_to_image.py` - 文生图工具
2. `seedream_mcp/tools/image_to_image.py` - 图生图工具
3. `seedream_mcp/tools/multi_image_fusion.py` - 多图融合工具
4. `seedream_mcp/tools/sequential_generation.py` - 组图生成工具

---

## 🔑 关键原则

在设计 MCP 工具描述时,应该:

1. **明确功能范围** - 说清楚工具能做什么、不能做什么
2. **说明使用场景** - 告诉 AI 什么时候应该用这个工具
3. **引导正确选择** - 如果有更合适的工具,明确指出
4. **避免歧义** - 使用【】强调关键信息(如"单张"、"多张")
5. **参数顺序** - 最重要的参数放在最前面
6. **必填参数** - 关键区分参数应设为必填
7. **参数描述** - 明确告诉 AI 如何使用参数(包含示例)

---

## ✨ 总结

通过优化工具描述,我们:
- ✅ 避免了重复调用单图工具
- ✅ 引导 AI 正确选择组图生成工具
- ✅ 提升了用户体验
- ✅ 减少了不必要的 API 调用

现在当用户要求生成多张图片时,系统会自动选择正确的工具! 🎊

