"""Setup configuration for OpenUP."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

# Read requirements
requirements_file = Path(__file__).parent / 'requirements.txt'
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip() 
        for line in requirements_file.read_text(encoding='utf-8').splitlines()
        if line.strip() and not line.startswith('#')
    ]

setup(
    name='openup',
    version='1.0.0',
    description='Universal File Preview & Visualization Application',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Rajveer Singh',
    author_email='support@openup.dev',
    url='https://github.com/Rajveersinghcse1/Web-dev',
    license='MIT',
    
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    
    install_requires=requirements,
    
    entry_points={
        'console_scripts': [
            'openup=main:main',
        ],
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',
    ],
    
    python_requires='>=3.11',
    
    include_package_data=True,
    
    keywords='file viewer preview visualization 3d geospatial medical data',
)
