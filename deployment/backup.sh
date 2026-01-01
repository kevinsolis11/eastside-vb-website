#!/bin/bash
# Backup script for Eastside VB Website
# Usage: ./deployment/backup.sh [--compress] [--upload-s3]
# Called by: systemd timer (backup.timer)

set -e

APP_ROOT="${APP_ROOT:-/home/volleyball/eastside-vb-website}"
BACKUP_DIR="${BACKUP_DIR:-$APP_ROOT/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
COMPRESS="${1:-false}"
UPLOAD_S3="${2:-false}"

mkdir -p "$BACKUP_DIR"
cd "$APP_ROOT"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP"

echo "Starting backup at $(date)"
echo "Backup directory: $BACKUP_DIR"
echo ""

# Step 1: Backup database
echo "1. Backing up database..."
if [ -f "volleyball_site/db.sqlite3" ]; then
  mkdir -p "$BACKUP_DIR/database"
  cp volleyball_site/db.sqlite3 "$BACKUP_DIR/database/db_$TIMESTAMP.sqlite3"
  echo "   ✓ Database backed up"
else
  echo "   ⚠ SQLite database not found (may be using external DB)"
fi

# Step 2: Backup media files
if [ -d "volleyball_site/media" ] && [ "$(ls -A volleyball_site/media)" ]; then
  echo "2. Backing up media files..."
  mkdir -p "$BACKUP_DIR/media"
  tar czf "$BACKUP_DIR/media/media_$TIMESTAMP.tar.gz" volleyball_site/media/
  echo "   ✓ Media files backed up"
else
  echo "2. No media files to backup"
fi

# Step 3: Backup static files (optional - can be regenerated)
echo "3. Backing up settings..."
mkdir -p "$BACKUP_DIR/config"
cp volleyball_site/settings.py "$BACKUP_DIR/config/settings_$TIMESTAMP.py" || true
echo "   ✓ Settings backed up"

# Step 4: Create backup manifest
echo "4. Creating backup manifest..."
MANIFEST="$BACKUP_DIR/manifest_$TIMESTAMP.txt"
cat > "$MANIFEST" <<EOF
Backup Timestamp: $TIMESTAMP
Backup Date: $(date)
App Root: $APP_ROOT

Contents:
- database/db_$TIMESTAMP.sqlite3
- media/media_$TIMESTAMP.tar.gz
- config/settings_$TIMESTAMP.py

Database Size: $(du -sh volleyball_site/db.sqlite3 2>/dev/null || echo "N/A")
Media Size: $(du -sh volleyball_site/media 2>/dev/null || echo "N/A")
Total Backup Size: $(du -sh $BACKUP_DIR 2>/dev/null | tail -1)

Retention: Backups older than $RETENTION_DAYS days will be deleted
EOF
echo "   ✓ Manifest created"

# Step 5: Compress backup directory (optional)
if [ "$COMPRESS" = "true" ]; then
  echo "5. Compressing backup..."
  tar czf "$BACKUP_FILE.tar.gz" -C "$BACKUP_DIR" database/ media/ config/ manifest_$TIMESTAMP.txt
  rm -rf "$BACKUP_DIR/database" "$BACKUP_DIR/media" "$BACKUP_DIR/config" "$MANIFEST"
  echo "   ✓ Backup compressed to $(du -h $BACKUP_FILE.tar.gz | cut -f1)"
fi

# Step 6: Upload to S3 (optional, requires AWS CLI)
if [ "$UPLOAD_S3" = "true" ]; then
  if command -v aws >/dev/null 2>&1; then
    echo "6. Uploading to S3..."
    S3_BUCKET="${S3_BUCKET:-volleyball-site-backups}"
    if [ -f "$BACKUP_FILE.tar.gz" ]; then
      aws s3 cp "$BACKUP_FILE.tar.gz" "s3://$S3_BUCKET/backups/" || echo "   ⚠ S3 upload failed"
    else
      aws s3 cp "$BACKUP_DIR" "s3://$S3_BUCKET/backups/$TIMESTAMP/" --recursive || echo "   ⚠ S3 upload failed"
    fi
    echo "   ✓ Backup uploaded to S3"
  else
    echo "   ⚠ AWS CLI not installed, skipping S3 upload"
  fi
fi

# Step 7: Cleanup old backups
echo "7. Cleaning up old backups (older than $RETENTION_DAYS days)..."
find "$BACKUP_DIR" -maxdepth 2 -type f -mtime +$RETENTION_DAYS -delete
echo "   ✓ Old backups removed"

# Step 8: Verify backup integrity
echo "8. Verifying backup..."
if [ -f "volleyball_site/db.sqlite3" ] && [ -f "$BACKUP_DIR/database/db_$TIMESTAMP.sqlite3" ]; then
  DB_SIZE_ORIGINAL=$(stat -f%z "volleyball_site/db.sqlite3" 2>/dev/null || stat -c%s "volleyball_site/db.sqlite3" 2>/dev/null || echo "unknown")
  DB_SIZE_BACKUP=$(stat -f%z "$BACKUP_DIR/database/db_$TIMESTAMP.sqlite3" 2>/dev/null || stat -c%s "$BACKUP_DIR/database/db_$TIMESTAMP.sqlite3" 2>/dev/null || echo "unknown")
  if [ "$DB_SIZE_ORIGINAL" = "$DB_SIZE_BACKUP" ]; then
    echo "   ✓ Database backup verified"
  else
    echo "   ⚠ Database backup size mismatch: $DB_SIZE_ORIGINAL vs $DB_SIZE_BACKUP"
  fi
fi

echo ""
echo "Backup complete at $(date)"
echo "Backup location: $BACKUP_DIR"
