# YouTube Easy Downloader - Chrome Extension

A convenient Chrome extension that adds one-click video download capabilities to YouTube pages with preconfigured quality settings.

## Features

- One-click video downloads
- Preset quality preferences
- Direct YouTube page integration
- Multiple format support
- Download progress indicator
- Seamless browser integration
- Configurable default settings

## How it works

The extension does not download videos by itself — it sends the video URL to
the desktop application, which does the downloading. The desktop app has a
small server **built in** at `http://localhost:5000` (local machine only);
starting the app starts the server, so there is nothing separate to install.
The desktop app must be running for the extension to work, and files are
saved by the desktop app to your Downloads folder.

## Installation

1. Install the desktop application first: run `python install.py` in the
   `python_youtube_downloader` folder (the installer offers to open this
   extension setup for you). See [INSTALL.md](INSTALL.md) for full steps.
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" using the toggle in the top right
4. Click "Load unpacked" and select this directory
5. The extension icon should appear in your Chrome toolbar

## Usage

1. Make sure the desktop application is running
2. Open any YouTube video page
3. Click the extension icon — the video downloads using your saved preferences

## Configuration

Right-click the extension icon to set your preferences (saved and synced by
Chrome):

- Download Type: Video + Audio, Video Only, or Audio Only
- Quality: High, Medium, or Low

## Permissions

This extension requires the following permissions:
- Storage (for saving preferences)
- ActiveTab / Scripting (for reading the current video URL)
- Context Menus (for the right-click preferences menu)
- Host permissions for youtube.com and `http://localhost:5000` (the desktop app's API)

## Development

To modify or enhance the extension:

1. Clone this repository
2. Make changes to the source files:
   - `manifest.json`: Extension configuration
   - `popup.html`: Extension popup interface
   - `popup.js`: Popup logic
   - `content.js`: YouTube page integration
   - `background.js`: Background processes
3. Test locally using Chrome's developer mode
4. Package for distribution if desired

## Troubleshooting

### Common Issues

1. **Download button not appearing**:
   - Refresh the YouTube page
   - Check if the extension is enabled
   - Verify YouTube URL permissions

2. **Downloads not starting**:
   - Check Chrome's download settings
   - Verify storage permissions
   - Ensure stable internet connection

3. **Quality selection not working**:
   - Clear extension storage
   - Reset preferences
   - Update the extension

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## License

This project is open source and available under the MIT License.
