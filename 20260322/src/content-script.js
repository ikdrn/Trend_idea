/**
 * PackageGuard - Content Script
 * Extracts package info from npm/VSX pages and calculates security score
 */

function calculateSecurityScore(data) {
  let score = 50; // baseline

  // Download count / weekly factor (npm)
  if (data.weeklyDownloads) {
    if (data.weeklyDownloads > 100000) score += 15;
    else if (data.weeklyDownloads > 10000) score += 12;
    else if (data.weeklyDownloads > 1000) score += 8;
    else if (data.weeklyDownloads > 100) score += 5;
    else if (data.weeklyDownloads > 10) score += 2;
    else score -= 10;
  }

  // Last update recency
  if (data.lastUpdate) {
    const now = Date.now();
    const lastUpdateMs = new Date(data.lastUpdate).getTime();
    const daysAgo = (now - lastUpdateMs) / (1000 * 60 * 60 * 24);

    if (daysAgo < 7) score += 10;
    else if (daysAgo < 30) score += 5;
    else if (daysAgo < 180) score += 0;
    else if (daysAgo > 365 * 2) score -= 15; // 2 years unmaintained = risky
  }

  // Package creation recency (new packages = risky)
  if (data.createdAt) {
    const now = Date.now();
    const createdMs = new Date(data.createdAt).getTime();
    const daysOld = (now - createdMs) / (1000 * 60 * 60 * 24);

    if (daysOld < 7) score -= 20; // Very new = suspicious
    else if (daysOld < 30) score -= 10;
  }

  // GitHub stars (VSX or linked)
  if (data.githubStars) {
    if (data.githubStars > 1000) score += 12;
    else if (data.githubStars > 100) score += 8;
    else if (data.githubStars > 10) score += 4;
  }

  // License presence
  if (data.hasLicense !== false) score += 5;

  // README presence
  if (data.hasReadme !== false) score += 3;

  // Clamp score to 0-100
  score = Math.max(0, Math.min(100, score));
  return Math.round(score);
}

function getScoreColor(score) {
  if (score >= 70) return '#28a745'; // green
  if (score >= 40) return '#ffc107'; // yellow
  return '#dc3545'; // red
}

function getRiskBadge(data) {
  const badges = [];

  if (data.createdAt) {
    const daysOld = (Date.now() - new Date(data.createdAt).getTime()) / (1000 * 60 * 60 * 24);
    if (daysOld < 7) badges.push('⚠️ NEW');
  }

  if (data.lastUpdate) {
    const daysAgo = (Date.now() - new Date(data.lastUpdate).getTime()) / (1000 * 60 * 60 * 24);
    if (daysAgo > 365 * 2) badges.push('⚠️ UNMAINTAINED');
  }

  return badges.join(' ');
}

function extractNpmData() {
  // Extract from npm.com/package page
  const packageJson = document.querySelector('script[type="application/json"]');
  if (!packageJson) return null;

  try {
    const data = JSON.parse(packageJson.textContent);
    const pkg = data?.props?.pageProps?.pkg;

    if (!pkg) return null;

    return {
      name: pkg.name,
      weeklyDownloads: pkg.weekly?.downloads || 0,
      lastUpdate: pkg.lastUpdate,
      createdAt: pkg.created,
      hasLicense: pkg.license ? true : false,
      hasReadme: pkg.readme ? true : false,
      githubStars: pkg.githubRepo?.stars || 0
    };
  } catch (e) {
    console.error('Failed to parse npm data:', e);
    return null;
  }
}

function extractVSXData() {
  // Fallback: extract visible text from VSX marketplace
  const nameEl = document.querySelector('.item-name');
  const statsEl = document.querySelector('.stats-item');

  if (!nameEl) return null;

  return {
    name: nameEl.textContent.trim(),
    weeklyDownloads: 0, // VSX doesn't expose downloads easily
    lastUpdate: null,
    createdAt: null,
    hasLicense: document.querySelector('[data-license]') !== null,
    hasReadme: document.querySelector('.readme') !== null,
    githubStars: 0
  };
}

function injectScoreBadge(score, riskBadge) {
  // Target npm package header
  const headerEl = document.querySelector('.npm-package-header') ||
                   document.querySelector('h1') ||
                   document.querySelector('[data-testid="package-header"]');

  if (!headerEl) return;

  const badge = document.createElement('div');
  badge.id = 'packageguard-badge';
  badge.style.cssText = `
    display: inline-block;
    margin-left: 10px;
    padding: 6px 12px;
    background: ${getScoreColor(score)};
    color: white;
    border-radius: 4px;
    font-weight: bold;
    font-size: 14px;
    vertical-align: middle;
  `;
  badge.innerHTML = `🛡️ Security Score: <strong>${score}/100</strong>`;

  if (riskBadge) {
    badge.innerHTML += `<br><small>${riskBadge}</small>`;
  }

  headerEl.appendChild(badge);
}

// Main execution
function init() {
  let data = null;

  if (window.location.hostname.includes('npmjs.com')) {
    data = extractNpmData();
  } else if (window.location.hostname.includes('marketplace.visualstudio.com')) {
    data = extractVSXData();
  }

  if (data) {
    const score = calculateSecurityScore(data);
    const riskBadge = getRiskBadge(data);
    injectScoreBadge(score, riskBadge);

    // Also notify via storage for popup
    chrome.storage.local.set({
      lastPackage: {
        name: data.name,
        score: score,
        riskBadge: riskBadge,
        timestamp: Date.now()
      }
    });
  }
}

// Run after short delay to ensure DOM is ready
setTimeout(init, 500);
