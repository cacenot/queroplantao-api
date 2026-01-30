#!/bin/bash
# GitHub Copilot MCP Configuration Script
# This script helps configure GitHub Copilot to use the Quero Plantão MCP server

set -e

echo "🚀 GitHub Copilot MCP Configuration"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src/queroplantao_mcp" ]; then
    echo "❌ Error: Please run this script from the packages/mcp-server directory"
    exit 1
fi

# Get the absolute path
MCP_DIR="$(pwd)"
PROJECT_DIR="$(dirname "$(dirname "$MCP_DIR")")"

echo "📍 Detected paths:"
echo "   MCP Server: $MCP_DIR"
echo "   Project: $PROJECT_DIR"
echo ""

# Check if .env exists and has API key
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found. Run 'make setup' first."
    exit 1
fi

if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY not found in .env file."
    echo "   Please add your OpenAI API key to .env before continuing."
    echo ""
fi

# Generate the configuration
CONFIG_FILE="github-copilot-config-generated.json"

cat > "$CONFIG_FILE" << EOF
{
  "github.copilot.chat.mcp": {
    "queroplantao-api": {
      "command": "uv",
      "args": [
        "run",
        "--project",
        "$MCP_DIR",
        "mcp-server"
      ],
      "env": {
        "OPENAI_API_KEY": "$(grep '^OPENAI_API_KEY=' .env | cut -d'=' -f2- || echo 'sk-your-openai-api-key-here')",
        "MCP_LLM_MODEL": "$(grep MCP_LLM_MODEL .env | cut -d'=' -f2 || echo 'gpt-4o-mini')",
        "MCP_LLM_TEMPERATURE": "$(grep MCP_LLM_TEMPERATURE .env | cut -d'=' -f2 || echo '0.1')",
        "MCP_LLM_MAX_TOKENS": "$(grep MCP_LLM_MAX_TOKENS .env | cut -d'=' -f2 || echo '4096')"
      }
    }
  }
}
EOF

echo "✅ Generated configuration file: $CONFIG_FILE"
echo ""
echo "📋 Next steps:"
echo ""
echo "1. Open VS Code settings (Ctrl/Cmd + Shift + P → 'Preferences: Open Settings (JSON)')"
echo ""
echo "2. Copy the contents of $CONFIG_FILE and paste into your settings.json"
echo ""
echo "3. Restart VS Code completely"
echo ""
echo "4. Open GitHub Copilot Chat and ask: 'What MCP servers do you have access to?'"
echo ""
echo "📄 Configuration preview:"
echo "------------------------"
cat "$CONFIG_FILE"
echo ""
echo "🎯 Test commands you can try:"
echo "   • 'Show me all screening endpoints'"
echo "   • 'What are the business rules for professionals?'"
echo "   • 'Generate a checklist for implementing a screening form'"
echo "   • 'Explain the ScreeningProcess state machine'"
echo ""
echo "📚 For more information, see the README.md file."