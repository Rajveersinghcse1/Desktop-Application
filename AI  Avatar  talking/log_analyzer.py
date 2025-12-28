#!/usr/bin/env python3
"""
Log analyzer for AI Avatar Studio.

Analyzes application logs to identify errors, performance issues, and patterns.

Usage:
    python log_analyzer.py
    python log_analyzer.py --errors
    python log_analyzer.py --performance
    python log_analyzer.py --export report.html

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class LogAnalyzer:
    """Analyze application logs."""
    
    def __init__(self, log_dir: str = None):
        """Initialize log analyzer."""
        self.base_dir = Path(__file__).parent
        self.log_dir = Path(log_dir) if log_dir else self.base_dir / "logs"
        
        self.entries = []
        self.errors = []
        self.warnings = []
        self.performance_data = []
        
        # Regex patterns
        self.log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d+ - (\w+) - (.+)'
        )
        self.performance_pattern = re.compile(
            r'(\w+) took ([\d.]+)s'
        )
        self.error_pattern = re.compile(
            r'Error: (.+)|Exception: (.+)|Failed to (.+)'
        )
    
    def load_logs(self, filename: str = "app.log", days: int = 7):
        """
        Load log entries.
        
        Args:
            filename: Log file name
            days: Number of days to analyze
        """
        log_file = self.log_dir / filename
        
        if not log_file.exists():
            print(f"⚠️  Log file not found: {log_file}")
            return
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        print(f"📖 Loading logs from: {log_file}")
        print(f"   Analyzing last {days} days...\n")
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry = self._parse_log_entry(line)
                if entry and entry['timestamp'] >= cutoff_date:
                    self.entries.append(entry)
                    
                    if entry['level'] == 'ERROR':
                        self.errors.append(entry)
                    elif entry['level'] == 'WARNING':
                        self.warnings.append(entry)
                    
                    # Extract performance data
                    perf_match = self.performance_pattern.search(entry['message'])
                    if perf_match:
                        self.performance_data.append({
                            'timestamp': entry['timestamp'],
                            'operation': perf_match.group(1),
                            'duration': float(perf_match.group(2))
                        })
        
        print(f"✅ Loaded {len(self.entries)} log entries")
        print(f"   Errors: {len(self.errors)}")
        print(f"   Warnings: {len(self.warnings)}")
        print(f"   Performance entries: {len(self.performance_data)}\n")
    
    def _parse_log_entry(self, line: str) -> Dict:
        """Parse a single log entry."""
        match = self.log_pattern.match(line)
        if not match:
            return None
        
        try:
            timestamp = datetime.strptime(match.group(1), '%Y-%m-%d %H:%M:%S')
            level = match.group(2)
            message = match.group(3)
            
            return {
                'timestamp': timestamp,
                'level': level,
                'message': message,
                'raw': line.strip()
            }
        except Exception:
            return None
    
    def analyze_errors(self):
        """Analyze error patterns."""
        print("\n" + "="*70)
        print("ERROR ANALYSIS".center(70))
        print("="*70 + "\n")
        
        if not self.errors:
            print("✅ No errors found!\n")
            return
        
        # Group errors by type
        error_types = Counter()
        error_details = defaultdict(list)
        
        for error in self.errors:
            # Extract error type
            error_match = self.error_pattern.search(error['message'])
            if error_match:
                error_type = error_match.group(1) or error_match.group(2) or error_match.group(3)
                error_types[error_type] += 1
                error_details[error_type].append({
                    'timestamp': error['timestamp'],
                    'message': error['message']
                })
            else:
                error_types['Unknown'] += 1
                error_details['Unknown'].append({
                    'timestamp': error['timestamp'],
                    'message': error['message']
                })
        
        # Display top errors
        print(f"Total Errors: {len(self.errors)}\n")
        print("Top Error Types:")
        
        for error_type, count in error_types.most_common(10):
            print(f"  {count:4d}x  {error_type[:60]}")
        
        print("\n" + "-"*70 + "\n")
        
        # Show recent errors
        print("Recent Errors (last 10):\n")
        for error in sorted(self.errors, key=lambda x: x['timestamp'], reverse=True)[:10]:
            print(f"  [{error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}]")
            print(f"  {error['message'][:100]}")
            print()
    
    def analyze_warnings(self):
        """Analyze warning patterns."""
        print("\n" + "="*70)
        print("WARNING ANALYSIS".center(70))
        print("="*70 + "\n")
        
        if not self.warnings:
            print("✅ No warnings found!\n")
            return
        
        # Group warnings
        warning_types = Counter()
        
        for warning in self.warnings:
            # Simple categorization
            msg = warning['message'].lower()
            if 'gpu' in msg or 'cuda' in msg:
                category = 'GPU/CUDA'
            elif 'memory' in msg:
                category = 'Memory'
            elif 'disk' in msg or 'space' in msg:
                category = 'Disk Space'
            elif 'model' in msg:
                category = 'Model'
            elif 'deprecat' in msg:
                category = 'Deprecation'
            else:
                category = 'Other'
            
            warning_types[category] += 1
        
        print(f"Total Warnings: {len(self.warnings)}\n")
        print("Warning Categories:")
        
        for category, count in warning_types.most_common():
            print(f"  {count:4d}x  {category}")
        
        print()
    
    def analyze_performance(self):
        """Analyze performance metrics."""
        print("\n" + "="*70)
        print("PERFORMANCE ANALYSIS".center(70))
        print("="*70 + "\n")
        
        if not self.performance_data:
            print("ℹ️  No performance data found in logs.\n")
            return
        
        # Group by operation
        operations = defaultdict(list)
        
        for entry in self.performance_data:
            operations[entry['operation']].append(entry['duration'])
        
        # Calculate statistics
        print("Operation Performance:\n")
        print(f"{'Operation':<30} {'Count':>8} {'Avg (s)':>10} {'Min (s)':>10} {'Max (s)':>10}")
        print("-"*70)
        
        for operation, durations in sorted(operations.items()):
            count = len(durations)
            avg = sum(durations) / count
            min_dur = min(durations)
            max_dur = max(durations)
            
            print(f"{operation:<30} {count:>8} {avg:>10.2f} {min_dur:>10.2f} {max_dur:>10.2f}")
        
        print()
        
        # Identify slow operations
        print("Slowest Operations:\n")
        
        all_operations = []
        for entry in self.performance_data:
            all_operations.append((entry['operation'], entry['duration'], entry['timestamp']))
        
        all_operations.sort(key=lambda x: x[1], reverse=True)
        
        for operation, duration, timestamp in all_operations[:10]:
            print(f"  {duration:6.2f}s  {operation:<30} [{timestamp.strftime('%Y-%m-%d %H:%M:%S')}]")
        
        print()
    
    def analyze_timeline(self):
        """Analyze activity timeline."""
        print("\n" + "="*70)
        print("ACTIVITY TIMELINE".center(70))
        print("="*70 + "\n")
        
        if not self.entries:
            print("ℹ️  No log entries found.\n")
            return
        
        # Group by hour
        hourly_activity = defaultdict(lambda: {'total': 0, 'errors': 0, 'warnings': 0})
        
        for entry in self.entries:
            hour = entry['timestamp'].replace(minute=0, second=0, microsecond=0)
            hourly_activity[hour]['total'] += 1
            
            if entry['level'] == 'ERROR':
                hourly_activity[hour]['errors'] += 1
            elif entry['level'] == 'WARNING':
                hourly_activity[hour]['warnings'] += 1
        
        # Display timeline
        print("Activity by Hour:\n")
        print(f"{'Time':<20} {'Total':>8} {'Errors':>8} {'Warnings':>8} {'Activity'}")
        print("-"*70)
        
        for hour in sorted(hourly_activity.keys()):
            data = hourly_activity[hour]
            bar = '█' * min(50, data['total'] // 10)
            
            print(f"{hour.strftime('%Y-%m-%d %H:00'):<20} "
                  f"{data['total']:>8} "
                  f"{data['errors']:>8} "
                  f"{data['warnings']:>8} "
                  f"{bar}")
        
        print()
    
    def generate_summary(self):
        """Generate summary report."""
        print("\n" + "="*70)
        print("SUMMARY REPORT".center(70))
        print("="*70 + "\n")
        
        if not self.entries:
            print("ℹ️  No log data to analyze.\n")
            return
        
        # Time range
        start = min(e['timestamp'] for e in self.entries)
        end = max(e['timestamp'] for e in self.entries)
        duration = end - start
        
        print(f"Analysis Period:")
        print(f"  Start: {start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  End:   {end.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Duration: {duration.days} days, {duration.seconds // 3600} hours")
        print()
        
        # Log levels
        level_counts = Counter(e['level'] for e in self.entries)
        
        print(f"Log Levels:")
        for level, count in level_counts.most_common():
            percentage = (count / len(self.entries)) * 100
            print(f"  {level:<10} {count:>6} ({percentage:>5.1f}%)")
        print()
        
        # Error rate
        if self.errors:
            error_rate = (len(self.errors) / len(self.entries)) * 100
            print(f"Error Rate: {error_rate:.2f}%")
            
            if error_rate > 10:
                print("  ⚠️  High error rate detected!")
            elif error_rate > 5:
                print("  ℹ️  Moderate error rate")
            else:
                print("  ✅ Low error rate")
        else:
            print(f"Error Rate: 0%")
            print("  ✅ No errors!")
        
        print()
        
        # Performance summary
        if self.performance_data:
            avg_duration = sum(e['duration'] for e in self.performance_data) / len(self.performance_data)
            print(f"Performance:")
            print(f"  Operations logged: {len(self.performance_data)}")
            print(f"  Average duration: {avg_duration:.2f}s")
            print()
    
    def export_html_report(self, output_file: str):
        """Export detailed HTML report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Log Analysis Report - AI Avatar Studio</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-top: 30px; }}
        .stat {{ display: inline-block; margin: 10px 20px 10px 0; padding: 15px; background: #f9f9f9; border-radius: 5px; }}
        .stat-label {{ font-size: 12px; color: #777; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #333; }}
        .error {{ color: #d32f2f; }}
        .warning {{ color: #f57c00; }}
        .success {{ color: #388e3c; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        .timestamp {{ color: #666; font-size: 12px; }}
        .message {{ font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Log Analysis Report</h1>
        <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Summary</h2>
        <div class="stat">
            <div class="stat-label">Total Entries</div>
            <div class="stat-value">{len(self.entries)}</div>
        </div>
        <div class="stat">
            <div class="stat-label error">Errors</div>
            <div class="stat-value error">{len(self.errors)}</div>
        </div>
        <div class="stat">
            <div class="stat-label warning">Warnings</div>
            <div class="stat-value warning">{len(self.warnings)}</div>
        </div>
        <div class="stat">
            <div class="stat-label success">Info</div>
            <div class="stat-value success">{len([e for e in self.entries if e['level'] == 'INFO'])}</div>
        </div>
        
        <h2>Recent Errors</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Message</th>
            </tr>
"""
        
        for error in sorted(self.errors, key=lambda x: x['timestamp'], reverse=True)[:20]:
            html += f"""            <tr>
                <td class="timestamp">{error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td class="message error">{error['message'][:200]}</td>
            </tr>
"""
        
        html += """        </table>
        
        <h2>Performance Metrics</h2>
        <table>
            <tr>
                <th>Operation</th>
                <th>Count</th>
                <th>Avg (s)</th>
                <th>Min (s)</th>
                <th>Max (s)</th>
            </tr>
"""
        
        operations = defaultdict(list)
        for entry in self.performance_data:
            operations[entry['operation']].append(entry['duration'])
        
        for operation, durations in sorted(operations.items()):
            count = len(durations)
            avg = sum(durations) / count
            min_dur = min(durations)
            max_dur = max(durations)
            
            html += f"""            <tr>
                <td>{operation}</td>
                <td>{count}</td>
                <td>{avg:.2f}</td>
                <td>{min_dur:.2f}</td>
                <td>{max_dur:.2f}</td>
            </tr>
"""
        
        html += """        </table>
    </div>
</body>
</html>
"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"\n✅ HTML report exported to: {output_file}\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Log analyzer for AI Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--log-dir",
        type=str,
        help="Log directory path (default: ./logs)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        default="app.log",
        help="Log file name (default: app.log)"
    )
    
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days to analyze (default: 7)"
    )
    
    parser.add_argument(
        "--errors",
        action="store_true",
        help="Show only error analysis"
    )
    
    parser.add_argument(
        "--performance",
        action="store_true",
        help="Show only performance analysis"
    )
    
    parser.add_argument(
        "--timeline",
        action="store_true",
        help="Show only timeline analysis"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export HTML report to file"
    )
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer(log_dir=args.log_dir)
    
    try:
        analyzer.load_logs(filename=args.log_file, days=args.days)
        
        if args.errors:
            analyzer.analyze_errors()
        elif args.performance:
            analyzer.analyze_performance()
        elif args.timeline:
            analyzer.analyze_timeline()
        else:
            # Full analysis
            analyzer.generate_summary()
            analyzer.analyze_errors()
            analyzer.analyze_warnings()
            analyzer.analyze_performance()
            analyzer.analyze_timeline()
        
        if args.export:
            analyzer.export_html_report(args.export)
    
    except KeyboardInterrupt:
        print("\n\nAnalysis cancelled.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
