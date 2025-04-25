# YouTube Downloader - Packaged Version Guide

## Overview

This document explains how to use the packaged version of the YouTube Downloader application that you can distribute to users without requiring them to install the Chrome extension.

## Package Contents

The packaged version has been created at `python_youtube_downloader/build/dist/youtube_downloader.zip` and contains:

- The main YouTube downloader application
- A user-friendly GUI interface 
- An API server for integration with web tools
- Cross-platform support (Windows, macOS, Linux)
- Launcher scripts for different platforms

## Installation Instructions

### Prerequisites

- Python 3.6 or higher
- Required dependencies: yt-dlp, flask, flask-cors

### Steps

1. Extract the `youtube_downloader.zip` file to a directory of your choice.

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application using the appropriate launcher for your platform:
   - Windows: Double-click on `run.bat` or open a command prompt and run `python run.py`
   - Linux/macOS: Open a terminal, navigate to the extracted directory and run `./run.sh` or `python3 run.py`

## Usage

### GUI Mode

When started on a system with a display, the YouTube Downloader will open in GUI mode:

1. Enter a YouTube URL in the text field
2. Select your desired quality and format
3. Click "Download" to start the download
4. Monitor progress in the progress bar
5. Files will be saved to the `downloads` folder in the application directory

### API Server (Advanced)

The application also runs a Flask API server on port 5000, which can be used by web applications or extensions:

- Health check endpoint: http://localhost:5000/
- Download endpoint: http://localhost:5000/download (POST)

The download endpoint accepts POST requests with the following JSON structure:
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "options": {
    "quality": "highest",
    "format": "mp4"
  }
}
```

## Troubleshooting

- **Cannot start the application**: Make sure Python is installed and in your PATH
- **Download fails**: Check that you have a valid YouTube URL and internet connection
- **Missing dependencies**: Run `pip install -r requirements.txt` again
- **Permission denied**: On Linux/macOS, you may need to make the script executable with `chmod +x run.sh`

## Integration with Browser Extensions

The packaged version can be used alongside the Chrome extension by configuring the extension to connect to the local API server. This allows downloading videos directly from the YouTube page via the "Start" button or context menu.