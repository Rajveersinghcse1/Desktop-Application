"""
GPU Detection and Setup Helper for AI Avatar Studio.

Helps users:
- Detect available GPUs
- Check CUDA installation
- Install GPU-enabled PyTorch
- Configure GPU settings
- Test GPU performance

Usage:
    python setup_gpu.py [command]

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import platform
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class GPUSetup:
    """Handles GPU detection and setup."""
    
    def __init__(self):
        """Initialize GPU setup helper."""
        self.system = platform.system()
    
    def detect_nvidia_gpu(self) -> Tuple[bool, List[Dict]]:
        """
        Detect NVIDIA GPUs.
        
        Returns:
            Tuple of (has_nvidia, gpu_list)
        """
        try:
            # Try nvidia-smi command
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                 "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                gpus = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 3:
                            gpus.append({
                                "name": parts[0],
                                "driver": parts[1],
                                "memory": parts[2]
                            })
                
                return True, gpus
            
            return False, []
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False, []
        except Exception as e:
            print(f"Error detecting GPU: {str(e)}")
            return False, []
    
    def check_cuda_version(self) -> Optional[str]:
        """
        Check CUDA version.
        
        Returns:
            CUDA version string or None
        """
        try:
            result = subprocess.run(
                ["nvcc", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse version from output
                for line in result.stdout.split('\n'):
                    if 'release' in line.lower():
                        parts = line.split('release')
                        if len(parts) > 1:
                            version = parts[1].split(',')[0].strip()
                            return version
            
            return None
            
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return None
    
    def check_pytorch_gpu(self) -> Tuple[bool, Optional[str]]:
        """
        Check if PyTorch has GPU support.
        
        Returns:
            Tuple of (has_gpu, cuda_version)
        """
        try:
            import torch
            
            if torch.cuda.is_available():
                cuda_version = torch.version.cuda
                device_count = torch.cuda.device_count()
                device_name = torch.cuda.get_device_name(0) if device_count > 0 else None
                
                return True, {
                    "cuda_version": cuda_version,
                    "device_count": device_count,
                    "device_name": device_name
                }
            
            return False, None
            
        except ImportError:
            return False, None
        except Exception as e:
            print(f"Error checking PyTorch: {str(e)}")
            return False, None
    
    def get_installation_command(self, cuda_version: Optional[str] = None) -> str:
        """
        Get PyTorch installation command for current system.
        
        Args:
            cuda_version: Specific CUDA version (e.g., "11.8")
        
        Returns:
            pip install command
        """
        if self.system == "Windows":
            if cuda_version:
                if cuda_version.startswith("11.8"):
                    return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                elif cuda_version.startswith("12.1"):
                    return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            
            # Default CUDA 11.8
            return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        
        elif self.system == "Linux":
            if cuda_version:
                if cuda_version.startswith("11.8"):
                    return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                elif cuda_version.startswith("12.1"):
                    return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"
            
            # Default CUDA 11.8
            return "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
        
        else:  # macOS
            return "pip install torch torchvision torchaudio"
    
    def test_gpu_performance(self) -> Dict:
        """
        Test GPU performance.
        
        Returns:
            Performance test results
        """
        try:
            import torch
            import time
            
            if not torch.cuda.is_available():
                return {"error": "No GPU available"}
            
            print("\n🔄 Running GPU performance test...\n")
            
            # Test matrix multiplication
            device = torch.device("cuda")
            size = 5000
            
            # Warm up
            a = torch.randn(size, size, device=device)
            b = torch.randn(size, size, device=device)
            _ = torch.matmul(a, b)
            torch.cuda.synchronize()
            
            # Timed test
            start = time.time()
            for _ in range(10):
                c = torch.matmul(a, b)
                torch.cuda.synchronize()
            gpu_time = (time.time() - start) / 10
            
            # Test on CPU for comparison
            a_cpu = a.cpu()
            b_cpu = b.cpu()
            start = time.time()
            _ = torch.matmul(a_cpu, b_cpu)
            cpu_time = time.time() - start
            
            speedup = cpu_time / gpu_time
            
            return {
                "gpu_time_ms": gpu_time * 1000,
                "cpu_time_ms": cpu_time * 1000,
                "speedup": speedup,
                "device": torch.cuda.get_device_name(0)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def diagnose(self) -> Dict:
        """
        Complete GPU diagnostic.
        
        Returns:
            Diagnostic results
        """
        print("\n" + "="*70)
        print("GPU DIAGNOSTIC")
        print("="*70 + "\n")
        
        results = {
            "system": self.system,
            "nvidia_gpu": None,
            "cuda_version": None,
            "pytorch_gpu": None,
            "recommendation": None
        }
        
        # Check NVIDIA GPU
        print("🔍 Checking for NVIDIA GPU...")
        has_nvidia, gpus = self.detect_nvidia_gpu()
        results["nvidia_gpu"] = {"detected": has_nvidia, "gpus": gpus}
        
        if has_nvidia:
            print("✅ NVIDIA GPU detected:")
            for gpu in gpus:
                print(f"   • {gpu['name']}")
                print(f"     Driver: {gpu['driver']}")
                print(f"     Memory: {gpu['memory']}")
        else:
            print("❌ No NVIDIA GPU detected")
        print()
        
        # Check CUDA
        print("🔍 Checking CUDA installation...")
        cuda_version = self.check_cuda_version()
        results["cuda_version"] = cuda_version
        
        if cuda_version:
            print(f"✅ CUDA installed: {cuda_version}")
        else:
            print("❌ CUDA not found (nvcc not in PATH)")
        print()
        
        # Check PyTorch GPU support
        print("🔍 Checking PyTorch GPU support...")
        has_pytorch_gpu, pytorch_info = self.check_pytorch_gpu()
        results["pytorch_gpu"] = {"available": has_pytorch_gpu, "info": pytorch_info}
        
        if has_pytorch_gpu:
            print("✅ PyTorch GPU support enabled:")
            print(f"   CUDA Version: {pytorch_info['cuda_version']}")
            print(f"   GPU Count: {pytorch_info['device_count']}")
            if pytorch_info['device_name']:
                print(f"   Device: {pytorch_info['device_name']}")
        else:
            print("❌ PyTorch GPU support not available")
        print()
        
        # Recommendations
        print("="*70)
        print("RECOMMENDATIONS")
        print("="*70 + "\n")
        
        if has_nvidia and cuda_version and has_pytorch_gpu:
            print("✅ GPU setup is complete!")
            print("   Your system is ready for GPU-accelerated generation.")
            results["recommendation"] = "ready"
        
        elif has_nvidia and cuda_version and not has_pytorch_gpu:
            print("⚠️  GPU detected but PyTorch needs GPU support")
            print("\nInstall GPU-enabled PyTorch:")
            install_cmd = self.get_installation_command(cuda_version)
            print(f"   {install_cmd}")
            results["recommendation"] = "install_pytorch_gpu"
        
        elif has_nvidia and not cuda_version:
            print("⚠️  GPU detected but CUDA not installed")
            print("\nInstall CUDA Toolkit:")
            print("   https://developer.nvidia.com/cuda-downloads")
            print("\nThen install GPU-enabled PyTorch:")
            install_cmd = self.get_installation_command()
            print(f"   {install_cmd}")
            results["recommendation"] = "install_cuda"
        
        else:
            print("ℹ️  No NVIDIA GPU detected")
            print("   Avatar Studio will use CPU (slower)")
            print("   Consider using a system with NVIDIA GPU for faster generation")
            results["recommendation"] = "cpu_only"
        
        print()
        
        return results
    
    def install_pytorch_gpu(self, cuda_version: Optional[str] = None) -> bool:
        """
        Install GPU-enabled PyTorch.
        
        Args:
            cuda_version: Specific CUDA version
        
        Returns:
            True if successful
        """
        install_cmd = self.get_installation_command(cuda_version)
        
        print(f"\n📦 Installing GPU-enabled PyTorch...\n")
        print(f"Command: {install_cmd}\n")
        
        response = input("Continue with installation? [Y/n]: ").strip().lower()
        if response and response != 'y':
            print("Cancelled.")
            return False
        
        try:
            # Run pip install
            result = subprocess.run(
                install_cmd.split(),
                check=True
            )
            
            print("\n✅ Installation completed!")
            print("\nVerifying GPU support...")
            
            # Verify
            has_gpu, info = self.check_pytorch_gpu()
            if has_gpu:
                print("✅ GPU support verified!")
                return True
            else:
                print("⚠️  GPU support not detected. Try restarting Python.")
                return False
        
        except subprocess.CalledProcessError as e:
            print(f"\n❌ Installation failed: {str(e)}")
            return False
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return False
    
    def benchmark(self) -> None:
        """Run GPU benchmark."""
        print("\n" + "="*70)
        print("GPU PERFORMANCE BENCHMARK")
        print("="*70 + "\n")
        
        result = self.test_gpu_performance()
        
        if "error" in result:
            print(f"❌ Benchmark failed: {result['error']}")
            return
        
        print(f"Device: {result['device']}")
        print(f"\nPerformance:")
        print(f"  GPU Time: {result['gpu_time_ms']:.2f} ms")
        print(f"  CPU Time: {result['cpu_time_ms']:.2f} ms")
        print(f"  Speedup: {result['speedup']:.1f}x")
        print()
        
        if result['speedup'] > 5:
            print("✅ Excellent GPU performance!")
        elif result['speedup'] > 2:
            print("✅ Good GPU performance")
        else:
            print("⚠️  Limited GPU speedup (check drivers/configuration)")
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="GPU Setup Helper for Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python setup_gpu.py diagnose      # Check GPU setup
  python setup_gpu.py install       # Install GPU PyTorch
  python setup_gpu.py benchmark     # Test GPU performance
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        choices=["diagnose", "install", "benchmark"],
        default="diagnose",
        help="Command to execute"
    )
    
    parser.add_argument(
        "--cuda-version",
        type=str,
        help="Specific CUDA version (e.g., 11.8, 12.1)"
    )
    
    args = parser.parse_args()
    
    setup = GPUSetup()
    
    try:
        if args.command == "diagnose":
            setup.diagnose()
        
        elif args.command == "install":
            setup.install_pytorch_gpu(cuda_version=args.cuda_version)
        
        elif args.command == "benchmark":
            setup.benchmark()
    
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
