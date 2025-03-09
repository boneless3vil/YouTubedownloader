import subprocess
import sys
import os

def check_python_version():
    if sys.version_info < (3, 11):
        print("Error: Python 3.11 or higher is required")
        sys.exit(1)

def install_package(package):
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package}")
        return False

def create_virtual_environment():
    print("Creating virtual environment...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "yt-venv"])
        print("Virtual environment created successfully")

        # Platform-specific activation instructions
        if os.name == 'nt':
            print("\nTo activate the virtual environment on Windows:")
            print("  .\\yt-venv\\Scripts\\activate")
            print("\nIf you get a PowerShell execution policy error, run:")
            print("  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser")
            print("\nTo build the Windows executable:")
            print("1. After activating the virtual environment")
            print("2. Run: python build.py")
            print("\nRequirements for Windows build:")
            print("- Visual Studio Build Tools with C++ components")
            print("- Administrator privileges")
        else:
            print("\nTo activate the virtual environment on Linux/Mac:")
            print("  source yt-venv/bin/activate")
            print("\nNote: Windows executable can only be built on Windows")
            print("To run the application directly:")
            print("  python youtube_downloader.py")

        return True
    except subprocess.CalledProcessError:
        print("Failed to create virtual environment")
        return False

def main():
    print("=== YouTube Downloader Installation ===")

    # Check Python version
    check_python_version()
    print("Python version check passed")

    # Create virtual environment
    if not create_virtual_environment():
        print("Error: Failed to create virtual environment")
        sys.exit(1)

    # Required packages
    packages = ['yt-dlp', 'pyperclip', 'pyinstaller']

    # Install packages
    all_success = True
    for package in packages:
        if not install_package(package):
            all_success = False

    if all_success:
        print("\nInstallation completed successfully!")

        if os.name == 'nt':
            print("\nTo build the Windows executable:")
            print("1. Activate the virtual environment (see instructions above)")
            print("2. Run: python build.py")
            print("\nThe build script will create YouTubeDownloader.exe in the dist folder")

        print("\nTo run without building:")
        print("1. Activate the virtual environment (see instructions above)")
        print("2. Run: python youtube_downloader.py")
    else:
        print("\nSome packages failed to install. Please try installing them manually:")
        print("pip install yt-dlp pyperclip pyinstaller")

if __name__ == "__main__":
    main()