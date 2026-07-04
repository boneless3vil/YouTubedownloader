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

const defaultPreferences = {
  downloadType: 'video-audio',
  quality: 'highest'
};

// Preferences live in chrome.storage.sync (shared with the popup) — a plain
// variable would reset every time the MV3 service worker is unloaded
async function getPreferences() {
  const prefs = await chrome.storage.sync.get(defaultPreferences);
  if (prefs.downloadType === 'video+audio') {
    prefs.downloadType = 'video-audio';
  }
  return prefs;
}

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info) => {
  if (info.parentMenuItemId === 'download-type') {
    chrome.storage.sync.set({downloadType: info.menuItemId});
  } else if (info.parentMenuItemId === 'quality') {
    chrome.storage.sync.set({quality: info.menuItemId});
  }
});

// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  if (tab.url && tab.url.includes('youtube.com/watch')) {
    chrome.tabs.sendMessage(tab.id, {
      action: 'startDownload',
      preferences: await getPreferences()
    });
  }
});

// Handle messages from content script
chrome.runtime.onMessage.addListener((request, sender) => {
  if (request.action === 'downloadVideo') {
    getPreferences()
      .then(preferences => fetch('http://localhost:5000/api/download', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          url: request.url,
          settings: preferences
        })
      }))
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
});
