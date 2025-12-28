# 🐳 Docker Quick Start Guide

## Setup in 3 Steps

### Windows

```cmd
cd "C:\Users\rkste\Desktop\AI  Avatar  talking"
scripts\docker_manage.bat setup
```

### Linux/Mac

```bash
cd ~/ai-avatar-studio
chmod +x scripts/docker_manage.sh
./scripts/docker_manage.sh setup
```

## What This Does

1. ✅ Creates persistent volume directories
2. ✅ Builds Docker image with all dependencies
3. ✅ Starts containers
4. ✅ Initializes SQLite database automatically

## Database Location

- **Inside Container**: `/app/data/database/projects.db`
- **On Your Computer**: `./docker_volumes/data/database/projects.db`

## Important: Data Persistence

Your data is stored in `docker_volumes/` folder:

```
docker_volumes/
├── data/database/projects.db  ← Your database (BACKED UP)
├── models/                    ← AI models (~3-5GB)
└── output/videos/             ← Generated videos
```

**Safe to Delete Container**: Data persists in volumes!
**NOT Safe to Delete**: `docker_volumes/` folder (contains all your data)

## Common Commands

| Action | Windows | Linux/Mac |
|--------|---------|-----------|
| Start | `scripts\docker_manage.bat start` | `./scripts/docker_manage.sh start` |
| Stop | `scripts\docker_manage.bat stop` | `./scripts/docker_manage.sh stop` |
| Status | `scripts\docker_manage.bat status` | `./scripts/docker_manage.sh status` |
| Backup DB | `scripts\docker_manage.bat backup` | `./scripts/docker_manage.sh backup` |
| View Logs | `scripts\docker_manage.bat logs` | `./scripts/docker_manage.sh logs` |

## Backup Your Database

```cmd
# Creates timestamped backup
scripts\docker_manage.bat backup

# Output: backups/projects_backup_20231222_143052.db
```

## Need More Help?

See [DOCKER_DATABASE_ARCHITECTURE.md](DOCKER_DATABASE_ARCHITECTURE.md) for complete documentation.
