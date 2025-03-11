# YouTube Video Downloader Chrome Extension

A powerful Chrome extension for downloading YouTube videos with advanced quality selection and server integration.

## Features

- Download YouTube videos directly from your browser
- Choose video quality (1080p, 720p, 480p, 360p)
- Select output format (MP4, WebM)
- Context menu integration for quick downloads
- Desktop application with GUI interface
- RESTful API backend for video processing
- Cross-browser compatibility
- Enhanced error handling and logging
- Real-time download progress tracking
- Automatic format detection
- Configurable download settings
- Comprehensive logging system with debug options

## Project Structure

```
├── chrome_extension/        # Chrome extension files
│   ├── manifest.json       # Extension manifest
│   ├── background.js       # Background service worker
│   ├── popup.html         # Extension popup UI
│   └── popup.js           # Popup functionality
└── python_youtube_downloader/  # Python backend
    └── youtube_downloader.py   # Flask server & GUI app
```

## Setup Instructions

### Backend Server

1. Install Python dependencies:
   ```bash
   pip install flask flask-cors yt-dlp tk
   ```

2. Run the server:
   ```bash
   cd python_youtube_downloader
   python youtube_downloader.py
   ```

### Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `chrome_extension` directory

## Development

- Backend server runs on port 5000
- Extension communicates with the server via REST API
- GUI available for desktop usage when running locally
- Headless mode supported for server-only deployment
- Comprehensive error logging and handling
- Support for multiple video formats
- Cross-platform compatibility tested
- Detailed logging levels for debugging
- Configurable log output formats
- Error tracking and reporting

## License

MIT License