// Background script for YouTube Video Downloader
let API_BASE_URL = '';

// Initialize context menu and server URL
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: 'downloadVideo',
    title: 'Download Video',
    contexts: ['link', 'video'],
    documentUrlPatterns: ['*://*.youtube.com/*']
  });

  // Get server URL from the Replit domain
  API_BASE_URL = 'https://' + chrome.runtime.id + '.replit.app';
  console.log('Initial server URL:', API_BASE_URL);
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === 'downloadVideo') {
    const videoUrl = info.linkUrl || info.pageUrl;
    initiateDownload(videoUrl);
  }
});

// Handle messages from popup and content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'download') {
    initiateDownload(request.url, request.options)
      .then(response => sendResponse(response))
      .catch(error => {
        console.error('Download error:', error);
        sendResponse({ success: false, error: error.message });
      });
    return true; // Keep the message channel open for async response
  }
});

// Communication with Flask backend
async function initiateDownload(videoUrl, options = null) {
  try {
    console.log('Current API URL:', API_BASE_URL);
    console.log('Attempting download for:', videoUrl);

    // Get active tab URL to determine Replit domain
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab && tab.url.includes('replit.app')) {
      // Extract Replit domain from active tab
      const replitDomain = new URL(tab.url).origin;
      API_BASE_URL = replitDomain;
      console.log('Updated server URL to:', API_BASE_URL);
    }

    const response = await fetch(`${API_BASE_URL}/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ 
        url: videoUrl,
        options: options || await chrome.storage.sync.get(['quality', 'format'])
      })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    console.log('Server response:', data);

    if (data.success) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: '/icons/icon128.png',
        title: 'Download Started',
        message: 'Your video download has begun.'
      });
      return { success: true };
    } else {
      throw new Error(data.error || 'Download failed');
    }
  } catch (error) {
    console.error('Download failed:', error);
    chrome.notifications.create({
      type: 'basic',
      iconUrl: '/icons/icon128.png',
      title: 'Download Failed',
      message: error.message
    });
    return { success: false, error: error.message };
  }
}