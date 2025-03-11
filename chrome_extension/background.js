// Background script for YouTube Video Downloader
let API_BASE_URL = '';

// Initialize API URL when extension loads
chrome.runtime.onInstalled.addListener(() => {
  // Set up context menu
  chrome.contextMenus.create({
    id: 'downloadVideo',
    title: 'Download Video',
    contexts: ['link', 'video'],
    documentUrlPatterns: ['*://*.youtube.com/*']
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'downloadVideo') {
    const videoUrl = info.linkUrl || info.pageUrl;
    initiateDownload(videoUrl);
  }
});

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'download') {
    initiateDownload(request.url, request.options)
      .then(response => sendResponse(response))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep the message channel open for async response
  }
});

// Communication with Flask backend
async function initiateDownload(videoUrl, options = null) {
  try {
    // Try localhost first for development
    const serverUrls = [
      'http://localhost:5000',
      'https://' + window.location.hostname
    ];

    let serverUrl = null;
    for (const url of serverUrls) {
      try {
        console.log('Attempting to connect to server at:', url);
        const healthCheck = await fetch(url, {
          headers: { 
            'Accept': 'application/json',
            'Origin': chrome.runtime.getURL('')
          }
        });

        if (healthCheck.ok) {
          const data = await healthCheck.json();
          console.log('Server response:', data);
          serverUrl = url;
          console.log('Successfully connected to server at:', url);
          break;
        }
      } catch (error) {
        console.log('Failed to connect to:', url, error);
      }
    }

    if (!serverUrl) {
      throw new Error('Server is not available. Please ensure the server is running.');
    }

    API_BASE_URL = serverUrl;

    const response = await fetch(`${API_BASE_URL}/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': chrome.runtime.getURL('')
      },
      body: JSON.stringify({ 
        url: videoUrl,
        options: options || await chrome.storage.sync.get(['quality', 'format'])
      })
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      throw new Error(errorData.error || `Server responded with status: ${response.status}`);
    }

    const data = await response.json();
    if (data.success) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon128.png',
        title: 'Download Started',
        message: 'Your video download has begun.'
      });
      return { success: true };
    } else {
      throw new Error(data.error || 'Download failed');
    }
  } catch (error) {
    console.error('Download error:', error);
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon128.png',
      title: 'Download Failed',
      message: error.message
    });
    return { success: false, error: error.message };
  }
}