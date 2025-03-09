document.addEventListener('DOMContentLoaded', function() {
  // Load saved settings
  chrome.storage.sync.get({
    downloadType: 'video+audio',
    quality: 'highest',
    format: 'mp4'
  }, function(items) {
    document.getElementById('downloadType').value = items.downloadType;
    document.getElementById('quality').value = items.quality;
    document.getElementById('format').value = items.format;
  });

  // Save settings
  document.getElementById('saveSettings').addEventListener('click', function() {
    const settings = {
      downloadType: document.getElementById('downloadType').value,
      quality: document.getElementById('quality').value,
      format: document.getElementById('format').value
    };

    chrome.storage.sync.set(settings, function() {
      const status = document.getElementById('status');
      status.textContent = 'Settings saved!';
      setTimeout(function() {
        status.textContent = '';
      }, 2000);
    });
  });
});
