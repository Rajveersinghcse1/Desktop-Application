#!/usr/bin/env python3
"""
Project templates for AI Avatar Studio.

Create projects from predefined templates for common use cases.

Usage:
    python project_templates.py --list
    python project_templates.py --create tutorial
    python project_templates.py --create marketing --output ./my_project

Author: AI Avatar Studio
Date: 2025-12-22
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


TEMPLATES = {
    'tutorial': {
        'name': 'Tutorial Video',
        'description': 'Educational tutorial with clear speech',
        'config': {
            'quality': 'high',
            'resolution': '1080p',
            'fps': 30,
            'tts_engine': 'gtts',
            'audio_enhancement': True,
            'noise_reduction': True
        },
        'example_script': """
# Tutorial Example

Welcome to this tutorial on Python programming.
Today, we'll learn about variables and data types.

Let's start with the basics.
A variable is a container for storing data values.
""".strip(),
        'tips': [
            'Use clear, professional headshot',
            'Speak slowly and clearly',
            'Break complex topics into segments',
            'Add pauses between sections'
        ]
    },
    
    'marketing': {
        'name': 'Marketing Video',
        'description': 'Promotional content with engaging delivery',
        'config': {
            'quality': 'high',
            'resolution': '1080p',
            'fps': 60,
            'tts_engine': 'coqui',
            'audio_enhancement': True,
            'noise_reduction': True
        },
        'example_script': """
# Marketing Example

Introducing our revolutionary new product!
Transform your workflow with cutting-edge technology.

Join thousands of satisfied customers today.
Limited time offer - Act now!
""".strip(),
        'tips': [
            'Use energetic, friendly expression',
            'Keep it concise (30-60 seconds)',
            'Clear call-to-action',
            'High production quality'
        ]
    },
    
    'news': {
        'name': 'News Report',
        'description': 'Professional news delivery',
        'config': {
            'quality': 'high',
            'resolution': '720p',
            'fps': 30,
            'tts_engine': 'pyttsx3',
            'audio_enhancement': False,
            'noise_reduction': False
        },
        'example_script': """
# News Report Example

Good evening. Here are today's top stories.

In technology news, a breakthrough in AI research...
The markets closed higher today...
And in sports, the championship game...

That's the news for tonight. Thank you for watching.
""".strip(),
        'tips': [
            'Neutral, professional expression',
            'Clear, authoritative voice',
            'Steady pacing',
            'Formal attire in photo'
        ]
    },
    
    'social_media': {
        'name': 'Social Media Post',
        'description': 'Short, engaging social media content',
        'config': {
            'quality': 'balanced',
            'resolution': '720p',
            'fps': 30,
            'tts_engine': 'gtts',
            'audio_enhancement': True,
            'noise_reduction': True
        },
        'example_script': """
# Social Media Example

Hey everyone!
Quick tip for today...

This simple trick will save you hours!
Try it out and let me know what you think!

Don't forget to like and subscribe!
""".strip(),
        'tips': [
            'Friendly, casual expression',
            'Keep it short (15-30 seconds)',
            'Engaging delivery',
            'Vertical format option'
        ]
    },
    
    'presentation': {
        'name': 'Business Presentation',
        'description': 'Professional business presentation',
        'config': {
            'quality': 'high',
            'resolution': '1080p',
            'fps': 30,
            'tts_engine': 'coqui',
            'audio_enhancement': True,
            'noise_reduction': True
        },
        'example_script': """
# Presentation Example

Good morning team.
Let's review this quarter's results.

Revenue increased by fifteen percent.
Customer satisfaction is at an all-time high.

Our strategy is working.
Let's continue this momentum.
""".strip(),
        'tips': [
            'Professional attire',
            'Confident, clear delivery',
            'Use data and facts',
            'Maintain eye contact'
        ]
    },
    
    'personal': {
        'name': 'Personal Message',
        'description': 'Personal greeting or message',
        'config': {
            'quality': 'balanced',
            'resolution': '720p',
            'fps': 30,
            'tts_engine': 'pyttsx3',
            'audio_enhancement': False,
            'noise_reduction': False
        },
        'example_script': """
# Personal Message Example

Hello!
I hope this message finds you well.

Thank you so much for your support.
It really means a lot to me.

Take care and talk soon!
""".strip(),
        'tips': [
            'Warm, friendly expression',
            'Natural, conversational tone',
            'Be authentic',
            'Show emotion'
        ]
    },
    
    'announcement': {
        'name': 'Public Announcement',
        'description': 'Formal public announcement',
        'config': {
            'quality': 'high',
            'resolution': '1080p',
            'fps': 30,
            'tts_engine': 'gtts',
            'audio_enhancement': True,
            'noise_reduction': True
        },
        'example_script': """
# Announcement Example

Attention all staff members.

Please be advised that the office will be closed
next Friday for maintenance.

Normal operations will resume on Monday.
Thank you for your cooperation.
""".strip(),
        'tips': [
            'Clear, authoritative tone',
            'Speak slowly for clarity',
            'Repeat important details',
            'Professional appearance'
        ]
    },
    
    'quick_test': {
        'name': 'Quick Test',
        'description': 'Fast test with low settings',
        'config': {
            'quality': 'fast',
            'resolution': '480p',
            'fps': 25,
            'tts_engine': 'pyttsx3',
            'audio_enhancement': False,
            'noise_reduction': False
        },
        'example_script': """
# Quick Test

This is a test video.
Testing one, two, three.
""".strip(),
        'tips': [
            'Use for quick validation',
            'Test setup before full production',
            'Check face detection',
            'Verify audio quality'
        ]
    }
}


class ProjectTemplates:
    """Manage project templates."""
    
    def __init__(self):
        """Initialize template manager."""
        self.base_dir = Path(__file__).parent
        self.templates = TEMPLATES
    
    def list_templates(self):
        """List all available templates."""
        print("\n" + "="*70)
        print("AVAILABLE TEMPLATES".center(70))
        print("="*70 + "\n")
        
        for key, template in self.templates.items():
            print(f"📋 {template['name']} ({key})")
            print(f"   {template['description']}")
            print(f"   Settings: {template['config']['quality']} quality, "
                  f"{template['config']['resolution']}, "
                  f"{template['config']['fps']} fps")
            print()
    
    def show_template_details(self, template_name: str):
        """Show detailed information about a template."""
        if template_name not in self.templates:
            print(f"❌ Template '{template_name}' not found")
            return
        
        template = self.templates[template_name]
        
        print("\n" + "="*70)
        print(f"{template['name']} TEMPLATE".center(70))
        print("="*70 + "\n")
        
        print(f"Description: {template['description']}\n")
        
        print("Configuration:")
        for key, value in template['config'].items():
            print(f"  {key:20s} {value}")
        print()
        
        print("Example Script:")
        print("-" * 70)
        print(template['example_script'])
        print("-" * 70)
        print()
        
        print("Tips:")
        for tip in template['tips']:
            print(f"  • {tip}")
        print()
    
    def create_project(self, template_name: str, output_dir: str = None):
        """
        Create a new project from template.
        
        Args:
            template_name: Template name
            output_dir: Output directory (default: ./projects/<template_name>)
        """
        if template_name not in self.templates:
            print(f"❌ Template '{template_name}' not found")
            return False
        
        template = self.templates[template_name]
        
        # Determine output directory
        if output_dir is None:
            output_dir = self.base_dir / "projects" / template_name
        else:
            output_dir = Path(output_dir)
        
        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Creating project in: {output_dir}\n")
        
        # Create config file
        config_file = output_dir / "config.json"
        with open(config_file, 'w') as f:
            json.dump(template['config'], f, indent=2)
        
        print(f"✅ Created: {config_file.name}")
        
        # Create script file
        script_file = output_dir / "script.txt"
        with open(script_file, 'w') as f:
            f.write(template['example_script'])
        
        print(f"✅ Created: {script_file.name}")
        
        # Create README
        readme_file = output_dir / "README.md"
        readme_content = f"""# {template['name']}

{template['description']}

## Configuration

This project uses the following settings:

"""
        
        for key, value in template['config'].items():
            readme_content += f"- **{key}**: {value}\n"
        
        readme_content += f"""
## Example Script

See `script.txt` for the example script.

## Tips

"""
        
        for tip in template['tips']:
            readme_content += f"- {tip}\n"
        
        readme_content += """
## Usage

1. Place your photo in this directory (e.g., `photo.jpg`)
2. Edit `script.txt` with your script
3. Generate video:

```bash
python ../generate_video.py -i photo.jpg -t "$(cat script.txt)" --quality {quality} --resolution {resolution}
```

Or use the config file:

```bash
python ../generate_video.py -i photo.jpg -t "$(cat script.txt)" --config config.json
```
""".format(
            quality=template['config']['quality'],
            resolution=template['config']['resolution']
        )
        
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print(f"✅ Created: {readme_file.name}")
        
        # Create placeholder for photo
        photo_placeholder = output_dir / "PUT_YOUR_PHOTO_HERE.txt"
        with open(photo_placeholder, 'w') as f:
            f.write("Place your photo in this directory.\n")
            f.write("Supported formats: .jpg, .jpeg, .png\n")
            f.write("Recommended: 512x512 or larger, clear face, good lighting\n")
        
        print(f"✅ Created: {photo_placeholder.name}")
        
        print("\n" + "="*70)
        print("✅ PROJECT CREATED SUCCESSFULLY!".center(70))
        print("="*70)
        print(f"\nProject location: {output_dir}")
        print(f"\nNext steps:")
        print(f"  1. Add your photo to: {output_dir}")
        print(f"  2. Edit script: {script_file}")
        print(f"  3. Generate video using commands in README.md")
        print()
        
        return True
    
    def create_custom_template(self, name: str, config: Dict):
        """Create a custom template."""
        # Validate config
        required_keys = ['quality', 'resolution', 'fps', 'tts_engine']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required config key: {key}")
                return False
        
        # Add to templates
        template_key = name.lower().replace(' ', '_')
        self.templates[template_key] = {
            'name': name,
            'description': 'Custom template',
            'config': config,
            'example_script': 'Add your script here.',
            'tips': ['Custom template']
        }
        
        # Save to file
        templates_file = self.base_dir / "custom_templates.json"
        
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                custom_templates = json.load(f)
        else:
            custom_templates = {}
        
        custom_templates[template_key] = self.templates[template_key]
        
        with open(templates_file, 'w') as f:
            json.dump(custom_templates, f, indent=2)
        
        print(f"\n✅ Custom template '{name}' created!")
        print(f"   Saved to: {templates_file}")
        print()
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Project templates for AI Avatar Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all templates
  python project_templates.py --list
  
  # Show template details
  python project_templates.py --details tutorial
  
  # Create project from template
  python project_templates.py --create tutorial
  
  # Create with custom output directory
  python project_templates.py --create marketing --output ./my_project
        """
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available templates"
    )
    
    parser.add_argument(
        "--details",
        type=str,
        metavar="TEMPLATE",
        help="Show detailed information about a template"
    )
    
    parser.add_argument(
        "--create",
        type=str,
        metavar="TEMPLATE",
        help="Create project from template"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        metavar="DIR",
        help="Output directory for created project"
    )
    
    args = parser.parse_args()
    
    manager = ProjectTemplates()
    
    try:
        if args.list:
            manager.list_templates()
        elif args.details:
            manager.show_template_details(args.details)
        elif args.create:
            manager.create_project(args.create, args.output)
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
