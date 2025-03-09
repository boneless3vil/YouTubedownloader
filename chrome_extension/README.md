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

## Installation

### From Source (Developer Mode)
1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" using the toggle in the top right
3. Click "Load unpacked" and select this directory
4. The extension icon should appear in your Chrome toolbar

### Using Chrome Web Store
*(Coming soon)*

## Usage

1. Click the extension icon on any YouTube video page
2. First time setup:
   - Configure your preferred video quality
   - Choose default format (Video+Audio, Video Only, Audio Only)
   - Set download location preferences
3. For subsequent uses:
   - Simply click the download button that appears on YouTube pages
   - The video will download using your preset preferences

## Configuration

The extension can be configured through the popup menu:

### Download Settings
- Video Quality (Auto, High, Medium, Low)
- Format Preference (MP4, WebM, etc.)
- Audio Quality for audio-only downloads
- Default Download Type (Video+Audio, Video Only, Audio Only)

### Interface Settings
- Show download button on video pages
- Enable notifications
- Display download progress

## Permissions

This extension requires the following permissions:
- Storage (for saving preferences)
- ActiveTab (for accessing video information)
- Downloads (for saving videos)
- Host permissions for YouTube.com

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
