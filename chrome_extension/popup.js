document.addEventListener('DOMContentLoaded', () => {
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
    if (tab && tab.url.includes('youtube.com')) {
      const quality = document.getElementById('quality').value;
      const format = document.getElementById('format').value;
      
      // Send download request to background script
      chrome.runtime.sendMessage({
        action: 'download',
        url: tab.url,
        options: { quality, format }
      });
    } else {
      alert('Please navigate to a YouTube video first.');
    }
  });
});
