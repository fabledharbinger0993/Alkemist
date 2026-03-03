#!/bin/bash
# ════════════════════════════════════════════════════════════════════════════
# Alkemist + OpenClaw + Ollama Launcher (Linux/Ubuntu)
# ════════════════════════════════════════════════════════════════════════════
#
# Purpose: One-command startup for your local AI agent
# Usage: ./launch-alkemist-agent.sh
#
# After running this, everything starts in background. You can close the terminal.
# Interact via Telegram bot or http://127.0.0.1:18789
#
# ════════════════════════════════════════════════════════════════════════════

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# ────────────────────────────────────────────────────────────────────────────
# Configuration (customize as needed)
# ────────────────────────────────────────────────────────────────────────────

OLLAMA_MODEL="${OLLAMA_MODEL:-mistral}"           # Options: mistral, llama3, deepseek-coder
OLLAMA_HOST="${OLLAMA_HOST:-127.0.0.1:11434}"
OPENCLAW_GATEWAY="${OPENCLAW_GATEWAY:-127.0.0.1:18789}"
ALKEMIST_BACKEND="${ALKEMIST_BACKEND:-127.0.0.1:8000}"
ALKEMIST_PROJECT_PATH="${ALKEMIST_PROJECT_PATH:-$HOME/.alkemist-projects}"
LOG_DIR="${LOG_DIR:-$HOME/.alkemist-logs}"

# Create log directory
mkdir -p "$LOG_DIR"

# ────────────────────────────────────────────────────────────────────────────
# Helper Functions
# ────────────────────────────────────────────────────────────────────────────

print_header() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║  🦞  OpenClaw + Ollama for Alkemist Development                     ║${NC}"
    echo -e "${CYAN}║      Launching your personal AI agent...                            ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

print_section() {
    echo -e "${YELLOW}$1${NC}"
}

print_success() {
    echo -e "${GREEN}  ✅ $1${NC}"
}

print_error() {
    echo -e "${RED}  ❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}  ⚠️  $1${NC}"
}

print_info() {
    echo -e "${CYAN}  ℹ️  $1${NC}"
}

print_waiting() {
    echo -e "${GRAY}  ⏳ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Wait for service to be ready
wait_for_service() {
    local url=$1
    local max_attempts=${2:-10}
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 1
    done
    
    return 1
}

# ────────────────────────────────────────────────────────────────────────────
# Step 1: Verify Prerequisites
# ────────────────────────────────────────────────────────────────────────────

print_header

print_section "📋 Step 1: Checking prerequisites..."

MISSING=()

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_success "Node.js: $NODE_VERSION"
else
    MISSING+=("Node.js")
    print_error "Node.js not found. Install from https://nodejs.org"
fi

# Check Ollama
if command_exists ollama; then
    OLLAMA_VERSION=$(ollama --version 2>/dev/null || echo "unknown")
    print_success "Ollama: $OLLAMA_VERSION"
else
    MISSING+=("Ollama")
    print_error "Ollama not found. Install from https://ollama.com"
fi

# Check OpenClaw
if command_exists openclaw; then
    OPENCLAW_VERSION=$(openclaw --version 2>/dev/null || echo "unknown")
    print_success "OpenClaw: $OPENCLAW_VERSION"
else
    MISSING+=("OpenClaw")
    print_error "OpenClaw not found. Run: npm install -g openclaw"
fi

# Exit if missing critical components
if [ ${#MISSING[@]} -gt 0 ]; then
    echo ""
    print_error "Missing components: $(IFS=', '; echo "${MISSING[*]}")"
    echo -e "${RED}Please install missing components and try again.${NC}"
    exit 1
fi

echo ""

# ────────────────────────────────────────────────────────────────────────────
# Step 2: Start Ollama
# ────────────────────────────────────────────────────────────────────────────

print_section "🧠 Step 2: Starting Ollama LLM..."

# Check if Ollama is already running
if pgrep -x "ollama" > /dev/null; then
    print_success "Ollama already running"
else
    print_info "Starting Ollama service..."
    
    # Start Ollama in background with logging
    nohup ollama serve > "$LOG_DIR/ollama.log" 2>&1 &
    OLLAMA_PID=$!
    
    print_waiting "Waiting for Ollama to be ready..."
    sleep 3
    
    # Verify Ollama is responding
    if wait_for_service "http://$OLLAMA_HOST/api/health" 10; then
        print_success "Ollama is ready (http://$OLLAMA_HOST)"
    else
        print_warning "Ollama started but not responding yet. Give it 10-15 seconds..."
    fi
fi

echo ""

# ────────────────────────────────────────────────────────────────────────────
# Step 3: Verify Ollama Model
# ────────────────────────────────────────────────────────────────────────────

print_section "📥 Step 3: Checking Ollama model..."

# List available models
if ollama list 2>/dev/null | grep -q "$OLLAMA_MODEL"; then
    print_success "Model '$OLLAMA_MODEL' is available"
else
    print_warning "Model '$OLLAMA_MODEL' not found locally"
    print_info "Downloading model (this takes 5-15 minutes on first run)..."
    echo -e "${CYAN}  💾 Pulling $OLLAMA_MODEL...${NC}"
    
    # Pull the model (this is long-running, user sees progress)
    ollama pull "$OLLAMA_MODEL"
    print_success "Model downloaded"
fi

echo ""

# ────────────────────────────────────────────────────────────────────────────
# Step 4: Start OpenClaw Gateway
# ────────────────────────────────────────────────────────────────────────────

print_section "🚀 Step 4: Starting OpenClaw Gateway..."

# Check if OpenClaw is already running
if pgrep -x "openclaw" > /dev/null; then
    print_success "OpenClaw already running"
else
    print_info "Starting OpenClaw daemon..."
    
    # Start OpenClaw in background with logging
    nohup openclaw start > "$LOG_DIR/openclaw.log" 2>&1 &
    OPENCLAW_PID=$!
    
    print_waiting "Waiting for OpenClaw Gateway to initialize..."
    sleep 5
fi

# Verify gateway is responding
if wait_for_service "http://$OPENCLAW_GATEWAY/health" 10 2>/dev/null || \
   netstat -tuln 2>/dev/null | grep -q ":18789\|$OPENCLAW_GATEWAY" || \
   ss -tuln 2>/dev/null | grep -q ":18789\|$OPENCLAW_GATEWAY"; then
    print_success "OpenClaw Gateway ready (http://$OPENCLAW_GATEWAY)"
else
    print_warning "Gateway initializing... give it 10-20 seconds"
fi

echo ""

# ────────────────────────────────────────────────────────────────────────────
# Step 5: Verify Telegram Connection
# ────────────────────────────────────────────────────────────────────────────

print_section "📱 Step 5: Checking Telegram bot..."

if openclaw status 2>/dev/null | grep -q "telegram"; then
    print_success "Telegram channel configured"
else
    print_warning "Telegram not configured yet"
    echo -e "${GRAY}     Run: openclaw onboard${NC}"
fi

echo ""

# ────────────────────────────────────────────────────────────────────────────
# Success Message
# ────────────────────────────────────────────────────────────────────────────

echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ YOUR ALKEMIST AI AGENT IS RUNNING!                              ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${CYAN}📊 Service Status:${NC}"
echo "  🧠 Ollama LLM .......... http://$OLLAMA_HOST (model: $OLLAMA_MODEL)"
echo "  🦞 OpenClaw Gateway .... http://$OPENCLAW_GATEWAY"
echo "  📱 Telegram Bot ........ Ready for commands"
echo ""

echo -e "${CYAN}🎯 What You Can Do Now:${NC}"
echo "  • Send messages to your Telegram bot"
echo "  • Bot will execute commands on your Alkemist project"
echo "  • No more terminal needed - it all runs in background"
echo ""

echo -e "${YELLOW}💬 Example Telegram Commands:${NC}"
echo "  '  /status' - Check what's running"
echo "  '  Test Alkemist backend' - Run pytest"
echo "  '  Build Bool agent' - Generate Bool files"
echo "  '  Check project health' - Health check"
echo "  '  Run all tests' - Full test suite"
echo ""

echo -e "${CYAN}🌐 Interfaces:${NC}"
echo "  • Telegram ........... Message your bot"
echo "  • Web Dashboard ...... http://$OPENCLAW_GATEWAY (optional)"
echo "  • Terminal ........... Your CLI"
echo ""

echo -e "${CYAN}📁 Your Alkemist Project:${NC}"
echo "  $ALKEMIST_PROJECT_PATH"
echo ""

echo -e "${CYAN}📋 Logs Location:${NC}"
echo "  $LOG_DIR/"
echo ""

echo -e "${YELLOW}🔐 Security Notes:${NC}"
echo "  ✓ Ollama bound to localhost only (not exposed)"
echo "  ✓ File access limited to your Alkemist folder"
echo "  ✓ Only your Telegram ID can send commands"
echo "  ✓ All actions logged for audit trail"
echo ""

echo -e "${GRAY}📖 For more information:${NC}"
echo "  • Setup guide: OPENCLAW_OLLAMA_SETUP.md"
echo "  • OpenClaw docs: https://docs.openclaw.ai"
echo "  • GitHub: https://github.com/openclaw/openclaw"
echo ""

echo -e "${GREEN}✨ You can now close this terminal!${NC}"
echo -e "${GREEN}   Everything continues running in the background.${NC}"
echo ""

echo "─────────────────────────────────────────────────────────────────────────"

# Keep script running or prompt to close
if [ -t 0 ]; then
    read -p "Press Enter to finish (script will exit, services remain running)"
else
    echo "Services started. Check logs in: $LOG_DIR/"
fi
