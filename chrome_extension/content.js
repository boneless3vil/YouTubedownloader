// Inject download button into YouTube page
function addDownloadButton() {
  // Check if we're on a video page
  if (!window.location.href.includes('youtube.com/watch')) return;

  // Remove existing button if any
  const existingBtn = document.getElementById('yt-downloader-btn');
  if (existingBtn) existingBtn.remove();

  // Find the like/dislike button row
  const menuContainer = document.querySelector('#top-level-buttons-computed');
  if (!menuContainer) return;

  // Create download button
  const downloadBtn = document.createElement('button');
  downloadBtn.id = 'yt-downloader-btn';
  downloadBtn.className = 'yt-downloader-btn';
  downloadBtn.innerHTML = `
    <div style="display: flex; align-items: center; padding: 8px 16px; cursor: pointer; color: #065fd4;">
      <span style="margin-right: 6px;">⬇️</span>
      Download
    </div>
  `;

  // Add click handler
  downloadBtn.addEventListener('click', () => {
    chrome.runtime.sendMessage({
      action: 'download',
      url: window.location.href,
      options: {
        quality: 'highest',
        format: 'mp4'
      }
    }, (response) => {
      if (response && response.success) {
        downloadBtn.innerHTML = `
          <div style="display: flex; align-items: center; padding: 8px 16px; color: #065fd4;">
            <span style="margin-right: 6px;">✅</span>
            Download Started
          </div>
        `;
      } else {
        const error = response ? response.error : 'Download failed';
        downloadBtn.innerHTML = `
          <div style="display: flex; align-items: center; padding: 8px 16px; color: #cc0000;">
            <span style="margin-right: 6px;">❌</span>
            ${error}
          </div>
        `;
      }
    });
  });

  // Insert button
  menuContainer.appendChild(downloadBtn);
}

// Run when page loads
addDownloadButton();

// Watch for navigation changes (YouTube is a SPA)
let lastUrl = location.href;
new MutationObserver(() => {
  if (location.href !== lastUrl) {
    lastUrl = location.href;
    setTimeout(addDownloadButton, 1000); // Wait for YouTube to update DOM
  }
}).observe(document, { subtree: true, childList: true });
