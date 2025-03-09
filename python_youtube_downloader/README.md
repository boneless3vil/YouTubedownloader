# Enhanced YouTube Downloader

A feature-rich YouTube downloader with a graphical user interface that allows you to download videos in your preferred quality and format.

## Features

- Download videos with both video and audio
- Download video-only streams
- Download audio-only streams
- Select specific video quality and format
- Clipboard detection for YouTube URLs
- Download history tracking
- Progress bar with download status
- Customizable download settings
- **Enhanced Playlist Support**:
  - Download entire playlists
  - Select specific video ranges
  - Reverse download order option
  - Progress tracking for playlist downloads

## Requirements

- Python 3.11 or later
- pip (Python package manager)
- Windows, Linux, or macOS

## Installation

### Quick Start

1. Clone or download this repository
2. Open terminal/command prompt in the project directory
3. Run the installation script:
```bash
python install.py
```

### Manual Installation

If you prefer to set up manually:

1. Create a virtual environment:
```bash
# Windows
python -m venv yt-venv
.\yt-venv\Scripts\activate

# Linux/Mac
python -m venv yt-venv
source yt-venv/bin/activate
```

2. Install required packages:
```bash
pip install yt-dlp pyperclip
```

## Usage

1. Start the application:
```bash
python youtube_downloader.py
```

2. Basic Video Download:
   - Enter a YouTube URL or paste from clipboard
   - Select download type (Video+Audio, Video Only, Audio Only)
   - Click "Download" and select your preferred quality
   - Monitor progress in the status bar

3. Playlist Download:
   - Enter a YouTube playlist URL
   - Use playlist options:
     - "Download All Videos" to download entire playlist
     - Enter start/end indices for specific videos
     - Toggle "Reverse Order" to download in reverse
   - Click "Download" and select quality
   - Monitor progress for each video

4. Settings:
   - Click "Settings" to configure:
     - Download path
     - Default video format
   - Settings are saved automatically

5. History:
   - Click "History" to view past downloads
   - Includes timestamp, format, and status

## Troubleshooting

### Common Issues

1. **Application Won't Start**:
   - Verify Python 3.11+ is installed
   - Ensure virtual environment is activated
   - Check if required packages are installed

2. **Download Fails**:
   - Check internet connection
   - Verify YouTube URL is valid
   - Try a different video quality
   - Check download history for error details

3. **Playlist Issues**:
   - Ensure playlist URL is correct (should contain "list=" parameter)
   - Verify playlist is not private
   - Check start/end indices are valid numbers
   - Try downloading a single video first

4. **GUI Problems**:
   - Restart the application
   - Check for error messages in terminal
   - Verify display settings

### Getting Help

If you encounter issues:
1. Check the terminal for error messages
2. Review the download history
3. Verify your Python version and dependencies
4. Try reinstalling the required packages

## License

This project is open source and available under the MIT License.