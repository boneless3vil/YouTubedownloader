// Add download button to YouTube interface
function addDownloadButton() {
  const menu = document.querySelector('#top-level-buttons-computed');
  if (!menu || document.querySelector('.yt-download-btn')) return;

  const downloadButton = document.createElement('button');
  downloadButton.className = 'yt-download-btn';
  downloadButton.innerHTML = '⬇️ Download';
  downloadButton.style.cssText = `
    background: #ff0000;
    color: white;
    border: none;
    border-radius: 2px;
    padding: 8px 12px;
    margin-left: 8px;
    cursor: pointer;
    font-size: 14px;
  `;

  downloadButton.addEventListener('click', function() {
    // Show loading state
    downloadButton.disabled = true;
    downloadButton.innerHTML = '⏳ Starting...';

    // Send message to background script to start download
    chrome.runtime.sendMessage({
      action: 'downloadVideo',
      url: window.location.href
    });
  });

  menu.appendChild(downloadButton);
}

// Handle messages from background script
chrome.runtime.onMessage.addListener(function(message) {
  if (message.action === 'startDownload') {
    // Extension icon was clicked, trigger download button click
    const downloadButton = document.querySelector('.yt-download-btn');
    if (downloadButton && !downloadButton.disabled) {
      downloadButton.click();
    }
  } else {
    const button = document.querySelector('.yt-download-btn');
    if (!button) return;

    if (message.action === 'downloadStarted') {
      button.innerHTML = '✅ ' + message.message;
      setTimeout(() => {
        button.disabled = false;
        button.innerHTML = '⬇️ Download';
      }, 3000);
    } else if (message.action === 'downloadError') {
      button.innerHTML = '❌ ' + message.message;
      setTimeout(() => {
        button.disabled = false;
        button.innerHTML = '⬇️ Download';
      }, 3000);
    }
  }
});

// Watch for navigation changes (for YouTube's SPA behavior)
const observer = new MutationObserver(function(mutations) {
  if (window.location.pathname === '/watch') {
    addDownloadButton();
  }
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Initial check
if (window.location.pathname === '/watch') {
  addDownloadButton();
}