chrome.runtime.onInstalled.addListener(() => {
  // Create main context menu items
  chrome.contextMenus.create({
    id: 'download-type',
    title: 'Download Type',
    contexts: ['action']
  });

  // Download type options
  const downloadTypes = [
    {id: 'video-audio', title: 'Video + Audio', checked: true},
    {id: 'video-only', title: 'Video Only'},
    {id: 'audio-only', title: 'Audio Only'}
  ];

  downloadTypes.forEach(type => {
    chrome.contextMenus.create({
      id: type.id,
      parentId: 'download-type',
      title: type.title,
      type: 'radio',
      checked: type.checked,
      contexts: ['action']
    });
  });

  // Create quality submenu
  chrome.contextMenus.create({
    id: 'quality',
    title: 'Quality',
    contexts: ['action']
  });

  // Quality options
  const qualities = [
    {id: 'highest', title: 'High Quality', checked: true},
    {id: 'medium', title: 'Medium Quality'},
    {id: 'lowest', title: 'Low Quality'}
  ];

  qualities.forEach(quality => {
    chrome.contextMenus.create({
      id: quality.id,
      parentId: 'quality',
      title: quality.title,
      type: 'radio',
      checked: quality.checked,
      contexts: ['action']
    });
  });
});

// Store user preferences
let userPreferences = {
  downloadType: 'video-audio',
  quality: 'highest'
};

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info) => {
  if (info.parentMenuItemId === 'download-type') {
    userPreferences.downloadType = info.menuItemId;
  } else if (info.parentMenuItemId === 'quality') {
    userPreferences.quality = info.menuItemId;
  }
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  if (tab.url.includes('youtube.com/watch')) {
    chrome.tabs.sendMessage(tab.id, {
      action: 'startDownload',
      preferences: userPreferences
    });
  }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'downloadVideo') {
    // Send download request to Python server
    fetch('http://localhost:5000/api/download', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: request.url,
        settings: userPreferences
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        chrome.tabs.sendMessage(sender.tab.id, {
          action: 'downloadStarted',
          message: 'Download started successfully'
        });
      } else {
        throw new Error(data.error || 'Download failed');
      }
    })
    .catch(error => {
      chrome.tabs.sendMessage(sender.tab.id, {
        action: 'downloadError',
        message: error.message
      });
    });
  }
  return true;
});