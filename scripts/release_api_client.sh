#!/bin/bash
# Script to release a new version of the API client

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current version
CURRENT_VERSION=$(cd packages/api-client && node -p "require('./package.json').version")

echo -e "${GREEN}📦 API Client Release Tool${NC}"
echo ""
echo "Current version: ${YELLOW}$CURRENT_VERSION${NC}"
echo ""
echo "Select version bump:"
echo "  1) Patch (bug fixes)       - $CURRENT_VERSION → $(cd packages/api-client && npm version patch --no-git-tag-version 2>/dev/null | sed 's/v//' && git checkout package.json 2>/dev/null)"
echo "  2) Minor (new features)    - $CURRENT_VERSION → $(cd packages/api-client && npm version minor --no-git-tag-version 2>/dev/null | sed 's/v//' && git checkout package.json 2>/dev/null)"
echo "  3) Major (breaking changes)- $CURRENT_VERSION → $(cd packages/api-client && npm version major --no-git-tag-version 2>/dev/null | sed 's/v//' && git checkout package.json 2>/dev/null)"
echo "  4) Custom version"
echo "  5) Cancel"
echo ""
read -p "Enter choice [1-5]: " choice

case $choice in
  1)
    VERSION_TYPE="patch"
    ;;
  2)
    VERSION_TYPE="minor"
    ;;
  3)
    VERSION_TYPE="major"
    ;;
  4)
    read -p "Enter custom version (e.g., 0.2.0): " CUSTOM_VERSION
    VERSION_TYPE="custom"
    ;;
  5)
    echo "Cancelled."
    exit 0
    ;;
  *)
    echo -e "${RED}Invalid choice${NC}"
    exit 1
    ;;
esac

# Bump version
if [ "$VERSION_TYPE" == "custom" ]; then
  NEW_VERSION=$CUSTOM_VERSION
  cd packages/api-client
  npm version $NEW_VERSION --no-git-tag-version
  cd ../..
else
  cd packages/api-client
  NEW_VERSION=$(npm version $VERSION_TYPE --no-git-tag-version | sed 's/v//')
  cd ../..
fi

echo ""
echo -e "${GREEN}✓${NC} Version bumped to ${YELLOW}$NEW_VERSION${NC}"
echo ""

# Generate client
echo -e "${YELLOW}Generating API client...${NC}"
make client-all || {
  echo -e "${RED}Failed to generate client${NC}"
  cd packages/api-client
  git checkout package.json
  cd ../..
  exit 1
}

echo ""
echo -e "${YELLOW}Building API client...${NC}"
cd packages/api-client
npm run build || {
  echo -e "${RED}Failed to build client${NC}"
  git checkout package.json
  cd ../..
  exit 1
}
cd ../..

echo ""
echo -e "${GREEN}✓${NC} Client generated successfully"
echo ""

sleep 2

# Confirm
echo "Ready to release version ${YELLOW}$NEW_VERSION${NC}"
echo ""
echo "This will:"
echo "  1. Commit the version bump"
echo "  2. Create and push tag: ${YELLOW}api-client-v$NEW_VERSION${NC}"
echo "  3. Trigger CI/CD to publish to GitHub Packages"
echo ""
read -p "Continue? [y/N]: " confirm

if [[ ! $confirm =~ ^[Yy]$ ]]; then
  echo "Cancelled. Reverting version bump..."
  cd packages/api-client
  git checkout package.json
  cd ../..
  exit 0
fi

# Commit and tag
git add packages/api-client

if git diff --cached --quiet; then
  echo -e "${RED}No changes to commit in packages/api-client.${NC}"
  echo "Canceling release to avoid tagging without a commit."
  exit 1
fi

git commit -m "chore(api-client): release v$NEW_VERSION"

TAG_NAME="api-client-v$NEW_VERSION"
git tag -a "$TAG_NAME" -m "Release API Client v$NEW_VERSION"

echo ""
echo -e "${GREEN}✓${NC} Created tag: ${YELLOW}$TAG_NAME${NC}"
echo ""

# Push
read -p "Push to remote? [y/N]: " push_confirm

if [[ $push_confirm =~ ^[Yy]$ ]]; then
  git push origin main
  git push origin "$TAG_NAME"
  
  echo ""
  echo -e "${GREEN}✓${NC} Pushed to remote"
  echo ""
  echo -e "${GREEN}🚀 Release in progress!${NC}"
  echo ""
  echo "Monitor the release at:"
  echo "  https://github.com/queroplantao/queroplantao-api/actions"
  echo ""
  echo "After publishing, install with:"
  echo -e "  ${YELLOW}npm install @cacenot/queroplantao-api-client@$NEW_VERSION${NC}"
else
  echo ""
  echo "Tag created locally. Push manually with:"
  echo -e "  ${YELLOW}git push origin main${NC}"
  echo -e "  ${YELLOW}git push origin $TAG_NAME${NC}"
fi
