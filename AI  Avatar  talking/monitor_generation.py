#!/usr/bin/env python3
"""
Real-time generation monitoring tool for AI Avatar Studio.

Monitors active generations and displays live statistics.

Usage:
    python monitor_generation.py
    python monitor_generation.py --watch
    python monitor_generation.py --stats

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.database_manager import DatabaseManager


class GenerationMonitor:
    """Monitors generation activity."""
    
    def __init__(self):
        """Initialize monitor."""
        self.db = DatabaseManager()
    
    def get_active_generations(self) -> List[Dict]:
        """
        Get currently active generations.
        
        Returns:
            List of active generation records
        """
        # In a real implementation, this would query for 'in_progress' status
        # For now, we'll get recent generations
        return self.db.get_recent_generations(limit=10)
    
    def get_statistics(self) -> Dict:
        """
        Get current statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.db.get_statistics()
    
    def get_recent_activity(self, hours: int = 24) -> Dict:
        """
        Get activity in recent hours.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            Activity summary
        """
        stats = self.db.get_statistics()
        
        # Calculate activity metrics
        total = stats.get('total_generations', 0)
        success = stats.get('successful_generations', 0)
        failed = stats.get('failed_generations', 0)
        
        return {
            'total_generations': total,
            'successful': success,
            'failed': failed,
            'success_rate': stats.get('success_rate', 0),
            'average_time': stats.get('average_processing_time_seconds', 0)
        }
    
    def display_dashboard(self):
        """Display monitoring dashboard."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("="*70)
        print("AI AVATAR STUDIO - GENERATION MONITOR".center(70))
        print("="*70)
        print()
        
        # Get statistics
        stats = self.get_statistics()
        activity = self.get_recent_activity()
        
        # Overall Statistics
        print("📊 OVERALL STATISTICS")
        print("-"*70)
        print(f"Total Projects:      {stats.get('total_projects', 0)}")
        print(f"Total Generations:   {stats.get('total_generations', 0)}")
        print(f"Success Rate:        {stats.get('success_rate', 0):.1f}%")
        print(f"Average Time:        {stats.get('average_processing_time_seconds', 0):.1f}s")
        print()
        
        # Recent Activity
        print("📈 RECENT ACTIVITY (24h)")
        print("-"*70)
        print(f"Successful:          {activity['successful']}")
        print(f"Failed:              {activity['failed']}")
        print(f"Success Rate:        {activity['success_rate']:.1f}%")
        print()
        
        # Active Generations
        print("🔄 RECENT GENERATIONS")
        print("-"*70)
        
        recent = self.db.get_recent_generations(limit=5)
        
        if recent:
            for gen in recent:
                status = gen.get('status', 'unknown')
                status_icon = {
                    'completed': '✅',
                    'failed': '❌',
                    'in_progress': '⏳',
                    'pending': '⏸️'
                }.get(status, '❓')
                
                project_name = gen.get('project_name', 'Unknown')
                created = gen.get('created_at', '')
                duration = gen.get('processing_time_seconds', 0)
                
                print(f"{status_icon} {project_name[:40]}")
                print(f"   Status: {status}, Time: {duration:.1f}s, Created: {created}")
        else:
            print("No recent generations found")
        
        print()
        print("="*70)
        print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Press Ctrl+C to exit")
        print()
    
    def watch(self, interval: int = 5):
        """
        Watch mode - continuously update display.
        
        Args:
            interval: Update interval in seconds
        """
        try:
            while True:
                self.display_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped.")
    
    def display_stats(self):
        """Display detailed statistics."""
        stats = self.get_statistics()
        
        print("\n" + "="*70)
        print("DETAILED STATISTICS".center(70))
        print("="*70 + "\n")
        
        print("📦 Projects")
        print(f"  Total:             {stats.get('total_projects', 0)}")
        print()
        
        print("🎬 Generations")
        print(f"  Total:             {stats.get('total_generations', 0)}")
        print(f"  Successful:        {stats.get('successful_generations', 0)}")
        print(f"  Failed:            {stats.get('failed_generations', 0)}")
        print(f"  Success Rate:      {stats.get('success_rate', 0):.2f}%")
        print()
        
        print("⏱️ Performance")
        print(f"  Average Time:      {stats.get('average_processing_time_seconds', 0):.2f}s")
        print(f"  Total Time:        {stats.get('total_processing_time_seconds', 0):.2f}s")
        print()
        
        # Additional metrics
        if stats.get('total_generations', 0) > 0:
            avg_duration = stats.get('average_processing_time_seconds', 0)
            if avg_duration > 0:
                daily_capacity = (24 * 3600) / avg_duration
                print("📊 Capacity Analysis")
                print(f"  Videos per hour:   {3600 / avg_duration:.1f}")
                print(f"  Daily capacity:    {daily_capacity:.0f}")
                print()
        
        print("="*70 + "\n")
    
    def export_report(self, output_file: str = "generation_report.json"):
        """
        Export detailed report to JSON.
        
        Args:
            output_file: Output file path
        """
        stats = self.get_statistics()
        activity = self.get_recent_activity()
        recent = self.db.get_recent_generations(limit=20)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "recent_activity": activity,
            "recent_generations": recent
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n✅ Report exported to: {output_file}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Monitor AI Avatar Studio generation activity",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch mode - continuously update display"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show detailed statistics"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export report to JSON file"
    )
    
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="Update interval in seconds (default: 5)"
    )
    
    args = parser.parse_args()
    
    monitor = GenerationMonitor()
    
    try:
        if args.watch:
            monitor.watch(interval=args.interval)
        elif args.stats:
            monitor.display_stats()
        elif args.export:
            monitor.export_report(args.export)
        else:
            # Default: show dashboard once
            monitor.display_dashboard()
    
    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
