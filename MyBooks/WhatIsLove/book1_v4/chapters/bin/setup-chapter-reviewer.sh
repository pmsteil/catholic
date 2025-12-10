#!/bin/bash
# Setup script for chapter-reviewer
# Installs uv if not already installed

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "✟ Setting up Chapter Reviewer..."
echo

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "📦 uv not found, installing..."
    echo

    # Install uv
    curl -LsSf https://astral.sh/uv/install.sh | sh

    if [ $? -ne 0 ]; then
        echo "❌ Failed to install uv"
        echo "Please install uv manually: https://docs.astral.sh/uv/"
        exit 1
    fi

    # Source the shell profile to get uv in PATH
    if [ -f "$HOME/.cargo/env" ]; then
        source "$HOME/.cargo/env"
    fi

    echo
fi

# Verify uv is now available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is still not available after installation"
    echo "Please restart your shell or run: source ~/.cargo/env"
    exit 1
fi

echo "✓ uv is installed"
echo

# Test the script (this will auto-install dependencies via uv)
echo "🧪 Testing chapter-reviewer script..."
"$SCRIPT_DIR/chapter-reviewer.py" --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo
    echo "✓ Setup complete!"
    echo
    echo "Usage examples:"
    echo "  $SCRIPT_DIR/chapter-reviewer.py CCCR"
    echo "  $SCRIPT_DIR/chapter-reviewer.py DOCTRINE"
    echo "  $SCRIPT_DIR/chapter-reviewer.py SCRIBE"
    echo
    echo "Note: Dependencies will be automatically managed by uv"
    echo
else
    echo "⚠ Script test failed, but uv is installed"
    echo "Dependencies will be installed automatically on first run"
fi
