"""
AI Avatar Studio - Setup Script

This script provides installation and distribution setup for the project.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read version
version_file = Path(__file__).parent / "version.py"
version_info = {}
exec(version_file.read_text(), version_info)

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text().splitlines() 
        if line.strip() and not line.startswith('#')
    ]

setup(
    name="ai-avatar-studio",
    version=version_info['__version__'],
    author=version_info['__author__'],
    author_email="contact@aiavatars.studio",
    description="Complete AI-powered talking avatar video generation system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-avatar-studio",
    packages=find_packages(exclude=['tests', 'tests.*', 'examples', 'docs']),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8,<3.12",
    install_requires=requirements,
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
            'sphinx>=6.0.0',
        ],
        'gpu': [
            'torch>=2.0.0',
            'torchvision>=0.15.0',
        ],
        'all': [
            'rembg>=2.0.0',  # Background removal
            'flask>=2.3.0',  # Web interface
            'fastapi>=0.100.0',  # API server
        ],
    },
    entry_points={
        'console_scripts': [
            'ai-avatar=main:main',
            'ai-avatar-generate=generate_video:main',
            'ai-avatar-monitor=monitor_generation:main',
            'ai-avatar-setup=quick_start:main',
            'ai-avatar-health=health_check:main',
            'ai-avatar-maintenance=maintenance:main',
        ],
    },
    include_package_data=True,
    package_data={
        '': [
            'config/*.py',
            '*.md',
            '*.txt',
            '.env.example',
        ],
    },
    project_urls={
        'Documentation': 'https://github.com/yourusername/ai-avatar-studio/docs',
        'Source': 'https://github.com/yourusername/ai-avatar-studio',
        'Bug Reports': 'https://github.com/yourusername/ai-avatar-studio/issues',
    },
    keywords='ai avatar video generation deep-learning lip-sync tts face-detection',
    zip_safe=False,
)
