document.addEventListener('DOMContentLoaded', () => {
  const statusElement = document.createElement('div');
  statusElement.id = 'status';
  statusElement.style.marginTop = '10px';
  statusElement.style.color = '#666';
  document.body.appendChild(statusElement);

  // Load saved preferences
  chrome.storage.sync.get(['quality', 'format'], (items) => {
    if (items.quality) {
      document.getElementById('quality').value = items.quality;
    }
    if (items.format) {
      document.getElementById('format').value = items.format;
    }
  });

  // Save preferences when changed
  document.getElementById('quality').addEventListener('change', (e) => {
    chrome.storage.sync.set({ quality: e.target.value });
  });

  document.getElementById('format').addEventListener('change', (e) => {
    chrome.storage.sync.set({ format: e.target.value });
  });

  // Handle download button click
  document.getElementById('downloadBtn').addEventListener('click', async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url.includes('youtube.com/watch')) {
      const quality = document.getElementById('quality').value;
      const format = document.getElementById('format').value;
      statusElement.textContent = 'Starting download...';
      statusElement.style.color = '#666';

      try {
        const response = await fetch(`https://${window.location.hostname}/download`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            url: tab.url,
            options: { quality, format }
          })
        });

        const data = await response.json();
        if (data.success) {
          statusElement.textContent = 'Download started successfully!';
          statusElement.style.color = '#4CAF50';
        } else {
          throw new Error(data.error || 'Download failed');
        }
      } catch (error) {
        console.error('Download error:', error);
        statusElement.textContent = `Error: ${error.message}`;
        statusElement.style.color = '#f44336';
      }
    } else {
      statusElement.textContent = 'Please navigate to a YouTube video page first.';
      statusElement.style.color = '#f44336';
    }
  });
});