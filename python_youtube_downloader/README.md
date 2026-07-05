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
- ffmpeg — required to merge video+audio and to convert audio-only downloads to MP3
- Deno (recommended) — yt-dlp uses it to run YouTube's player JavaScript; without it some formats are missing
- Windows, Linux, or macOS

## Installation

Run the interactive installer from this directory:

```bash
python install.py
```

It walks you through everything needed at runtime:

1. Checks your Python version
2. Creates a virtual environment (`.venv`) and installs the Python packages into it
3. Checks for ffmpeg and Deno, and offers to install them (via winget on Windows)
4. Asks where downloads should be saved (writes `settings.json`)
5. Creates `YouTube Downloader.bat` and an optional desktop shortcut (Windows)
6. Optionally helps you install the Chrome extension

Every prompt has a sensible default — pressing Enter through the installer gives a working setup.

### Manual Installation

If you prefer to set up manually:

```bash
python -m venv .venv
# Windows
.venv\Scripts\pip install yt-dlp pyperclip flask flask-cors
# Linux/Mac
.venv/bin/pip install yt-dlp pyperclip flask flask-cors
```

Then install ffmpeg (and ideally Deno) with your system's package manager.

## Usage

1. Start the application — double-click `YouTube Downloader.bat` (Windows), or run:
```bash
.venv\Scripts\python youtube_downloader.py
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

4. Settings (via the "Settings" button, or the window's title-bar icon menu at the top left):
   - Source folder for in-progress downloads (optional; finished files are moved to the destination)
   - Destination folder for finished downloads
   - Default download type (Video + Audio, Video Only, Audio Only)
   - Default video format

5. History:
   - Click "History" to view past downloads
   - Includes timestamp, format, and status

## Built-in server for the Chrome extension

The desktop app doubles as the backend for the companion Chrome extension —
there is no separate server to install or run. When the app starts, it also
starts a small API on `http://127.0.0.1:47811` (reachable only from this
machine). The extension sends the video URL and your preferences there, and
the desktop app performs the download.

- `GET /` — health check; the extension's downloads work only while the app is running
- `POST /api/download` — starts a download (`{"url": ..., "settings": {"downloadType": ..., "quality": ...}}`)

API downloads are saved to the destination folder configured in the app's
Settings. See [chrome_extension/INSTALL.md](../chrome_extension/INSTALL.md)
for installing the extension itself.

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