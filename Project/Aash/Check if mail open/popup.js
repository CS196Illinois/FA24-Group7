document.addEventListener('DOMContentLoaded', function() {
  // Get the active tab
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    const currentTab = tabs[0];

    // Check if the URL includes "/inbox"
    if (currentTab.url.includes("/inbox")) {
      document.getElementById('status').textContent = 'You are in your Outlook inbox.';
    } else {
      document.getElementById('status').textContent = 'You are not in your Outlook inbox.';
    }
  });
});
