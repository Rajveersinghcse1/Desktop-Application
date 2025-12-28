#!/bin/bash
# Docker setup and management script for AI Avatar Studio

set -e  # Exit on error

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================="
echo "AI Avatar Studio - Docker Management"
echo "========================================="

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Create necessary directories for volumes
setup_volumes() {
    print_info "Setting up Docker volumes..."
    
    mkdir -p "$PROJECT_ROOT/docker_volumes/data/database"
    mkdir -p "$PROJECT_ROOT/docker_volumes/data/cache"
    mkdir -p "$PROJECT_ROOT/docker_volumes/data/logs"
    mkdir -p "$PROJECT_ROOT/docker_volumes/models"
    mkdir -p "$PROJECT_ROOT/docker_volumes/output/videos"
    mkdir -p "$PROJECT_ROOT/docker_volumes/output/thumbnails"
    mkdir -p "$PROJECT_ROOT/local_output"
    
    print_success "Volume directories created"
}

# Build Docker image
build_image() {
    print_info "Building Docker image..."
    cd "$PROJECT_ROOT"
    docker-compose build
    print_success "Docker image built successfully"
}

# Start containers
start_containers() {
    print_info "Starting containers..."
    cd "$PROJECT_ROOT"
    docker-compose up -d
    print_success "Containers started"
    
    echo ""
    echo "Container Status:"
    docker-compose ps
}

# Stop containers
stop_containers() {
    print_info "Stopping containers..."
    cd "$PROJECT_ROOT"
    docker-compose down
    print_success "Containers stopped"
}

# View logs
view_logs() {
    cd "$PROJECT_ROOT"
    docker-compose logs -f
}

# Check status
check_status() {
    cd "$PROJECT_ROOT"
    echo "Container Status:"
    docker-compose ps
    
    echo ""
    echo "Volume Usage:"
    du -sh "$PROJECT_ROOT/docker_volumes/"* 2>/dev/null || echo "No volumes yet"
    
    echo ""
    echo "Database Status:"
    if [ -f "$PROJECT_ROOT/docker_volumes/data/database/projects.db" ]; then
        DB_SIZE=$(du -h "$PROJECT_ROOT/docker_volumes/data/database/projects.db" | cut -f1)
        print_success "Database exists (Size: $DB_SIZE)"
        
        # Show database statistics
        docker-compose exec ai-avatar-studio python3 -c "
from utils.database import DatabaseManager
db = DatabaseManager()
stats = db.get_statistics()
print(f'Total Projects: {stats[\"total_projects\"]}')
print(f'Total Generations: {stats[\"total_generations\"]}')
print(f'Success Rate: {stats[\"success_rate\"]:.2f}%')
" 2>/dev/null || echo "Container not running"
    else
        print_info "Database not yet created"
    fi
}

# Backup database
backup_database() {
    print_info "Creating database backup..."
    
    BACKUP_DIR="$PROJECT_ROOT/backups"
    mkdir -p "$BACKUP_DIR"
    
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/projects_backup_$TIMESTAMP.db"
    
    if [ -f "$PROJECT_ROOT/docker_volumes/data/database/projects.db" ]; then
        cp "$PROJECT_ROOT/docker_volumes/data/database/projects.db" "$BACKUP_FILE"
        print_success "Backup created: $BACKUP_FILE"
    else
        print_error "Database file not found"
        exit 1
    fi
}

# Restore database
restore_database() {
    if [ -z "$1" ]; then
        print_error "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_info "Restoring database from: $BACKUP_FILE"
    
    # Stop containers
    stop_containers
    
    # Restore backup
    cp "$BACKUP_FILE" "$PROJECT_ROOT/docker_volumes/data/database/projects.db"
    
    print_success "Database restored successfully"
    
    # Restart containers
    start_containers
}

# Clean up old data
cleanup() {
    print_info "Cleaning up old data..."
    
    # Remove old cache files
    find "$PROJECT_ROOT/docker_volumes/data/cache" -type f -mtime +7 -delete 2>/dev/null
    
    # Rotate logs
    find "$PROJECT_ROOT/docker_volumes/data/logs" -name "*.log" -mtime +30 -delete 2>/dev/null
    
    # Clean up Docker
    docker system prune -f
    
    print_success "Cleanup completed"
}

# Reset everything (DANGEROUS)
reset_all() {
    read -p "This will delete ALL data including database, models, and outputs. Continue? (yes/no): " confirm
    
    if [ "$confirm" != "yes" ]; then
        print_info "Reset cancelled"
        exit 0
    fi
    
    print_info "Resetting everything..."
    
    # Stop containers
    stop_containers
    
    # Remove volumes
    rm -rf "$PROJECT_ROOT/docker_volumes"
    
    # Remove containers and images
    docker-compose down --rmi all --volumes
    
    print_success "Reset completed. Run 'setup' to start fresh."
}

# Show help
show_help() {
    cat << EOF
Usage: $0 [command]

Commands:
    setup       - Initial setup (create volumes, build image)
    build       - Build Docker image
    start       - Start containers
    stop        - Stop containers
    restart     - Restart containers
    logs        - View container logs
    status      - Show container and database status
    backup      - Backup database
    restore     - Restore database from backup
    cleanup     - Clean up old files and Docker cache
    reset       - Reset everything (DANGEROUS)
    shell       - Open shell in container
    help        - Show this help message

Examples:
    $0 setup                                    # First-time setup
    $0 start                                    # Start the application
    $0 logs                                     # View logs
    $0 backup                                   # Backup database
    $0 restore backups/projects_backup_*.db     # Restore from backup
EOF
}

# Open shell in container
open_shell() {
    cd "$PROJECT_ROOT"
    docker-compose exec ai-avatar-studio /bin/bash
}

# Main command handler
case "$1" in
    setup)
        check_docker
        setup_volumes
        build_image
        start_containers
        print_success "Setup complete! Application is running."
        ;;
    build)
        check_docker
        build_image
        ;;
    start)
        check_docker
        setup_volumes
        start_containers
        ;;
    stop)
        stop_containers
        ;;
    restart)
        stop_containers
        start_containers
        ;;
    logs)
        view_logs
        ;;
    status)
        check_status
        ;;
    backup)
        backup_database
        ;;
    restore)
        restore_database "$2"
        ;;
    cleanup)
        cleanup
        ;;
    reset)
        reset_all
        ;;
    shell)
        open_shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
