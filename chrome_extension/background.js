// Background script for YouTube Video Downloader
const API_BASE_URL = 'https://' + chrome.runtime.getURL('').split('://')[1].split('/')[0];

// Set up context menu
chrome.runtime.onInstalled.addListener(() => {
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
    initiateDownload(request.url, request.options, sendResponse);
    return true; // Keep the message channel open for async response
  }
});

// Communication with Flask backend
async function initiateDownload(videoUrl, options = null) {
  try {
    console.log('Making request to:', `${API_BASE_URL}/download`);
    const response = await fetch(`${API_BASE_URL}/download`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        url: videoUrl,
        options: options || await chrome.storage.sync.get(['quality', 'format'])
      })
    });

    if (!response.ok) {
      throw new Error(`Server responded with status: ${response.status}`);
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