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
      statusElement.textContent = 'Connecting to server...';
      statusElement.style.color = '#666';

      try {
        // Create a download button in popup that shows detailed status
        const downloadStatus = document.createElement('div');
        downloadStatus.style.marginTop = '10px';
        downloadStatus.style.padding = '5px';
        downloadStatus.style.border = '1px solid #ddd';
        downloadStatus.style.borderRadius = '4px';
        downloadStatus.style.fontSize = '12px';
        downloadStatus.innerHTML = `<strong>Server:</strong> Connecting...<br>
                                    <strong>URL:</strong> ${tab.url.substring(0, 30)}...<br>
                                    <strong>Quality:</strong> ${quality}<br>
                                    <strong>Format:</strong> ${format}`;
        document.body.appendChild(downloadStatus);
      
        // Use the background script to make the request
        chrome.runtime.sendMessage({
          action: 'download',
          url: tab.url,
          options: { quality, format }
        }, (response) => {
          if (chrome.runtime.lastError) {
            console.error('Chrome runtime error:', chrome.runtime.lastError);
            statusElement.textContent = `Error: ${chrome.runtime.lastError.message}`;
            statusElement.style.color = '#f44336';
            downloadStatus.innerHTML += `<br><strong>Error:</strong> ${chrome.runtime.lastError.message}`;
            downloadStatus.style.borderColor = '#f44336';
            return;
          }
          
          if (response && response.success) {
            statusElement.textContent = 'Download started successfully!';
            statusElement.style.color = '#4CAF50';
            downloadStatus.innerHTML += '<br><strong>Status:</strong> Download started ✓';
            downloadStatus.style.borderColor = '#4CAF50';
          } else {
            const error = response ? response.error : 'Download failed';
            statusElement.textContent = `Error: ${error}`;
            statusElement.style.color = '#f44336';
            downloadStatus.innerHTML += `<br><strong>Error:</strong> ${error}`;
            downloadStatus.style.borderColor = '#f44336';
            console.error('Download error:', error);
          }
        });
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