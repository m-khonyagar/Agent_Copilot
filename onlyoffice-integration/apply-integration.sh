#!/usr/bin/env bash
# apply-integration.sh
# ─────────────────────────────────────────────────────────────────────────────
# Applies the ONLYOFFICE integration to the Amline_namAvaran repository.
#
# Usage:
#   cd /path/to/Amline_namAvaran
#   bash /path/to/onlyoffice-integration/apply-integration.sh
#
# This script is IDEMPOTENT — running it multiple times is safe.
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AMLINE_ROOT="${1:-$(pwd)}"

echo "🔷 Amline root: $AMLINE_ROOT"
echo "🔷 Integration source: $SCRIPT_DIR"
echo ""

# ── Verify we are in the right directory ─────────────────────────────────────
if [[ ! -f "$AMLINE_ROOT/docker-compose.yml" ]]; then
  echo "❌ Error: $AMLINE_ROOT does not look like the Amline_namAvaran root."
  echo "   Please run from or pass the Amline_namAvaran directory."
  exit 1
fi

# ── Backend: copy new files ───────────────────────────────────────────────────
echo "📦 Copying backend files..."

cp "$SCRIPT_DIR/backend/app/services/onlyoffice.py" \
   "$AMLINE_ROOT/backend/backend/app/services/onlyoffice.py"
echo "  ✓ app/services/onlyoffice.py"

cp "$SCRIPT_DIR/backend/app/models/office_document.py" \
   "$AMLINE_ROOT/backend/backend/app/models/office_document.py"
echo "  ✓ app/models/office_document.py"

cp "$SCRIPT_DIR/backend/app/api/routes/onlyoffice_docs.py" \
   "$AMLINE_ROOT/backend/backend/app/api/routes/onlyoffice_docs.py"
echo "  ✓ app/api/routes/onlyoffice_docs.py"

# ── Backend: set down_revision in migration ──────────────────────────────────
LAST_REV=$(cd "$AMLINE_ROOT/backend/backend" && python -m alembic heads 2>/dev/null | head -1 | awk '{print $1}' || echo "")
MIGRATION_FILE="$AMLINE_ROOT/backend/backend/alembic/versions/20240407_add_office_documents.py"

if [[ ! -f "$MIGRATION_FILE" ]]; then
  cp "$SCRIPT_DIR/backend/alembic/versions/20240407_add_office_documents.py" "$MIGRATION_FILE"
  if [[ -n "$LAST_REV" ]]; then
    sed -i "s/^down_revision = None/down_revision = \"$LAST_REV\"/" "$MIGRATION_FILE"
    echo "  ✓ alembic migration (down_revision=$LAST_REV)"
  else
    echo "  ⚠️  alembic migration copied — please set down_revision manually"
  fi
else
  echo "  ℹ  alembic migration already exists, skipping"
fi

# ── Backend: replace config.py ───────────────────────────────────────────────
echo ""
echo "📝 Updating backend config.py..."
cp "$SCRIPT_DIR/backend/patches/config.py.full.py" \
   "$AMLINE_ROOT/backend/backend/app/core/config.py"
echo "  ✓ app/core/config.py"

# ── Backend: replace router.py ───────────────────────────────────────────────
echo "📝 Updating backend router.py..."
cp "$SCRIPT_DIR/backend/patches/router.py.full.py" \
   "$AMLINE_ROOT/backend/backend/app/api/router.py"
echo "  ✓ app/api/router.py"

# ── Frontend: copy new files ─────────────────────────────────────────────────
echo ""
echo "🎨 Copying frontend files..."

mkdir -p "$AMLINE_ROOT/admin-ui/src/components/DocumentEditor"
cp "$SCRIPT_DIR/admin-ui/src/components/DocumentEditor/DocumentEditor.tsx" \
   "$AMLINE_ROOT/admin-ui/src/components/DocumentEditor/DocumentEditor.tsx"
echo "  ✓ src/components/DocumentEditor/DocumentEditor.tsx"

mkdir -p "$AMLINE_ROOT/admin-ui/src/pages/office"
cp "$SCRIPT_DIR/admin-ui/src/pages/office/OfficePage.tsx" \
   "$AMLINE_ROOT/admin-ui/src/pages/office/OfficePage.tsx"
echo "  ✓ src/pages/office/OfficePage.tsx"

# ── Frontend: replace App.tsx and navigation.ts ───────────────────────────────
echo "📝 Updating frontend App.tsx..."
cp "$SCRIPT_DIR/admin-ui/patches/App.tsx.full.tsx" \
   "$AMLINE_ROOT/admin-ui/src/App.tsx"
echo "  ✓ src/App.tsx"

echo "📝 Updating frontend navigation.ts..."
cp "$SCRIPT_DIR/admin-ui/patches/navigation.ts.full.ts" \
   "$AMLINE_ROOT/admin-ui/src/config/navigation.ts"
echo "  ✓ src/config/navigation.ts"

# ── Environment variables ─────────────────────────────────────────────────────
echo ""
if ! grep -q "ONLYOFFICE_JWT_SECRET" "$AMLINE_ROOT/.env" 2>/dev/null; then
  echo "🔑 Adding ONLYOFFICE env vars to .env..."
  cat "$SCRIPT_DIR/docker/.env.onlyoffice.example" >> "$AMLINE_ROOT/.env"
  echo "  ✓ .env updated (remember to set ONLYOFFICE_JWT_SECRET!)"
else
  echo "  ℹ  ONLYOFFICE env vars already in .env, skipping"
fi

# ── Docker Compose ────────────────────────────────────────────────────────────
echo ""
echo "🐳 ONLYOFFICE Docker Compose service:"
echo "   To add the ONLYOFFICE service to your stack, either:"
echo "   a) Append the service block to docker-compose.yml manually (see docker/docker-compose.onlyoffice.yml)"
echo "   b) Use overlay: docker compose -f docker-compose.yml -f onlyoffice-integration/docker/docker-compose.onlyoffice.yml up -d"
echo ""

echo "✅ Integration files applied successfully!"
echo ""
echo "Next steps:"
echo "  1. Set ONLYOFFICE_JWT_SECRET in .env:  openssl rand -hex 32"
echo "  2. Add ONLYOFFICE service to docker-compose.yml"
echo "  3. Set down_revision in the Alembic migration if not done automatically"
echo "  4. Run: docker compose up -d --build && docker compose exec backend alembic upgrade head"
echo "  5. Open the admin panel → 📝 اسناد آفیس"
