#!/bin/bash
# 使用 GitHub CLI 自动创建仓库并迁移

set -e  # 遇到错误立即退出

echo "=========================================="
echo "迁移 Seedream_MCP 到你自己的 GitHub 仓库"
echo "=========================================="
echo ""

# 检查 GitHub CLI 是否安装
if ! command -v gh &> /dev/null; then
    echo "❌ 错误: 未找到 GitHub CLI (gh)"
    echo ""
    echo "请先安装 GitHub CLI:"
    echo "  brew install gh"
    echo ""
    echo "然后登录:"
    echo "  gh auth login"
    exit 1
fi

# 检查是否已登录
if ! gh auth status &> /dev/null; then
    echo "❌ 错误: 未登录 GitHub CLI"
    echo ""
    echo "请先登录:"
    echo "  gh auth login"
    exit 1
fi

echo "✅ GitHub CLI 已安装并登录"
echo ""

# 获取当前 GitHub 用户名
GITHUB_USER=$(gh api user -q .login)
echo "GitHub 用户: $GITHUB_USER"
echo ""

# 设置仓库名称
REPO_NAME="Seedream_MCP"
REPO_DESCRIPTION="增强版 Seedream 4.0 MCP 工具 - 支持文生图、图生图、多图融合、组图生成，集成七牛云存储和提示词模板系统"

echo "仓库名称: $REPO_NAME"
echo "仓库描述: $REPO_DESCRIPTION"
echo ""

# 询问是否创建私有仓库
read -p "是否创建私有仓库? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    VISIBILITY="--private"
    echo "将创建私有仓库"
else
    VISIBILITY="--public"
    echo "将创建公开仓库"
fi
echo ""

# 1. 查看当前远程仓库
echo "1️⃣  当前远程仓库:"
git remote -v
echo ""

# 2. 移除原来的 origin
echo "2️⃣  移除原来的 origin..."
git remote remove origin
echo "✅ 已移除原来的 origin"
echo ""

# 3. 创建新的 GitHub 仓库
echo "3️⃣  创建新的 GitHub 仓库..."
gh repo create "$REPO_NAME" \
    --description "$REPO_DESCRIPTION" \
    $VISIBILITY \
    --source=. \
    --remote=origin
echo "✅ 已创建仓库: https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""

# 4. 查看新的远程仓库
echo "4️⃣  新的远程仓库:"
git remote -v
echo ""

# 5. 确保 .env 不会被提交
echo "5️⃣  检查 .gitignore..."
if ! grep -q "^\.env$" .gitignore; then
    echo ".env" >> .gitignore
    echo "✅ 已添加 .env 到 .gitignore"
else
    echo "✅ .env 已在 .gitignore 中"
fi
echo ""

# 6. 提交所有修改
echo "6️⃣  提交所有修改..."
git add .
git commit -m "feat: 增强版 Seedream MCP

✨ 新功能:
- 添加七牛云自动上传功能
- 添加提示词模板系统 (公众号封面、潮流派对等8个模板)
- 支持 Raycast AI Markdown 图片渲染
- 添加 .env.example 配置模板

🐛 修复:
- 修复图片保存路径问题
- 修复工具描述和参数
- 优化图片返回格式

📝 文档:
- 添加详细的安装和配置文档
- 添加 MCP 客户端配置说明
- 添加七牛云集成文档
- 添加使用示例
" || echo "⚠️  没有新的修改需要提交"
echo ""

# 7. 推送到你的仓库
echo "7️⃣  推送到你的 GitHub 仓库..."
git push -u origin main
echo "✅ 已推送到你的仓库"
echo ""

echo "=========================================="
echo "🎉 迁移完成!"
echo "=========================================="
echo ""
echo "仓库信息:"
echo "  📦 仓库名称: $REPO_NAME"
echo "  🔗 仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
echo "  👤 所有者: $GITHUB_USER"
echo ""
echo "现在你可以:"
echo "  1. 访问仓库: gh repo view --web"
echo "  2. 推送修改: git push"
echo "  3. 拉取更新: git pull"
echo "  4. 克隆仓库: git clone https://github.com/$GITHUB_USER/$REPO_NAME.git"
echo ""
echo "=========================================="

