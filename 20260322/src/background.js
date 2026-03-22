/**
 * PackageGuard - Background Service Worker
 * Handles extension lifecycle and event coordination
 */

chrome.runtime.onInstalled.addListener(details => {
  if (details.reason === 'install') {
    chrome.tabs.create({
      url: 'https://www.npmjs.com/'
    });
  }
});

// Handle messages from content scripts if needed
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'updateScore') {
    // Could be extended for cross-tab communication
    chrome.storage.local.set({ lastPackage: request.data });
    sendResponse({ status: 'updated' });
  }
});
