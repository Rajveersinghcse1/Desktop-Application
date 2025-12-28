#!/usr/bin/env python3
"""
Configuration wizard for AI Avatar Studio.

Interactive tool to configure the application.

Usage:
    python config_wizard.py
    python config_wizard.py --reset
    python config_wizard.py --export config.json

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


class ConfigWizard:
    """Interactive configuration wizard."""
    
    def __init__(self):
        """Initialize wizard."""
        self.base_dir = Path(__file__).parent
        self.env_file = self.base_dir / ".env"
        self.config = {}
    
    def print_header(self, title: str):
        """Print section header."""
        print("\n" + "="*70)
        print(title.center(70))
        print("="*70 + "\n")
    
    def get_input(
        self,
        prompt: str,
        default: Any = None,
        choices: Optional[list] = None,
        input_type: type = str
    ) -> Any:
        """
        Get user input with validation.
        
        Args:
            prompt: Input prompt
            default: Default value
            choices: List of valid choices
            input_type: Type to convert to
        
        Returns:
            User input value
        """
        while True:
            if default is not None:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "
            
            if choices:
                print(f"  Choices: {', '.join(str(c) for c in choices)}")
            
            user_input = input(full_prompt).strip()
            
            if not user_input and default is not None:
                return default
            
            if not user_input and default is None:
                print("  Error: Value required")
                continue
            
            if choices and user_input not in [str(c) for c in choices]:
                print(f"  Error: Must be one of: {', '.join(str(c) for c in choices)}")
                continue
            
            try:
                return input_type(user_input)
            except ValueError:
                print(f"  Error: Invalid {input_type.__name__}")
    
    def configure_general(self):
        """Configure general settings."""
        self.print_header("GENERAL SETTINGS")
        
        print("Application Settings:")
        
        self.config['APP_NAME'] = self.get_input(
            "Application name",
            default="AI Avatar Studio"
        )
        
        self.config['LOG_LEVEL'] = self.get_input(
            "Log level",
            default="INFO",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"]
        )
        
        self.config['AUTO_SAVE'] = self.get_input(
            "Auto-save projects",
            default="true",
            choices=["true", "false"]
        )
    
    def configure_paths(self):
        """Configure paths."""
        self.print_header("PATHS CONFIGURATION")
        
        print("Directory paths (use absolute paths or leave default):")
        
        self.config['OUTPUT_DIR'] = self.get_input(
            "Output directory",
            default="./output"
        )
        
        self.config['MODELS_DIR'] = self.get_input(
            "Models directory",
            default="./models"
        )
        
        self.config['TEMP_DIR'] = self.get_input(
            "Temporary directory",
            default="./temp"
        )
        
        self.config['LOGS_DIR'] = self.get_input(
            "Logs directory",
            default="./logs"
        )
    
    def configure_gpu(self):
        """Configure GPU settings."""
        self.print_header("GPU CONFIGURATION")
        
        # Check GPU availability
        try:
            import torch
            has_gpu = torch.cuda.is_available()
            if has_gpu:
                gpu_name = torch.cuda.get_device_name(0)
                print(f"✅ GPU detected: {gpu_name}\n")
                default_gpu = "true"
            else:
                print("ℹ️  No GPU detected\n")
                default_gpu = "false"
        except ImportError:
            print("⚠️  PyTorch not installed\n")
            default_gpu = "false"
        
        self.config['USE_GPU'] = self.get_input(
            "Enable GPU acceleration",
            default=default_gpu,
            choices=["true", "false"]
        )
        
        if self.config['USE_GPU'] == "true":
            self.config['CUDA_VISIBLE_DEVICES'] = self.get_input(
                "CUDA device ID",
                default="0"
            )
    
    def configure_video(self):
        """Configure video settings."""
        self.print_header("VIDEO CONFIGURATION")
        
        print("Default video settings:")
        
        self.config['DEFAULT_RESOLUTION'] = self.get_input(
            "Default resolution",
            default="720p",
            choices=["480p", "720p", "1080p", "4k"]
        )
        
        self.config['DEFAULT_QUALITY'] = self.get_input(
            "Default quality",
            default="balanced",
            choices=["fast", "balanced", "high"]
        )
        
        self.config['DEFAULT_VIDEO_FORMAT'] = self.get_input(
            "Default video format",
            default="mp4",
            choices=["mp4", "avi", "webm", "mkv"]
        )
        
        self.config['DEFAULT_FPS'] = self.get_input(
            "Default FPS",
            default="30",
            input_type=int
        )
    
    def configure_audio(self):
        """Configure audio settings."""
        self.print_header("AUDIO CONFIGURATION")
        
        print("Audio processing settings:")
        
        self.config['DEFAULT_TTS_ENGINE'] = self.get_input(
            "Default TTS engine",
            default="pyttsx3",
            choices=["pyttsx3", "gtts", "coqui"]
        )
        
        self.config['DEFAULT_TTS_VOICE'] = self.get_input(
            "Default TTS voice",
            default="default"
        )
        
        self.config['ENABLE_AUDIO_ENHANCEMENT'] = self.get_input(
            "Enable audio enhancement",
            default="true",
            choices=["true", "false"]
        )
        
        self.config['ENABLE_NOISE_REDUCTION'] = self.get_input(
            "Enable noise reduction",
            default="true",
            choices=["true", "false"]
        )
    
    def configure_advanced(self):
        """Configure advanced settings."""
        self.print_header("ADVANCED SETTINGS")
        
        print("Advanced options:")
        
        self.config['ENABLE_BACKGROUND_REMOVAL'] = self.get_input(
            "Enable background removal",
            default="false",
            choices=["true", "false"]
        )
        
        self.config['ENABLE_SUBTITLES'] = self.get_input(
            "Enable subtitle generation",
            default="false",
            choices=["true", "false"]
        )
        
        self.config['MAX_CONCURRENT_GENERATIONS'] = self.get_input(
            "Max concurrent generations",
            default="1",
            input_type=int
        )
        
        self.config['CACHE_ENABLED'] = self.get_input(
            "Enable caching",
            default="true",
            choices=["true", "false"]
        )
    
    def save_config(self):
        """Save configuration to .env file."""
        self.print_header("SAVING CONFIGURATION")
        
        # Backup existing config
        if self.env_file.exists():
            backup_file = self.env_file.with_suffix('.env.backup')
            import shutil
            shutil.copy(self.env_file, backup_file)
            print(f"✅ Backed up existing config to: {backup_file.name}")
        
        # Write new config
        with open(self.env_file, 'w') as f:
            f.write("# AI Avatar Studio Configuration\n")
            f.write(f"# Generated: {os.popen('date').read().strip()}\n\n")
            
            for key, value in self.config.items():
                f.write(f"{key}={value}\n")
        
        print(f"✅ Configuration saved to: {self.env_file.name}\n")
    
    def export_json(self, output_file: str):
        """Export configuration to JSON."""
        with open(output_file, 'w') as f:
            json.dump(self.config, f, indent=2)
        
        print(f"✅ Configuration exported to: {output_file}\n")
    
    def import_json(self, input_file: str):
        """Import configuration from JSON."""
        with open(input_file, 'r') as f:
            self.config = json.load(f)
        
        print(f"✅ Configuration imported from: {input_file}\n")
    
    def display_summary(self):
        """Display configuration summary."""
        self.print_header("CONFIGURATION SUMMARY")
        
        for key, value in self.config.items():
            print(f"  {key:35s} = {value}")
        
        print()
    
    def run_wizard(self):
        """Run complete configuration wizard."""
        print("\n" + "="*70)
        print("AI AVATAR STUDIO - CONFIGURATION WIZARD".center(70))
        print("="*70)
        print("\nThis wizard will guide you through configuring the application.")
        print("Press Ctrl+C at any time to cancel.\n")
        
        input("Press Enter to begin... ")
        
        # Run configuration steps
        self.configure_general()
        self.configure_paths()
        self.configure_gpu()
        self.configure_video()
        self.configure_audio()
        
        response = input("\nConfigure advanced settings? [y/N]: ").strip().lower()
        if response == 'y':
            self.configure_advanced()
        
        # Show summary
        self.display_summary()
        
        response = input("Save this configuration? [Y/n]: ").strip().lower()
        if response != 'n':
            self.save_config()
            
            print("\n" + "="*70)
            print("✅ CONFIGURATION COMPLETE!".center(70))
            print("="*70)
            print("\nYou can now start using AI Avatar Studio!")
            print("Run: python main.py\n")
        else:
            print("\nConfiguration not saved.")
    
    def reset_config(self):
        """Reset configuration to defaults."""
        self.print_header("RESET CONFIGURATION")
        
        response = input("Are you sure you want to reset to defaults? [y/N]: ").strip().lower()
        if response != 'y':
            print("Reset cancelled.")
            return
        
        # Backup current config
        if self.env_file.exists():
            backup_file = self.env_file.with_suffix('.env.old')
            import shutil
            shutil.copy(self.env_file, backup_file)
            print(f"✅ Backed up current config to: {backup_file.name}")
        
        # Copy from example
        example_file = self.base_dir / ".env.example"
        if example_file.exists():
            import shutil
            shutil.copy(example_file, self.env_file)
            print(f"✅ Reset to default configuration\n")
        else:
            print("⚠️  .env.example not found\n")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Configuration wizard for AI Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Reset configuration to defaults"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        metavar="FILE",
        help="Export current config to JSON"
    )
    
    parser.add_argument(
        "--import",
        dest="import_file",
        type=str,
        metavar="FILE",
        help="Import config from JSON"
    )
    
    args = parser.parse_args()
    
    wizard = ConfigWizard()
    
    try:
        if args.reset:
            wizard.reset_config()
        elif args.export:
            # Load current config first
            if wizard.env_file.exists():
                with open(wizard.env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            wizard.config[key] = value
            wizard.export_json(args.export)
        elif args.import_file:
            wizard.import_json(args.import_file)
            wizard.display_summary()
            response = input("\nSave this configuration? [Y/n]: ").strip().lower()
            if response != 'n':
                wizard.save_config()
        else:
            wizard.run_wizard()
    
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
