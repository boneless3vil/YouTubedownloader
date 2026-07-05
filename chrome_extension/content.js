// Find a container that is actually rendered: YouTube's markup keeps old
// nodes around at zero size, so matching a selector is not enough - the
// element must have real dimensions or the button is invisible
function findVisibleContainer() {
  const candidates = [
    '#actions #top-level-buttons-computed',
    '#top-level-buttons-computed',
    '#actions ytd-menu-renderer',
    '#actions-inner',
    '#owner',
  ];
  for (const sel of candidates) {
    for (const el of document.querySelectorAll(sel)) {
      if (el.offsetWidth > 0 && el.offsetHeight > 0) return el;
    }
  }
  return null;
}

// Add download button to YouTube interface
function addDownloadButton() {
  const existing = document.querySelector('.yt-download-btn');
  // If the button exists but ended up in a hidden container after a SPA
  // navigation, re-place it
  if (existing) {
    if (existing.offsetWidth > 0) return;
    existing.remove();
  }
  const menu = findVisibleContainer();
  if (!menu) return;

  const downloadButton = document.createElement('button');
  downloadButton.className = 'yt-download-btn';
  downloadButton.innerHTML = '⬇️ Download';
  downloadButton.style.cssText = `
    background: #f00;
    color: white;
    border: none;
    border-radius: 18px;
    padding: 0 16px;
    height: 36px;
    margin-left: 8px;
    cursor: pointer;
    font-size: 14px;
    font-family: "Roboto", "Arial", sans-serif;
    flex-shrink: 0;
    align-self: center;
  `;

  downloadButton.addEventListener('click', function() {
    // Show loading state
    downloadButton.disabled = true;
    downloadButton.innerHTML = '⏳ Starting...';

    // Send message to background script to start download
    chrome.runtime.sendMessage({
      action: 'downloadVideo',
      url: window.location.href
    });
  });

  menu.appendChild(downloadButton);
}

// Handle messages from background script
chrome.runtime.onMessage.addListener(function(message) {
  if (message.action === 'startDownload') {
    // Extension icon was clicked, trigger download button click
    const downloadButton = document.querySelector('.yt-download-btn');
    if (downloadButton && !downloadButton.disabled) {
      downloadButton.click();
    }
  } else {
    const button = document.querySelector('.yt-download-btn');
    if (!button) return;

    if (message.action === 'downloadStarted') {
      button.innerHTML = '✅ ' + message.message;
      setTimeout(() => {
        button.disabled = false;
        button.innerHTML = '⬇️ Download';
      }, 3000);
    } else if (message.action === 'downloadError') {
      button.innerHTML = '❌ ' + message.message;
      setTimeout(() => {
        button.disabled = false;
        button.innerHTML = '⬇️ Download';
      }, 3000);
    }
  }
});

// Watch for navigation changes (for YouTube's SPA behavior). YouTube mutates
// the DOM constantly, so coalesce bursts into one check per 500ms instead of
// running on every mutation
let pending = null;
const observer = new MutationObserver(function() {
  if (pending || window.location.pathname !== '/watch') return;
  pending = setTimeout(function() {
    pending = null;
    if (window.location.pathname === '/watch') addDownloadButton();
  }, 500);
});

observer.observe(document.body, {
  childList: true,
  subtree: true
});

// Initial check
if (window.location.pathname === '/watch') {
  addDownloadButton();
}