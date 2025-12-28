# 🛠️ Maintenance Tools Guide

This guide covers the maintenance and management tools for AI Avatar Studio.

---

## 📋 Overview

Three powerful utilities for managing your Avatar Studio:

1. **maintenance.py** - Unified maintenance interface
2. **backup_manager.py** - Backup and restore
3. **cleanup_manager.py** - Disk space management

---

## 🔧 Maintenance Tool (Recommended)

The **maintenance.py** script provides a single interface for all operations.

### Quick Commands

```bash
# Check system health
python maintenance.py diagnose

# Show current status
python maintenance.py status

# Create backup
python maintenance.py backup

# Clean old files (30+ days)
python maintenance.py cleanup --days 30

# Preview cleanup (don't delete)
python maintenance.py cleanup --dry-run

# Optimize system
python maintenance.py optimize
```

### Detailed Usage

#### 1. System Diagnostics

Check if everything is working correctly:

```bash
python maintenance.py diagnose
```

**Checks:**
- ✅ Python version
- ✅ FFmpeg availability
- ✅ Disk space
- ✅ RAM
- ✅ Database connectivity
- ✅ Disk usage by category
- ✅ Large files

**Output Example:**
```
🔍 Running System Diagnostics...

PYTHON: ✅ OK (3.10.0)
FFMPEG: ✅ OK
DISK_SPACE: ✅ OK (150.5 GB available)
RAM: ✅ OK (12.3 GB available)
DATABASE: ✅ OK (15 projects, 42 generations)

Overall Status: ✅ HEALTHY
```

#### 2. System Status

Quick overview of current state:

```bash
python maintenance.py status
```

**Shows:**
- Database statistics (projects, generations, success rate)
- Disk usage breakdown
- Available resources
- Latest backup information

#### 3. Backup

Create a complete backup:

```bash
# Basic backup (database + config + videos)
python maintenance.py backup

# Include AI models (adds ~400 MB)
python maintenance.py backup --models

# Exclude videos (faster, smaller)
python maintenance.py backup --no-output
```

**Backup Contents:**
- Database (projects.db)
- Configuration files (.env)
- Generated videos (optional)
- AI models (optional)

**Backup Location:** `./backups/avatar_backup_YYYYMMDD_HHMMSS.zip`

#### 4. Restore

Restore from a previous backup:

```bash
python maintenance.py restore backups/avatar_backup_20251222_143000.zip
```

**Warning:** This overwrites current data. Current files are backed up automatically.

#### 5. Cleanup

Remove old files to free disk space:

```bash
# Clean files older than 30 days
python maintenance.py cleanup --days 30

# Preview what would be deleted (safe)
python maintenance.py cleanup --dry-run

# Clean files older than 7 days
python maintenance.py cleanup --days 7
```

**Cleans:**
- Old videos (30+ days)
- Failed generation files
- Temporary files
- Cache files
- Old log files

#### 6. Optimize

Optimize for best performance:

```bash
python maintenance.py optimize
```

**Performs:**
- Cleans temp files
- Clears cache
- Optimizes database (VACUUM)
- Removes old logs

**Recommended:** Run weekly or after many generations.

---

## 💾 Backup Manager (Advanced)

Direct access to backup operations.

### Create Backup

```bash
# Basic backup
python utils/backup_manager.py create

# Include models
python utils/backup_manager.py create --models

# No compression (faster)
python utils/backup_manager.py create --compression none
```

### List Backups

```bash
python utils/backup_manager.py list
```

**Output:**
```
📦 Found 3 backup(s):

  • avatar_backup_20251222_143000
    Size: 1250.45 MB
    Created: 2025-12-22T14:30:00
    Compressed: Yes
```

### Restore Backup

```bash
# Full restore
python utils/backup_manager.py restore backups/avatar_backup_20251222_143000.zip

# Restore only database
python utils/backup_manager.py restore backup.zip --no-config --no-output

# Restore including models
python utils/backup_manager.py restore backup.zip --models
```

### Delete Backup

```bash
python utils/backup_manager.py delete avatar_backup_20251222_143000
```

### Cleanup Old Backups

```bash
# Keep only 5 most recent
python utils/backup_manager.py cleanup --keep 5

# Keep only 3 most recent
python utils/backup_manager.py cleanup --keep 3
```

---

## 🧹 Cleanup Manager (Advanced)

Direct access to cleanup operations.

### Analyze Disk Usage

```bash
python utils/cleanup_manager.py analyze
```

**Output:**
```
📊 Analyzing disk usage...

Total Size: 3456.78 MB

Breakdown by category:

  OUTPUT:
    Path: ./output
    Size: 2100.50 MB
    Files: 45
    Videos: 42
  
  MODELS:
    Path: ./models
    Size: 400.25 MB
    Models: 3
  
  TEMP:
    Path: ./temp
    Size: 50.10 MB
    Files: 123
```

### Clean Old Videos

```bash
# Remove videos older than 30 days
python utils/cleanup_manager.py videos --days 30

# Preview only
python utils/cleanup_manager.py videos --days 30 --dry-run

# Remove videos older than 7 days
python utils/cleanup_manager.py videos --days 7
```

### Clean Failed Generations

```bash
python utils/cleanup_manager.py failed

# Preview only
python utils/cleanup_manager.py failed --dry-run
```

### Clean Temp Files

```bash
python utils/cleanup_manager.py temp
```

### Clean Cache Files

```bash
python utils/cleanup_manager.py cache
```

### Clean Old Logs

```bash
# Remove logs older than 30 days
python utils/cleanup_manager.py logs --days 30

# Remove logs older than 7 days
python utils/cleanup_manager.py logs --days 7
```

### Clean Everything

```bash
# Clean all categories
python utils/cleanup_manager.py all --days 30

# Preview everything that would be deleted
python utils/cleanup_manager.py all --dry-run
```

### Find Large Files

```bash
# Find files > 100 MB
python utils/cleanup_manager.py large --min-size 100

# Find files > 500 MB
python utils/cleanup_manager.py large --min-size 500

# Include models in search
python utils/cleanup_manager.py large --include-models
```

---

## 📅 Recommended Maintenance Schedule

### Daily (Automated)

```bash
# Quick cleanup
python maintenance.py optimize
```

### Weekly

```bash
# Full diagnostics
python maintenance.py diagnose

# Create backup
python maintenance.py backup

# Clean old files
python maintenance.py cleanup --days 30
```

### Monthly

```bash
# Full backup with models
python maintenance.py backup --models

# Deep cleanup
python maintenance.py cleanup --days 7

# Check for large files
python utils/cleanup_manager.py large --min-size 500
```

---

## 🔄 Automation Examples

### Windows Task Scheduler

Create a batch file `daily_maintenance.bat`:

```batch
@echo off
cd "C:\Path\To\AI  Avatar  talking"
python maintenance.py optimize
python maintenance.py backup --no-output
```

Schedule to run daily at 2 AM.

### Linux/Mac Cron

Add to crontab (`crontab -e`):

```bash
# Daily at 2 AM
0 2 * * * cd /path/to/avatar-studio && python maintenance.py optimize

# Weekly backup on Sunday at 3 AM
0 3 * * 0 cd /path/to/avatar-studio && python maintenance.py backup

# Monthly cleanup on 1st at 4 AM
0 4 1 * * cd /path/to/avatar-studio && python maintenance.py cleanup --days 30
```

---

## 🚨 Troubleshooting

### Backup Failed

**Problem:** Backup creation fails

**Solutions:**
1. Check disk space: `python maintenance.py diagnose`
2. Check permissions on backup directory
3. Try without models: `python maintenance.py backup --no-output`

### Restore Failed

**Problem:** Restore fails

**Solutions:**
1. Verify backup file exists and is not corrupted
2. Check available disk space
3. Close the application before restoring
4. Restore incrementally (database only first)

### Cleanup Removes Too Much

**Problem:** Important files deleted

**Solutions:**
1. **Always use --dry-run first!**
2. Restore from backup: `python maintenance.py restore latest_backup.zip`
3. Check backup directory for automatic backups
4. Adjust days parameter (increase to keep more)

### Out of Disk Space

**Problem:** Running out of disk space

**Solutions:**
```bash
# 1. Analyze usage
python maintenance.py diagnose

# 2. Find large files
python utils/cleanup_manager.py large

# 3. Clean aggressively (7 days)
python maintenance.py cleanup --days 7

# 4. Remove old backups
python utils/backup_manager.py cleanup --keep 3
```

---

## 💡 Tips & Best Practices

### Backup Strategy

1. **Create backups before major operations:**
   ```bash
   python maintenance.py backup
   # Then do risky operation
   ```

2. **Keep multiple backup versions:**
   - Keep at least 5 recent backups
   - One weekly backup for a month
   - One monthly backup for a year

3. **Store backups off-site:**
   - Copy to external drive
   - Upload to cloud storage
   - Keep in different physical location

### Cleanup Strategy

1. **Always preview first:**
   ```bash
   python maintenance.py cleanup --dry-run
   ```

2. **Clean incrementally:**
   - Start with 90 days
   - Then 60 days
   - Then 30 days
   - Finally 7 days (if needed)

3. **Keep successful projects:**
   - Only clean failed generations
   - Archive important videos elsewhere
   - Don't clean if unsure

### Optimization

1. **Run optimize weekly:**
   ```bash
   python maintenance.py optimize
   ```

2. **Monitor disk usage:**
   ```bash
   python maintenance.py status
   ```

3. **Check diagnostics monthly:**
   ```bash
   python maintenance.py diagnose
   ```

---

## 📊 Disk Space Planning

### Typical Usage

- **Small project (10 videos):**
  - Output: ~500 MB
  - Database: ~1 MB
  - Logs: ~5 MB
  - Total: ~500 MB

- **Medium project (100 videos):**
  - Output: ~5 GB
  - Database: ~10 MB
  - Logs: ~50 MB
  - Total: ~5 GB

- **Large project (1000 videos):**
  - Output: ~50 GB
  - Database: ~100 MB
  - Logs: ~500 MB
  - Total: ~50 GB

### Recommended Allocation

- **Minimum:** 10 GB free
- **Comfortable:** 50 GB free
- **Production:** 100+ GB free

### Models Size

- **Required models:** ~400 MB
- **Optional models:** ~1 GB
- **Total models:** ~1.5 GB max

---

## 🔐 Safety Features

All maintenance tools include safety features:

1. **Dry-run mode** - Preview before deleting
2. **Automatic backups** - Before restore operations
3. **Selective restore** - Choose what to restore
4. **Metadata tracking** - Know what's in each backup
5. **Confirmation prompts** - For destructive operations

---

## 📞 Support

For issues with maintenance tools:

1. Check logs: `./logs/`
2. Run diagnostics: `python maintenance.py diagnose`
3. Verify installation: `python verify_setup.py`
4. Check disk space: `python maintenance.py status`

---

**Keep your Avatar Studio running smoothly! 🎬✨**
