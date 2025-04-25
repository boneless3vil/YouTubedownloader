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
  // Apply YouTube style button
  downloadBtn.style.background = 'none';
  downloadBtn.style.border = 'none';
  downloadBtn.style.cursor = 'pointer';
  downloadBtn.style.padding = '0';
  downloadBtn.style.margin = '0 8px';
  downloadBtn.innerHTML = `
    <div style="display: flex; align-items: center; padding: 8px 16px; cursor: pointer; color: #065fd4; font-family: 'Roboto', Arial, sans-serif; font-weight: 500; font-size: 14px;">
      <span style="margin-right: 6px;">⬇️</span>
      Start
    </div>
  `;

  // Add click handler
  downloadBtn.addEventListener('click', async () => {
    try {
      downloadBtn.innerHTML = `
        <div style="display: flex; align-items: center; padding: 8px 16px; color: #666; font-family: 'Roboto', Arial, sans-serif; font-weight: 500; font-size: 14px;">
          <span style="margin-right: 6px;">⏳</span>
          Starting...
        </div>
      `;

      const response = await chrome.runtime.sendMessage({
        action: 'download',
        url: window.location.href,
        options: {
          quality: 'highest',
          format: 'mp4'
        }
      });

      if (response && response.success) {
        downloadBtn.innerHTML = `
          <div style="display: flex; align-items: center; padding: 8px 16px; color: #065fd4; font-family: 'Roboto', Arial, sans-serif; font-weight: 500; font-size: 14px;">
            <span style="margin-right: 6px;">✅</span>
            Download Started
          </div>
        `;
      } else {
        const error = response ? response.error : 'Download failed';
        downloadBtn.innerHTML = `
          <div style="display: flex; align-items: center; padding: 8px 16px; color: #cc0000; font-family: 'Roboto', Arial, sans-serif; font-weight: 500; font-size: 14px;">
            <span style="margin-right: 6px;">❌</span>
            ${error}
          </div>
        `;
        console.error('Download error:', error);
      }
    } catch (error) {
      console.error('Failed to start download:', error);
      downloadBtn.innerHTML = `
        <div style="display: flex; align-items: center; padding: 8px 16px; color: #cc0000; font-family: 'Roboto', Arial, sans-serif; font-weight: 500; font-size: 14px;">
          <span style="margin-right: 6px;">❌</span>
          Server error
        </div>
      `;
    }
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