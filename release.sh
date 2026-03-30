#!/bin/bash

set -euo pipefail

# Clear previous release artifacts
rm -rf release/
echo "Cleared previous release artifacts."

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
RELEASE_DIR="$ROOT_DIR/release"

# Create release folders
mkdir -p "$RELEASE_DIR/python"
mkdir -p "$RELEASE_DIR/rust"

# Build Python binaries and move to release/python
echo "Building Python..."
"$ROOT_DIR/build_py.sh"
mv "$ROOT_DIR/note" "$RELEASE_DIR/python/note"
if [ -d "$ROOT_DIR/_internal" ]; then
	mv "$ROOT_DIR/_internal" "$RELEASE_DIR/python/_internal"
fi
echo "Python binaries moved to $RELEASE_DIR/python"

# Build Rust binaries and move to release/rust
echo "Building Rust..."
"$ROOT_DIR/build_rs.sh"
mv "$ROOT_DIR/note" "$RELEASE_DIR/rust/note"
echo "Rust binaries moved to $RELEASE_DIR/rust"

echo "Release complete: $RELEASE_DIR"

# Copy install/uninstall scripts to python and rust folders
cp "$ROOT_DIR/install.sh" "$RELEASE_DIR/python/install.sh"
cp "$ROOT_DIR/uninstall.sh" "$RELEASE_DIR/python/uninstall.sh"
chmod +x "$RELEASE_DIR/python/install.sh" "$RELEASE_DIR/python/uninstall.sh"
echo "Copied install.sh and uninstall.sh to $RELEASE_DIR/python"

cp "$ROOT_DIR/install.sh" "$RELEASE_DIR/rust/install.sh"
cp "$ROOT_DIR/uninstall.sh" "$RELEASE_DIR/rust/uninstall.sh"
chmod +x "$RELEASE_DIR/rust/install.sh" "$RELEASE_DIR/rust/uninstall.sh"
echo "Copied install.sh and uninstall.sh to $RELEASE_DIR/rust"

# Copy documentation and license files to both python and rust folders
cp "$ROOT_DIR/doc/installation/README.txt" "$RELEASE_DIR/python/README.txt"
cp "$ROOT_DIR/LICENSE" "$RELEASE_DIR/python/LICENSE"
echo "Copied README.txt and LICENSE to $RELEASE_DIR/python"

cp "$ROOT_DIR/doc/installation/README.txt" "$RELEASE_DIR/rust/README.txt"
cp "$ROOT_DIR/LICENSE" "$RELEASE_DIR/rust/LICENSE"
echo "Copied README.txt and LICENSE to $RELEASE_DIR/rust"

VERSION="$(cat "$ROOT_DIR/VERSION" | tr -d '[:space:]')"
PYTHON_ZIP_NAME="dot_note_python_v${VERSION}.zip"
RUST_ZIP_NAME="dot_note_rust_v${VERSION}.zip"
PYTHON_ZIP_PATH="$RELEASE_DIR/$PYTHON_ZIP_NAME"
RUST_ZIP_PATH="$RELEASE_DIR/$RUST_ZIP_NAME"

for f in "$RELEASE_DIR/$PYTHON_ZIP_NAME" "$ROOT_DIR/$PYTHON_ZIP_NAME" \
          "$RELEASE_DIR/$RUST_ZIP_NAME" "$ROOT_DIR/$RUST_ZIP_NAME"; do
	[ -f "$f" ] && rm -f "$f"
done

cd "$RELEASE_DIR"
zip -r -9 "$ROOT_DIR/$PYTHON_ZIP_NAME" "python"
mv "$ROOT_DIR/$PYTHON_ZIP_NAME" "$PYTHON_ZIP_PATH"
echo "Created archive: $PYTHON_ZIP_PATH"

zip -r -9 "$ROOT_DIR/$RUST_ZIP_NAME" "rust"
mv "$ROOT_DIR/$RUST_ZIP_NAME" "$RUST_ZIP_PATH"
echo "Created archive: $RUST_ZIP_PATH"

"$ROOT_DIR/release_gh.sh" "v${VERSION}" "$PYTHON_ZIP_PATH" "$RUST_ZIP_PATH"
