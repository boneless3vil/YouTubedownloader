# YouTube Video Downloader Project

This project provides two implementations of a YouTube video downloader:
1. A desktop application built with Python and Tkinter
2. A Chrome extension for in-browser downloads

The two work together: the desktop app includes a small local API server
(`http://127.0.0.1:47811`, this machine only) that the Chrome extension sends
download requests to. The extension therefore requires the desktop app to be
installed and running; there is no separate server component.

## Getting started

```bash
cd python_youtube_downloader
python install.py
```

The interactive installer sets up everything needed at runtime (Python
packages, ffmpeg, Deno, download folder, launcher) and can optionally walk
you through installing the Chrome extension.

## Project Structure

```
.
├── python_youtube_downloader/    # Desktop application
│   ├── youtube_downloader.py     # Main application file
│   ├── build.py                 # Build script
│   ├── install.py               # Installation script
│   ├── settings.json            # Application settings
│   └── README.md               # Python app documentation
│
└── chrome_extension/            # Browser extension
    ├── manifest.json           # Extension manifest
    ├── popup.html             # Extension popup interface
    ├── popup.js              # Popup logic
    ├── content.js           # Content script
    ├── background.js       # Background script
    ├── README.md         # Extension documentation
    └── icons/             # Extension icons
        ├── icon16.png    
        ├── icon48.png   
        └── icon128.png 
```

## Components

### Python Desktop Application
A feature-rich desktop application with support for:
- Video and audio downloads
- Quality selection
- Playlist support
- Progress tracking
- Customizable settings

[View Python Application Documentation](python_youtube_downloader/README.md)

### Chrome Extension
A browser extension that provides:
- One-click downloads
- Preset quality preferences
- Direct YouTube integration
- Download progress tracking

[View Chrome Extension Documentation](chrome_extension/README.md)


## License

This project is open source and available under the MIT License.