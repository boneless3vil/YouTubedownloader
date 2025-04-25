import os
import sys
import shutil
import subprocess
import zipfile
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_directories():
    """Create necessary directories for build process"""
    build_dir = Path("build")
    dist_dir = build_dir / "dist"
    package_dir = build_dir / "youtube_downloader"
    
    # Create directories if they don't exist
    for directory in [build_dir, dist_dir, package_dir]:
        directory.mkdir(exist_ok=True)
        logger.info(f"Created directory: {directory}")
    
    return build_dir, dist_dir, package_dir

def copy_source_files(package_dir):
    """Copy source files to package directory"""
    # Copy the main script
    shutil.copy("youtube_downloader.py", package_dir / "youtube_downloader.py")
    
    # Create __init__.py to make it a proper package
    with open(package_dir / "__init__.py", "w") as f:
        f.write("# YouTube Downloader Package\n")
    
    # Create __main__.py for direct execution
    with open(package_dir / "__main__.py", "w") as f:
        f.write("from .youtube_downloader import main\n\nif __name__ == '__main__':\n    main()\n")
    
    # Create a run script for easy execution
    with open(package_dir / "run.py", "w") as f:
        f.write("#!/usr/bin/env python3\nfrom youtube_downloader import main\n\nif __name__ == '__main__':\n    main()\n")
    
    # Make run.py executable
    run_script = package_dir / "run.py"
    run_script.chmod(run_script.stat().st_mode | 0o111)  # Add executable bit
    
    logger.info("Source files copied to package directory")

def create_launcher_scripts(package_dir):
    """Create launcher scripts for different platforms"""
    # Windows batch file
    with open(package_dir / "run.bat", "w") as f:
        f.write("@echo off\npython run.py\n")
    
    # Linux/Mac shell script
    with open(package_dir / "run.sh", "w") as f:
        f.write("#!/bin/bash\npython3 run.py\n")
    
    # Make shell script executable
    shell_script = package_dir / "run.sh"
    shell_script.chmod(shell_script.stat().st_mode | 0o111)  # Add executable bit
    
    logger.info("Launcher scripts created")

def create_readme(package_dir):
    """Create README file with usage instructions"""
    with open(package_dir / "README.md", "w") as f:
        f.write("""# YouTube Downloader

A simple but powerful tool to download YouTube videos.

## Features

- Download YouTube videos in various formats and qualities
- Simple GUI interface for desktop use
- API server for integration with browser extensions
- Cross-platform support (Windows, macOS, Linux)

## Requirements

- Python 3.6+
- yt-dlp
- flask
- flask-cors
- tkinter (for GUI)

## Installation

1. Make sure Python 3.6+ is installed on your system
2. Install the required dependencies:
   ```
   pip install yt-dlp flask flask-cors
   ```
3. For GUI functionality, ensure Tkinter is installed (comes with most Python installations)

## Usage

### GUI Mode

Run the application with:

```
python run.py
```

This will start both the API server and the GUI interface if a display is available.

### Headless Mode

In headless environments, the app will run in API-only mode automatically.
The API server will start on port 5000 and accept download requests.

## API Endpoints

- `GET /`: Health check endpoint
- `POST /download`: Start a video download
  - Request body: `{"url": "YouTube URL", "options": {"quality": "highest", "format": "mp4"}}`

## License

MIT License
""")
    logger.info("README file created")

def create_setup_py(package_dir):
    """Create setup.py for pip installation"""
    with open(package_dir / "setup.py", "w") as f:
        f.write("""from setuptools import setup, find_packages

setup(
    name="youtube_downloader",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "yt-dlp",
        "flask",
        "flask-cors",
    ],
    entry_points={
        'console_scripts': [
            'youtube-downloader=youtube_downloader:main',
        ],
    },
    author="Replit User",
    description="A tool to download YouTube videos with GUI and API server",
    keywords="youtube, download, video, flask, api",
    python_requires=">=3.6",
)
""")
    logger.info("setup.py file created")

def create_requirements_txt(package_dir):
    """Create requirements.txt file"""
    with open(package_dir / "requirements.txt", "w") as f:
        f.write("yt-dlp>=2023.3.4\nflask>=2.0.0\nflask-cors>=3.0.10\n")
    logger.info("requirements.txt file created")

def create_zip_package(dist_dir, package_dir):
    """Create a zip file of the package"""
    zip_path = dist_dir / "youtube_downloader.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from the package directory to the zip
        for root, _, files in os.walk(package_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, os.path.dirname(package_dir))
                zipf.write(file_path, arcname)
    
    logger.info(f"Zip package created at: {zip_path}")
    return zip_path

def build_package():
    """Main build function"""
    logger.info("Starting build process...")
    
    # Create directories
    build_dir, dist_dir, package_dir = create_directories()
    
    # Copy source files
    copy_source_files(package_dir)
    
    # Create launcher scripts
    create_launcher_scripts(package_dir)
    
    # Create documentation
    create_readme(package_dir)
    
    # Create setup files
    create_setup_py(package_dir)
    create_requirements_txt(package_dir)
    
    # Create zip package
    zip_path = create_zip_package(dist_dir, package_dir)
    
    logger.info(f"Build completed successfully!")
    logger.info(f"Package available at: {zip_path}")
    
    return zip_path

if __name__ == "__main__":
    try:
        zip_path = build_package()
        print(f"\nPackage successfully built: {zip_path}")
        print("You can distribute this zip file to users who want to run the YouTube Downloader application.")
    except Exception as e:
        logger.error(f"Build failed: {str(e)}", exc_info=True)
        sys.exit(1)