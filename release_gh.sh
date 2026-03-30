#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RELEASE_DIR="$ROOT_DIR/release"
ZIP_PATH="$RELEASE_DIR/dot_note.zip"
VERSION_FILE="$ROOT_DIR/VERSION"

# Read version
if [ ! -f "$VERSION_FILE" ]; then
	echo "Error: VERSION file not found."
	exit 1
fi
VERSION="v$(cat "$VERSION_FILE" | tr -d '[:space:]')"

# Check zip exists
if [ ! -f "$ZIP_PATH" ]; then
	echo "Error: $ZIP_PATH not found. Run release.sh first."
	exit 1
fi

# Check gh is available
if ! command -v gh &>/dev/null; then
	echo "Error: GitHub CLI (gh) is not installed. Install it from https://cli.github.com"
	exit 1
fi

echo "Ready to publish release:"
echo "  Tag:    $VERSION"
echo "  Asset:  $ZIP_PATH"
echo ""
read -r -p "Publish to GitHub? [Y/n]: " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
	echo "Aborted."
	exit 0
fi

# Create tag and GitHub release, upload zip
gh release create "$VERSION" "$ZIP_PATH" \
	--title "$VERSION" \
	--notes "Release $VERSION"

echo "Published release $VERSION with $ZIP_PATH"
