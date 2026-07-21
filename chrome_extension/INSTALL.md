# Installing the Downstream Chrome Extension

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
     │   ├── icon16.png
     │   ├── icon48.png
     │   └── icon128.png
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

- The desktop application must be installed and running. The extension's
  server is **built into the desktop app** — starting `downstream.py`
  (or `Downstream.bat`) also starts the API the extension talks to
  at `http://localhost:47811`. There is nothing separate to install or run.
- To install the desktop app, run `python install.py` in the repository
  root — the installer can also open this extension setup for you.

## Troubleshooting

If the extension doesn't work:
1. Check that the desktop app is running (visit http://localhost:47811 in
   your browser — it should reply that the API is active)
2. Verify the extension is enabled in Chrome
3. Try refreshing the YouTube page
4. Check Chrome's console for any error messages