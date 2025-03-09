import PyInstaller.__main__
import os
import json
import sys
import shutil
from pathlib import Path

def check_windows_environment():
    """Check if we're running on Windows and have necessary prerequisites"""
    if os.name != 'nt':
        print("\nError: This build script must be run on Windows.")
        print("Please copy the project to a Windows system and run the build there.")
        print("\nBuild requirements on Windows:")
        print("1. Python 3.11 or higher")
        print("2. Visual Studio Build Tools with C++ components")
        print("3. Administrator privileges")
        sys.exit(1)

def create_default_settings():
    """Create default settings file if it doesn't exist"""
    default_settings = {
        "download_path": os.path.expanduser("~/Downloads"),
        "format": "mp4"
    }
    with open("settings.json", "w") as f:
        json.dump(default_settings, f)

def build_executable():
    """Build the Windows executable with proper configuration"""
    # Verify Windows environment first
    check_windows_environment()

    # Check Python version
    if sys.version_info < (3, 11):
        print("\nError: Python 3.11 or higher is required.")
        print("Please upgrade your Python installation.")
        sys.exit(1)

    print("\nPreparing to build YouTube Downloader for Windows...")

    # Ensure we're in the correct directory
    if not os.path.exists("youtube_downloader.py"):
        print("Error: youtube_downloader.py not found in current directory")
        print("Please run this script from the python_youtube_downloader directory")
        sys.exit(1)

    # Create default settings if it doesn't exist
    if not os.path.exists("settings.json"):
        print("Creating default settings.json...")
        create_default_settings()

    # Create Windows-specific runtime hook
    print("Creating Windows runtime hook...")
    with open('runtime-hook.py', 'w') as f:
        f.write('''
import os
import sys
import tkinter
import tkinter.ttk

def _find_tcl_tk():
    """Find and set TCL/TK paths for Windows executable"""
    import _tkinter
    tcl_dir = os.path.join(sys._MEIPASS, "tcl")
    tk_dir = os.path.join(sys._MEIPASS, "tk")

    if os.path.exists(tcl_dir) and os.path.exists(tk_dir):
        vers = [d for d in os.listdir(tcl_dir) if d.startswith('tcl')]
        if vers:
            tcl_vers = sorted(vers)[-1]  # Get latest version
            tk_vers = 'tk' + tcl_vers[3:]  # Corresponding tk version
            os.environ['TCL_LIBRARY'] = os.path.join(tcl_dir, tcl_vers)
            os.environ['TK_LIBRARY'] = os.path.join(tk_dir, tk_vers)
            return True
    return False

if os.name == 'nt':  # Windows-specific initialization
    try:
        if not _find_tcl_tk():
            print("Warning: Could not find bundled TCL/TK libraries")
        root = tkinter.Tk()
        root.withdraw()
    except Exception as e:
        print(f"Warning: Tkinter initialization error: {e}")
''')

    # Clear existing build and dist directories
    print("Cleaning previous build files...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)

    # Windows-specific PyInstaller options
    options = [
        'youtube_downloader.py',
        '--onefile',
        '--name=YouTubeDownloader',
        '--windowed',  # Windows GUI mode
        '--add-data=settings.json;.',  # Windows path separator
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=_tkinter',
        '--hidden-import=json',
        '--collect-all=yt_dlp',
        '--collect-all=pyperclip',
        '--runtime-hook=runtime-hook.py',
        '--clean',
        '--uac-admin',  # Request admin rights
        '--disable-windowed-traceback',
        '--noupx',  # More reliable than UPX compression
    ]

    # Add icon if available
    if os.path.exists("icon.ico"):
        options.append('--icon=icon.ico')

    try:
        print("\nStarting PyInstaller build process...")
        PyInstaller.__main__.run(options)

        # Verify the Windows executable was created
        exe_path = os.path.join('dist', 'YouTubeDownloader.exe')

        if os.path.exists(exe_path):
            print(f"\nBuild completed successfully!")
            print(f"Windows executable created at: {exe_path}")
            print("\nImportant notes for Windows users:")
            print("1. The executable must be run with administrator privileges")
            print("2. Keep the executable in a path without spaces")
            print("3. Some antivirus software may need to be temporarily disabled during first run")
            print("4. Make sure all Visual C++ redistributables are installed")
        else:
            raise FileNotFoundError("Windows executable not found after build")

    except Exception as e:
        print(f"\nError during Windows build: {str(e)}")
        print("\nWindows build troubleshooting steps:")
        print("1. Ensure all dependencies are installed (pip install pyinstaller yt-dlp pyperclip)")
        print("2. Install Visual C++ Redistributable for Visual Studio 2015-2022")
        print("3. Run from a directory path without spaces")
        print("4. Try running as administrator")
        print("5. Temporarily disable antivirus software")
        print("6. Clear the build and dist folders before rebuilding")
        sys.exit(1)

if __name__ == "__main__":
    build_executable()