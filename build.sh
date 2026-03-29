#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

usage() {
	echo "Usage: ./build.sh [python|rust]"
	exit 1
}

TARGET="${1:-}"

if [ -z "$TARGET" ]; then
	echo "Choose build target:"
	echo "1) python"
	echo "2) rust"
	read -r -p "Enter choice [1-2]: " CHOICE

	case "$CHOICE" in
		1|python)
			TARGET="python"
			;;
		2|rust)
			TARGET="rust"
			;;
		*)
			echo "Error: invalid choice."
			usage
			;;
	esac
fi

case "$TARGET" in
	python)
		if [ $# -gt 1 ]; then
			"$ROOT_DIR/build_py.sh" "${@:2}"
		else
			"$ROOT_DIR/build_py.sh"
		fi
		;;
	rust)
		if [ $# -gt 1 ]; then
			"$ROOT_DIR/build_rs.sh" "${@:2}"
		else
			"$ROOT_DIR/build_rs.sh"
		fi
		;;
	*)
		usage
		;;
esac
