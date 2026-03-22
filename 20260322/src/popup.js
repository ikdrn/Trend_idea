/**
 * PackageGuard - Popup Script
 * Displays score and info for currently viewed package
 */

function getScoreColor(score) {
  if (score >= 70) return '#28a745';
  if (score >= 40) return '#ffc107';
  return '#dc3545';
}

function displayPackageInfo(pkg) {
  const display = document.getElementById('package-display');

  if (!pkg) {
    display.className = 'package-info empty';
    display.innerHTML = 'Navigate to npm.com or VSCode Marketplace to check a package security score.';
    return;
  }

  display.className = 'package-info';
  const fillColor = getScoreColor(pkg.score);

  let html = `
    <div class="package-name">${escapeHtml(pkg.name)}</div>
    <div class="score-bar">
      <div class="score-fill" style="width: ${pkg.score}%; background: ${fillColor};">
        ${pkg.score}/100
      </div>
    </div>
  `;

  if (pkg.riskBadge) {
    html += `<div class="risk-badge">${escapeHtml(pkg.riskBadge)}</div>`;
  }

  display.innerHTML = html;
}

function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

document.addEventListener('DOMContentLoaded', () => {
  // Load last viewed package
  chrome.storage.local.get('lastPackage', result => {
    const pkg = result.lastPackage;
    if (pkg && Date.now() - pkg.timestamp < 60000) {
      // Only show if less than 1 minute old
      displayPackageInfo(pkg);
    }
  });

  // Refresh button
  document.getElementById('btn-refresh').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (tabs[0]) {
        chrome.tabs.reload(tabs[0].id);
      }
    });
  });

  // Report button
  document.getElementById('btn-report').addEventListener('click', () => {
    chrome.tabs.create({
      url: 'https://github.com/issues/new?title=PackageGuard%20Report'
    });
  });
});
