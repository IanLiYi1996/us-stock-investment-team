#!/bin/bash
# =============================================================
# US Stock Investment Team — 一键部署脚本
# 用法: bash setup.sh
# =============================================================

set -e

WORKSPACE="$HOME/.openclaw/workspace-cio"
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/scripts"
AGENTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/agents"
SHARED_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/shared"
PRINCIPLES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/principles"

echo ""
echo "🤖 US Stock Investment Team — 部署向导"
echo "========================================"
echo ""

# ─── 1. 检查依赖 ───────────────────────────────────────────────
echo "📦 检查依赖..."

check_cmd() {
  if ! command -v "$1" &> /dev/null; then
    echo "  ❌ 未找到: $1 — 请先安装"
    MISSING=1
  else
    echo "  ✅ $1"
  fi
}

MISSING=0
check_cmd python3
check_cmd node
check_cmd openclaw

if [ "$MISSING" = "1" ]; then
  echo ""
  echo "请先安装缺少的依赖，然后重新运行此脚本。"
  echo "  OpenClaw: npm install -g openclaw"
  exit 1
fi

# ─── 2. 检查 Python 包 ─────────────────────────────────────────
echo ""
echo "📦 检查 Python 包..."
python3 -c "import yfinance" 2>/dev/null && echo "  ✅ yfinance" || echo "  ⚠️  yfinance 未安装 (pip install yfinance)"
python3 -c "import alpaca" 2>/dev/null && echo "  ✅ alpaca-trade-api" || echo "  ⚠️  alpaca 未安装 (pip install alpaca-trade-api)"
python3 -c "import pandas" 2>/dev/null && echo "  ✅ pandas" || echo "  ⚠️  pandas 未安装 (pip install pandas)"

# ─── 3. 创建目录结构 ────────────────────────────────────────────
echo ""
echo "📁 创建工作目录..."
mkdir -p "$WORKSPACE"/{decisions,inbox,memory,principles,research,scripts,shared,signals,watchlist}
echo "  ✅ $WORKSPACE"

# ─── 4. 复制 Agent 配置 ─────────────────────────────────────────
echo ""
echo "⚙️  部署 Agent 配置..."

deploy_agent() {
  local agent=$1
  local src="$AGENTS_DIR/$agent"
  local dst

  case $agent in
    cio)      dst="$WORKSPACE" ;;
    research) dst="$HOME/.openclaw/workspace-research" ;;
    ko)       dst="$HOME/.openclaw/workspace-ko" ;;
    advisor)  dst="$HOME/.openclaw/workspace-advisor" ;;
    ops)      dst="$HOME/.openclaw/workspace-ops" ;;
  esac

  if [ -d "$src" ]; then
    mkdir -p "$dst"
    for f in "$src"/*.md; do
      if [ -f "$f" ]; then
        fname=$(basename "$f")
        if [ ! -f "$dst/$fname" ]; then
          cp "$f" "$dst/$fname"
          echo "  ✅ $agent/$fname → $dst/"
        else
          echo "  ⚠️  跳过（已存在）: $agent/$fname"
        fi
      fi
    done
  fi
}

deploy_agent cio
deploy_agent research
deploy_agent ko
deploy_agent advisor
deploy_agent ops

# ─── 5. 复制共享规则与模板到所有 workspace ──────────────────────
echo ""
echo "📋 复制共享规则与模板..."
for ws in "$WORKSPACE" "$HOME/.openclaw/workspace-research" "$HOME/.openclaw/workspace-ko" "$HOME/.openclaw/workspace-advisor" "$HOME/.openclaw/workspace-ops"; do
  mkdir -p "$ws/shared"
  for f in "$SHARED_DIR"/*.md; do
    if [ -f "$f" ]; then
      cp "$f" "$ws/shared/"
    fi
  done
done
echo "  ✅ shared/ 规则已复制到所有 5 个 workspace"

# ─── 6. 复制脚本 ────────────────────────────────────────────────
echo ""
echo "🔧 复制分析脚本..."
for f in "$SCRIPTS_DIR"/*.py "$SCRIPTS_DIR"/*.sh; do
  if [ -f "$f" ]; then
    cp "$f" "$WORKSPACE/scripts/"
    chmod +x "$WORKSPACE/scripts/$(basename $f)"
    echo "  ✅ scripts/$(basename $f)"
  fi
done

# ─── 7. 复制投资原则模板 ─────────────────────────────────────────
echo ""
echo "📚 复制投资原则模板..."
if [ ! -f "$WORKSPACE/principles/INVESTMENT_FRAMEWORK.md" ]; then
  cp "$PRINCIPLES_DIR/INVESTMENT_FRAMEWORK.md" "$WORKSPACE/principles/"
  echo "  ✅ principles/INVESTMENT_FRAMEWORK.md"
fi

# ─── 7.5 创建 KO 知识库目录 ──────────────────────────────────────
echo ""
echo "📚 创建 KO 知识库目录..."
KO_WS="$HOME/.openclaw/workspace-ko"
mkdir -p "$KO_WS"/{knowledge,inbox}
mkdir -p "$KO_WS/knowledge/decisions"
echo "  ✅ $KO_WS/knowledge/ 和 inbox/"

# ─── 7.6 创建 Ops 审计目录 ───────────────────────────────────────
echo ""
echo "🛡️  创建 Ops 审计目录..."
OPS_WS="$HOME/.openclaw/workspace-ops"
mkdir -p "$OPS_WS"/audits/{weekly,monthly,quarterly}
echo "  ✅ $OPS_WS/audits/"

# ─── 8. 配置 Alpaca ─────────────────────────────────────────────
echo ""
if [ ! -f "$HOME/.alpaca/credentials" ]; then
  echo "🔑 配置 Alpaca Paper Trading API..."
  echo "  请前往 https://app.alpaca.markets/signup 注册并获取 API Key"
  read -p "  输入 Alpaca API Key: " ALPACA_KEY
  read -p "  输入 Alpaca Secret Key: " ALPACA_SECRET
  mkdir -p "$HOME/.alpaca"
  cat > "$HOME/.alpaca/credentials" << EOF
ALPACA_API_KEY=$ALPACA_KEY
ALPACA_SECRET_KEY=$ALPACA_SECRET
EOF
  chmod 600 "$HOME/.alpaca/credentials"
  echo "  ✅ ~/.alpaca/credentials 已创建"
else
  echo "  ✅ Alpaca credentials 已存在，跳过"
fi

# ─── 9. 配置观察清单 ─────────────────────────────────────────────
echo ""
if [ ! -f "$WORKSPACE/watchlist/watchlist.yaml" ]; then
  cp "$(dirname "${BASH_SOURCE[0]}")/config/watchlist.example.yaml" "$WORKSPACE/watchlist/watchlist.yaml"
  echo "⚙️  已创建观察清单模板: $WORKSPACE/watchlist/watchlist.yaml"
  echo "  请编辑此文件，填写你的持仓标的"
fi

# ─── 10. 提示下一步 ─────────────────────────────────────────────
echo ""
echo "========================================"
echo "✅ 部署完成！"
echo ""
echo "📌 下一步："
echo ""
echo "  1. 配置 OpenClaw 主配置："
echo "     cp openclaw/openclaw.example.json ~/.openclaw/openclaw.json"
echo "     编辑 ~/.openclaw/openclaw.json，替换 Slack Token 和频道 ID"
echo ""
echo "  2. 创建 5 个 Slack 频道并邀请 Bot："
echo "     #invest-us-market → CIO"
echo "     #research         → Research"
echo "     #know             → KO"
echo "     #ops              → Ops"
echo "     #advisor          → Advisor（可选）"
echo ""
echo "  3. 配置 CIO 频道 ID："
echo "     编辑: $WORKSPACE/SOUL.md"
echo "     替换: RESEARCH_CHANNEL_ID / KO_CHANNEL_ID / CIO_CHANNEL_ID"
echo ""
echo "  4. 填写用户画像（推荐）："
echo "     编辑: $WORKSPACE/USER.md（风险偏好、通知频率等）"
echo ""
echo "  5. 配置你的持仓标的："
echo "     编辑: $WORKSPACE/watchlist/watchlist.yaml"
echo ""
echo "  6. 配置定时任务："
echo "     cp openclaw/cron/cron.example.json ~/.openclaw/cron/cron.json"
echo "     编辑 ~/.openclaw/cron/cron.json，替换频道 ID"
echo ""
echo "  7. 启动 OpenClaw："
echo "     openclaw gateway start"
echo ""
echo "  8. 测试："
echo "     python3 $WORKSPACE/scripts/stock_analysis.py AAPL"
echo "     在 Slack #invest-us-market 中 @CIO 测试"
echo ""
echo "  详细文档: docs/openclaw-setup.md"
echo ""
echo "🚀 开始你的美股 AI 投资之旅！"
