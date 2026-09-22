#!/usr/bin/env bash
set -euo pipefail
REPO_URL="${EDUARDOOS_EOSCHOOL_URL:-https://github.com/EduardoOsteicoechea/eduardoos-eoschool-connector.git}"
ROOT="$(pwd)"
TARGET="$ROOT/.eoschool"
SKILL_SRC="$TARGET/skill/eoschool"
SKILL_DST="$ROOT/.cursor/skills/eoschool"

if [[ -e "$TARGET" && ! -d "$TARGET/.git" ]]; then
  echo "Refusing: $TARGET exists and is not a git clone." >&2
  exit 1
fi

if [[ -d "$TARGET/.git" ]]; then
  git -C "$TARGET" pull --ff-only || true
else
  git clone --depth 1 "$REPO_URL" "$TARGET"
fi

mkdir -p "$ROOT/.cursor/skills"
rm -rf "$SKILL_DST"
cp -R "$SKILL_SRC" "$SKILL_DST"

if [[ ! -f "$TARGET/.env" && -f "$TARGET/.env.example" ]]; then
  cp "$TARGET/.env.example" "$TARGET/.env"
  echo "Created $TARGET/.env â€” add your API key (UI only at eduardoos.com)."
fi

echo "Installed connector at $TARGET"
echo "Cursor skill at $SKILL_DST (name: eoschool)"
echo "Read $SKILL_SRC/CAVEATS.md before posting materials."

