# Installing the YouTube Easy Downloader Chrome Extension

## Installation Steps

1. Download and Extract Files:
   - Download all the extension files
   - Keep the folder structure intact:
     ```
     chrome_extension/
     ├── manifest.json
     ├── background.js
     ├── content.js
     ├── icons/
     │   ├── icon16.svg
     │   ├── icon48.svg
     │   └── icon128.svg
     ```

2. Open Chrome Extensions Page:
   - Open Google Chrome
   - Type `chrome://extensions/` in the address bar
   - Press Enter

3. Enable Developer Mode:
   - Look for the "Developer mode" toggle in the top right corner
   - Turn it ON

4. Load the Extension:
   - Click the "Load unpacked" button that appears
   - Navigate to and select the `chrome_extension` folder
   - Click "Select Folder"

5. Verify Installation:
   - The extension icon should appear in your Chrome toolbar
   - If you don't see it, click the puzzle piece icon to find it
   - Pin the extension for easy access

## Usage

1. Single-Click Download:
   - Navigate to any YouTube video
   - Click the extension icon once
   - The video will download in best quality

2. Custom Settings (Right-Click Menu):
   - Right-click the extension icon
   - Select video quality (High/Medium/Low)
   - Choose download type:
     - Video + Audio
     - Video Only
     - Audio Only

## Requirements

- Make sure the Python server is running (`youtube_downloader.py`)
- The server must be accessible at `http://localhost:5000`
- Chrome browser must be able to connect to localhost

## Troubleshooting

If the extension doesn't work:
1. Check if Python server is running
2. Verify the extension is enabled in Chrome
3. Try refreshing the YouTube page
4. Check Chrome's console for any error messages