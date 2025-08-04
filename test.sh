LAST_TAG=$(git describe --tags --abbrev=0 HEAD 2>/dev/null || echo "")
LAST_TAG="v1.1.40"


if [ -n "$LAST_TAG" ]; then
  # Get commits since last tag
  CHANGELOG=$(git log --oneline --no-merges "${LAST_TAG}..HEAD" | head -10)
  if [ -z "$CHANGELOG" ]; then
    CHANGELOG="No changes since last release"
  fi
else
  # If no tags exist, get last 10 commits
  CHANGELOG=$(git log --oneline --no-merges -10)
fi

# Ensure we have some content
if [ -z "$CHANGELOG" ]; then
  CHANGELOG="No changes detected"
fi

# Pass changelog with actual newlines
echo "changelog<<EOF"
echo "$CHANGELOG"
echo "EOF"
echo "📝 Changelog generated from ${LAST_TAG:-'beginning'} to HEAD"

echo "Raw changelog:"
echo "$CHANGELOG"