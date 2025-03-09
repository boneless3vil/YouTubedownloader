# === YouTube Video Downloader with Clipboard Auto-Paste & Fixed Exit ===

# Global settings
$global:ytDlpPath = "yt-dlp"             # Use full path if not in your PATH.
$global:downloadFormat = "mp4"            # Desired output container (e.g., mp4, mkv)

# Set the default download folder to the current user's Downloads folder
$downloadFolder = "$env:USERPROFILE\Downloads"

function Show-Menu {
    Write-Host "=== YouTube Video Downloader ==="
    Write-Host "1. Download YouTube Video"
    Write-Host "2. Change Settings"
    Write-Host "3. Exit"
}

function Download-Video {
    # Attempt to retrieve clipboard content
    try {
        $clipboardContent = Get-Clipboard -Raw
    }
    catch {
        $clipboardContent = ""
    }
    
    # Check if clipboard content is a YouTube URL
    if ($clipboardContent -match "^(https?://)?(www\.)?(youtube\.com|youtu\.be)") {
        Write-Host "Detected YouTube URL in clipboard:" $clipboardContent
        $url = $clipboardContent
    }
    else {
        $url = Read-Host "Enter YouTube URL"
    }

    if ([string]::IsNullOrWhiteSpace($url)) {
        Write-Host "URL cannot be empty. Please try again."
        return
    }

    Write-Host "Retrieving and downloading high quality streams, please wait..."
    
    # Build the output template using the default download folder
    $outputTemplate = "$downloadFolder\%(title)s.%(ext)s"
    $command = "$global:ytDlpPath -f bestvideo+bestaudio --merge-output-format $global:downloadFormat -o `"$outputTemplate`" `"$url`""
    
    Write-Host "Executing: $command"
    
    try {
        Invoke-Expression $command
    }
    catch {
        Write-Host "An error occurred during the download process: $_"
    }
}

function Change-Settings {
    Write-Host "=== Change Settings ==="
    Write-Host "1. Set yt-dlp path"
    Write-Host "2. Set output format (default: mp4)"
    Write-Host "3. Back"
    $choice = Read-Host "Select an option (1-3)"
    switch ($choice) {
        "1" {
            $newPath = Read-Host "Enter the full path to the yt-dlp executable (or type 'yt-dlp' if it is in your PATH)"
            if (-not [string]::IsNullOrEmpty($newPath)) {
                $global:ytDlpPath = $newPath
                Write-Host "yt-dlp path updated to: $global:ytDlpPath"
            }
        }
        "2" {
            $newFormat = Read-Host "Enter desired output format (e.g., mp4, mkv)"
            if (-not [string]::IsNullOrEmpty($newFormat)) {
                $global:downloadFormat = $newFormat
                Write-Host "Output format updated to: $global:downloadFormat"
            }
        }
        "3" {
            return
        }
        default {
            Write-Host "Invalid selection. Returning to main menu."
        }
    }
}

# Main loop
while ($true) {
    Show-Menu
    $option = Read-Host "Select an option (1-3)"
    switch ($option) {
        "1" {
            Download-Video
        }
        "2" {
            Change-Settings
        }
        "3" {
            Write-Host "Exiting..."
            exit
        }
        default {
            Write-Host "Invalid selection. Please try again."
        }
    }
}
