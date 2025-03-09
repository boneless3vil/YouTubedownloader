# YouTube Downloader - Windows Executable

A user-friendly YouTube video downloader with a graphical interface, packaged as a Windows executable.

## System Requirements

- Windows 10 or later
- At least 4GB RAM
- 500MB free disk space
- Internet connection
- Administrator privileges

## Prerequisites

The following components must be installed before running the executable:

1. **Visual C++ Redistributable**
   - Install "Microsoft Visual C++ Redistributable for Visual Studio 2015-2022"
   - Download from: [Microsoft's Official Download Page](https://aka.ms/vs/17/release/vc_redist.x64.exe)

## Installation

1. Download `YouTubeDownloader.exe` from the `dist` folder
2. Place the executable in a directory path without spaces
   - Good example: `C:\Programs\YouTubeDownloader`
   - Bad example: `C:\Program Files\YouTube Downloader`
3. First time setup:
   - Right-click the executable
   - Select "Run as administrator"
   - If Windows SmartScreen appears, click "More info" then "Run anyway"
   - You may need to temporarily disable antivirus software for the first run

## Usage

1. Launch the application:
   - Double-click `YouTubeDownloader.exe`
   - For the first run, use "Run as administrator"

2. Basic Video Download:
   - Paste a YouTube URL
   - Select download type (Video+Audio, Video Only, Audio Only)
   - Click "Download"
   - Choose your preferred quality
   - Monitor progress in the status bar

3. Playlist Download:
   - Paste a YouTube playlist URL
   - Use playlist options:
     - Download entire playlist
     - Select specific video ranges
     - Choose download order
   - Click "Download"
   - Select quality preferences

4. Settings:
   - Click "Settings" to configure:
     - Download path
     - Default video format
   - Settings are saved automatically

## Common Issues and Solutions

1. **Application Won't Start**
   - Run as administrator
   - Verify Visual C++ Redistributable is installed
   - Move to a path without spaces
   - Temporarily disable antivirus
   - Check Windows Event Viewer for errors

2. **Download Fails**
   - Check internet connection
   - Verify YouTube URL is valid
   - Try a different video quality
   - Check download history for error details

3. **GUI Problems**
   - Ensure running from a proper path
   - Run as administrator
   - Check display scaling settings
   - Reinstall Visual C++ Redistributable

4. **Download Path Issues**
   - Use Settings to set a valid download path
   - Avoid restricted folders
   - Ensure write permissions
   - Use forward slashes in paths

## Notes

- The application creates a settings file in its directory
- Download history is maintained in the same folder
- Some antivirus software may flag the executable
- Age-restricted videos require proper configuration

## Support

If you encounter issues:
1. Check the application's download history
2. Verify system requirements
3. Try running as administrator
4. Ensure all prerequisites are installed

## Legal Notice

This application is for personal use only. Respect YouTube's terms of service and content creators' rights.

## License

This project is open source and available under the MIT License.
