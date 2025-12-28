#!/usr/bin/env python3
"""
Performance benchmark tool for AI Avatar Studio.

Measures and compares performance across different configurations.

Usage:
    python benchmark.py
    python benchmark.py --full
    python benchmark.py --compare
    python benchmark.py --export results.json

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import time
import json
import platform
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class PerformanceBenchmark:
    """Performance benchmarking tool."""
    
    def __init__(self):
        """Initialize benchmark."""
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info(),
            'benchmarks': {}
        }
    
    def _get_system_info(self) -> Dict:
        """Get system information."""
        info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'python_version': sys.version.split()[0],
            'architecture': platform.machine()
        }
        
        # RAM
        try:
            import psutil
            info['ram_gb'] = psutil.virtual_memory().total / (1024**3)
            info['ram_available_gb'] = psutil.virtual_memory().available / (1024**3)
        except ImportError:
            info['ram_gb'] = 'unknown'
        
        # GPU
        try:
            import torch
            if torch.cuda.is_available():
                info['gpu'] = torch.cuda.get_device_name(0)
                info['cuda_version'] = torch.version.cuda
            else:
                info['gpu'] = 'none'
        except ImportError:
            info['gpu'] = 'unknown'
        
        return info
    
    def benchmark_imports(self) -> Dict:
        """Benchmark module import times."""
        print("\n🔍 Benchmarking imports...")
        
        imports = {
            'torch': 'import torch',
            'opencv': 'import cv2',
            'numpy': 'import numpy',
            'PIL': 'from PIL import Image',
            'customtkinter': 'import customtkinter',
            'librosa': 'import librosa'
        }
        
        results = {}
        
        for name, import_stmt in imports.items():
            try:
                start = time.time()
                exec(import_stmt)
                duration = time.time() - start
                results[name] = {
                    'time_ms': duration * 1000,
                    'status': 'success'
                }
                print(f"  {name:15s} {duration*1000:6.1f} ms")
            except ImportError:
                results[name] = {
                    'time_ms': 0,
                    'status': 'not_installed'
                }
                print(f"  {name:15s} NOT INSTALLED")
        
        return results
    
    def benchmark_face_detection(self) -> Dict:
        """Benchmark face detection performance."""
        print("\n🔍 Benchmarking face detection...")
        
        try:
            from core.face_detection import FaceDetectionManager
            import numpy as np
            from PIL import Image
            
            # Create test image
            test_image = Image.new('RGB', (640, 480), color='white')
            
            face_mgr = FaceDetectionManager()
            
            # Warm up
            face_mgr.detect_from_image(test_image)
            
            # Benchmark
            iterations = 10
            start = time.time()
            for _ in range(iterations):
                face_mgr.detect_from_image(test_image)
            duration = (time.time() - start) / iterations
            
            result = {
                'avg_time_ms': duration * 1000,
                'iterations': iterations,
                'fps': 1 / duration if duration > 0 else 0
            }
            
            print(f"  Average: {result['avg_time_ms']:.1f} ms/frame")
            print(f"  FPS: {result['fps']:.1f}")
            
            return result
        
        except Exception as e:
            print(f"  Error: {str(e)}")
            return {'error': str(e)}
    
    def benchmark_tts(self) -> Dict:
        """Benchmark text-to-speech performance."""
        print("\n🔍 Benchmarking TTS...")
        
        try:
            from core.tts import TTSManager
            
            tts = TTSManager()
            test_text = "The quick brown fox jumps over the lazy dog."
            
            # Warm up
            tts.synthesize(test_text)
            
            # Benchmark
            iterations = 5
            start = time.time()
            for _ in range(iterations):
                tts.synthesize(test_text)
            duration = (time.time() - start) / iterations
            
            result = {
                'avg_time_s': duration,
                'chars_per_second': len(test_text) / duration,
                'iterations': iterations
            }
            
            print(f"  Average: {result['avg_time_s']:.2f} s")
            print(f"  Speed: {result['chars_per_second']:.0f} chars/s")
            
            return result
        
        except Exception as e:
            print(f"  Error: {str(e)}")
            return {'error': str(e)}
    
    def benchmark_video_encoding(self) -> Dict:
        """Benchmark video encoding performance."""
        print("\n🔍 Benchmarking video encoding...")
        
        try:
            from core.video import VideoProcessor
            import numpy as np
            from PIL import Image
            import tempfile
            
            processor = VideoProcessor()
            
            # Create test frames
            frames = []
            for _ in range(30):  # 1 second at 30fps
                img = Image.new('RGB', (640, 480), color='blue')
                frames.append(img)
            
            # Benchmark
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp_path = tmp.name
            
            try:
                start = time.time()
                processor.create_video_from_frames(
                    frames=frames,
                    output_path=tmp_path,
                    fps=30
                )
                duration = time.time() - start
                
                result = {
                    'time_s': duration,
                    'fps_achieved': len(frames) / duration,
                    'frame_count': len(frames)
                }
                
                print(f"  Time: {result['time_s']:.2f} s")
                print(f"  Speed: {result['fps_achieved']:.1f} fps")
                
                return result
            
            finally:
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
        
        except Exception as e:
            print(f"  Error: {str(e)}")
            return {'error': str(e)}
    
    def benchmark_database(self) -> Dict:
        """Benchmark database operations."""
        print("\n🔍 Benchmarking database...")
        
        try:
            from utils.database_manager import DatabaseManager
            
            db = DatabaseManager()
            
            # Benchmark writes
            write_times = []
            for i in range(100):
                start = time.time()
                project_id = db.create_project(f"Benchmark_Test_{i}")
                write_times.append(time.time() - start)
                db.delete_project(project_id)
            
            # Benchmark reads
            project_id = db.create_project("Benchmark_Read_Test")
            read_times = []
            for _ in range(100):
                start = time.time()
                db.get_project(project_id)
                read_times.append(time.time() - start)
            db.delete_project(project_id)
            
            result = {
                'avg_write_ms': sum(write_times) / len(write_times) * 1000,
                'avg_read_ms': sum(read_times) / len(read_times) * 1000,
                'write_ops_per_sec': 1 / (sum(write_times) / len(write_times)),
                'read_ops_per_sec': 1 / (sum(read_times) / len(read_times))
            }
            
            print(f"  Write: {result['avg_write_ms']:.2f} ms ({result['write_ops_per_sec']:.0f} ops/s)")
            print(f"  Read: {result['avg_read_ms']:.2f} ms ({result['read_ops_per_sec']:.0f} ops/s)")
            
            return result
        
        except Exception as e:
            print(f"  Error: {str(e)}")
            return {'error': str(e)}
    
    def benchmark_disk_io(self) -> Dict:
        """Benchmark disk I/O performance."""
        print("\n🔍 Benchmarking disk I/O...")
        
        try:
            import tempfile
            
            # Write test
            test_data = b'0' * (10 * 1024 * 1024)  # 10 MB
            
            write_times = []
            for _ in range(5):
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp_path = tmp.name
                
                try:
                    start = time.time()
                    with open(tmp_path, 'wb') as f:
                        f.write(test_data)
                    write_times.append(time.time() - start)
                finally:
                    os.unlink(tmp_path)
            
            # Read test
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp_path = tmp.name
                tmp.write(test_data)
            
            try:
                read_times = []
                for _ in range(5):
                    start = time.time()
                    with open(tmp_path, 'rb') as f:
                        _ = f.read()
                    read_times.append(time.time() - start)
            finally:
                os.unlink(tmp_path)
            
            avg_write = sum(write_times) / len(write_times)
            avg_read = sum(read_times) / len(read_times)
            
            result = {
                'write_speed_mb_s': 10 / avg_write,
                'read_speed_mb_s': 10 / avg_read,
                'avg_write_time_s': avg_write,
                'avg_read_time_s': avg_read
            }
            
            print(f"  Write: {result['write_speed_mb_s']:.1f} MB/s")
            print(f"  Read: {result['read_speed_mb_s']:.1f} MB/s")
            
            return result
        
        except Exception as e:
            print(f"  Error: {str(e)}")
            return {'error': str(e)}
    
    def run_quick_benchmark(self) -> Dict:
        """Run quick benchmark suite."""
        print("\n" + "="*70)
        print("QUICK PERFORMANCE BENCHMARK".center(70))
        print("="*70)
        
        self.results['benchmarks']['imports'] = self.benchmark_imports()
        self.results['benchmarks']['database'] = self.benchmark_database()
        self.results['benchmarks']['disk_io'] = self.benchmark_disk_io()
        
        return self.results
    
    def run_full_benchmark(self) -> Dict:
        """Run complete benchmark suite."""
        print("\n" + "="*70)
        print("FULL PERFORMANCE BENCHMARK".center(70))
        print("="*70)
        
        self.results['benchmarks']['imports'] = self.benchmark_imports()
        self.results['benchmarks']['face_detection'] = self.benchmark_face_detection()
        self.results['benchmarks']['tts'] = self.benchmark_tts()
        self.results['benchmarks']['video_encoding'] = self.benchmark_video_encoding()
        self.results['benchmarks']['database'] = self.benchmark_database()
        self.results['benchmarks']['disk_io'] = self.benchmark_disk_io()
        
        return self.results
    
    def display_summary(self):
        """Display benchmark summary."""
        print("\n" + "="*70)
        print("BENCHMARK SUMMARY".center(70))
        print("="*70 + "\n")
        
        print("💻 System Information:")
        for key, value in self.results['system_info'].items():
            print(f"  {key:20s} {value}")
        print()
        
        print("⚡ Performance Scores:")
        
        # Calculate overall score
        scores = []
        
        if 'database' in self.results['benchmarks']:
            db = self.results['benchmarks']['database']
            if 'write_ops_per_sec' in db:
                db_score = min(100, db['write_ops_per_sec'] / 10)
                scores.append(db_score)
                print(f"  Database:      {db_score:5.1f}/100")
        
        if 'disk_io' in self.results['benchmarks']:
            io = self.results['benchmarks']['disk_io']
            if 'write_speed_mb_s' in io:
                io_score = min(100, io['write_speed_mb_s'] / 5)
                scores.append(io_score)
                print(f"  Disk I/O:      {io_score:5.1f}/100")
        
        if scores:
            overall = sum(scores) / len(scores)
            print(f"\n  Overall:       {overall:5.1f}/100")
        
        print()
    
    def export_results(self, output_file: str):
        """Export results to JSON."""
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✅ Results exported to: {output_file}\n")
    
    def compare_with_baseline(self, baseline_file: str):
        """Compare current results with baseline."""
        try:
            with open(baseline_file, 'r') as f:
                baseline = json.load(f)
            
            print("\n" + "="*70)
            print("COMPARISON WITH BASELINE".center(70))
            print("="*70 + "\n")
            
            # Compare database performance
            if 'database' in self.results['benchmarks'] and 'database' in baseline.get('benchmarks', {}):
                current_db = self.results['benchmarks']['database']
                baseline_db = baseline['benchmarks']['database']
                
                if 'write_ops_per_sec' in current_db and 'write_ops_per_sec' in baseline_db:
                    current = current_db['write_ops_per_sec']
                    base = baseline_db['write_ops_per_sec']
                    diff = ((current - base) / base) * 100
                    
                    print(f"Database Write:")
                    print(f"  Current:  {current:.0f} ops/s")
                    print(f"  Baseline: {base:.0f} ops/s")
                    print(f"  Change:   {diff:+.1f}%")
                    print()
            
            # Compare disk I/O
            if 'disk_io' in self.results['benchmarks'] and 'disk_io' in baseline.get('benchmarks', {}):
                current_io = self.results['benchmarks']['disk_io']
                baseline_io = baseline['benchmarks']['disk_io']
                
                if 'write_speed_mb_s' in current_io and 'write_speed_mb_s' in baseline_io:
                    current = current_io['write_speed_mb_s']
                    base = baseline_io['write_speed_mb_s']
                    diff = ((current - base) / base) * 100
                    
                    print(f"Disk Write:")
                    print(f"  Current:  {current:.1f} MB/s")
                    print(f"  Baseline: {base:.1f} MB/s")
                    print(f"  Change:   {diff:+.1f}%")
                    print()
        
        except FileNotFoundError:
            print(f"\nBaseline file not found: {baseline_file}")
        except Exception as e:
            print(f"\nError comparing with baseline: {str(e)}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Performance benchmark for AI Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full benchmark suite (slower)"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export results to JSON file"
    )
    
    parser.add_argument(
        "--compare",
        type=str,
        metavar="FILE",
        help="Compare with baseline results"
    )
    
    args = parser.parse_args()
    
    benchmark = PerformanceBenchmark()
    
    try:
        if args.full:
            benchmark.run_full_benchmark()
        else:
            benchmark.run_quick_benchmark()
        
        benchmark.display_summary()
        
        if args.export:
            benchmark.export_results(args.export)
        
        if args.compare:
            benchmark.compare_with_baseline(args.compare)
    
    except KeyboardInterrupt:
        print("\n\nBenchmark cancelled.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
