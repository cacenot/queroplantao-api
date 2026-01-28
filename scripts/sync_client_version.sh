#!/usr/bin/env bash
# Script to sync CLIENT_VERSION constant with package.json version

set -euo pipefail

PACKAGE_JSON="packages/api-client/package.json"
INDEX_TS="packages/api-client/src/client/index.ts"

# Extract version from package.json
VERSION=$(grep '"version":' "$PACKAGE_JSON" | head -1 | sed 's/.*"version": "\(.*\)".*/\1/')

echo "📦 Package version: $VERSION"

# Update CLIENT_VERSION in index.ts
sed -i "s/export const CLIENT_VERSION = \".*\";/export const CLIENT_VERSION = \"$VERSION\";/" "$INDEX_TS"

echo "✅ Updated CLIENT_VERSION to $VERSION in $INDEX_TS"
