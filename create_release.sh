#!/bin/bash
# GitHub Release automation script

VERSION="v2.1.0"
RELEASE_NAME="Chess AI v2.1.0 - Eury Engine"
ZIP_FILE="ChessAI-Portable-v2.1.zip"

echo "🚀 Creating GitHub Release $VERSION"
echo "=================================================="

# Step 1: Commit changes
echo "📝 Committing changes..."
git add .
git commit -m "Release $VERSION - Analysis Mode + Lichess UI" || true

# Step 2: Push to main
echo "⬆️  Pushing to GitHub..."
git push origin main

# Step 3: Create and push tag
echo "🏷️  Creating tag $VERSION..."
git tag -a $VERSION -m "$RELEASE_NAME" -f
git push origin $VERSION -f

echo ""
echo "✅ Git setup complete!"
echo ""
echo "📋 Next steps (manual):"
echo "1. Go to: https://github.com/Eurus-Infosec/chess-ai/releases/new"
echo "2. Choose tag: $VERSION"
echo "3. Title: $RELEASE_NAME"
echo "4. Upload: $ZIP_FILE"
echo "5. Copy description from RELEASE_NOTES.md"
echo "6. Click 'Publish release'"
echo ""
echo "💡 Or use GitHub CLI (if installed):"
echo "   gh release create $VERSION $ZIP_FILE --title \"$RELEASE_NAME\" --notes-file RELEASE_NOTES.md"
