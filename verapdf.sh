#!/usr/bin/env bash
# Run veraPDF against a PDF file using the local Docker image.
#
# Usage:
#   ./verapdf.sh <file.pdf> [extra veraPDF args...]
#
# Examples:
#   ./verapdf.sh out.pdf --flavour ua1
#   ./verapdf.sh out.pdf --flavour ua1 --format text

set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: $0 <file.pdf> [extra veraPDF args...]"
    exit 1
fi

PDF="$1"; shift
PDF_ABS="$(cd "$(dirname "$PDF")" && pwd)/$(basename "$PDF")"
PDF_DIR="$(dirname "$PDF_ABS")"
PDF_NAME="$(basename "$PDF_ABS")"

# Build the image if it doesn't exist yet
if ! docker image inspect verapdf &>/dev/null; then
    echo "Building veraPDF Docker image (first run only)..."
    docker build -t verapdf "$(dirname "$0")/docker/verapdf"
fi

docker run --rm \
    -v "$PDF_DIR":/data \
    verapdf \
    --flavour ua1 \
    "/data/$PDF_NAME" \
    "$@"
