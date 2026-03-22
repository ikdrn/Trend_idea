const express = require('express');
const path = require('path');
const fetch = require('node-fetch');
const cheerio = require('cheerio');

const app = express();
const PORT = process.env.PORT || 3000;

// Trend data store
let trendData = {
  repos: [],
  lastUpdated: new Date(),
  updateInterval: 3600000 // 1 hour
};

// Keyword-based classifier
const CLASSIFIERS = {
  aiAgent: [
    'agent', 'agentic', 'langchain', 'llm', 'gpt', 'claude', 'openai',
    'multiagent', 'framework', 'ai', 'ml', 'model', 'deepseek',
    'ollama', 'anthropic', 'tool', 'autonomous', 'reasoning',
    'sashiko', 'nemoclaw', 'openclaw', 'deerflow', 'picolm'
  ],
  security: [
    'security', 'cve', 'vulnerability', 'vulnerability', 'exploit',
    'malware', 'hack', 'audit', 'compliance', 'privacy', 'encryption',
    'crypto', 'ssl', 'tls', 'penetration', 'pentesting', 'scanner',
    'firewall', 'intrusion', 'detection'
  ],
  language: {
    python: ['python', 'py', 'typer', 'fastapi', 'django', 'flask'],
    javascript: ['javascript', 'js', 'typescript', 'ts', 'node', 'react', 'nextjs', 'svelte'],
    rust: ['rust', 'cargo', 'wasm', 'assembly', 'performance'],
    go: ['go', 'golang', 'cli'],
    other: []
  }
};

/**
 * Fetch and parse GitHub Trending
 */
async function fetchGitHubTrending() {
  try {
    const response = await fetch('https://github.com/trending', {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }
    });
    const html = await response.text();
    const $ = cheerio.load(html);

    const repos = [];

    $('article.Box-row').each((i, el) => {
      if (i >= 10) return; // Top 10 only

      const $el = $(el);
      const repoLink = $el.find('h2 a').attr('href')?.trim() || '';
      const description = $el.find('p.col-9').text().trim() || '';
      const language = $el.find('[itemprop="programmingLanguage"]').text().trim() || 'Unknown';
      const stars = $el.find('svg.octicon-star').parent().text().trim() || '0';

      if (repoLink) {
        repos.push({
          name: repoLink.replace(/^\//g, ''),
          url: `https://github.com${repoLink}`,
          description: description.substring(0, 120),
          language: language,
          stars: stars
        });
      }
    });

    return repos;
  } catch (err) {
    console.error('Error fetching GitHub Trending:', err.message);
    return [];
  }
}

/**
 * Calculate trend scores
 */
function classifyTrend(repo) {
  const text = `${repo.name} ${repo.description} ${repo.language}`.toLowerCase();

  // AI Agent score
  const aiAgentMatches = CLASSIFIERS.aiAgent.filter(kw => text.includes(kw)).length;
  const aiAgentScore = Math.min(100, aiAgentMatches * 15);

  // Security score
  const securityMatches = CLASSIFIERS.security.filter(kw => text.includes(kw)).length;
  const securityScore = Math.min(100, securityMatches * 20);

  // Language classification
  let langTag = 'Other';
  for (const [lang, keywords] of Object.entries(CLASSIFIERS.language)) {
    if (keywords.some(kw => text.includes(kw))) {
      langTag = lang.charAt(0).toUpperCase() + lang.slice(1);
      break;
    }
  }

  return {
    aiAgent: aiAgentScore,
    security: securityScore,
    language: langTag,
    trend: aiAgentScore > 30 ? 'AI Agent' : securityScore > 30 ? 'Security' : 'General'
  };
}

/**
 * Update trend data
 */
async function updateTrends() {
  console.log('[' + new Date().toISOString() + '] Updating trend data...');
  const repos = await fetchGitHubTrending();

  trendData.repos = repos.map(repo => ({
    ...repo,
    scores: classifyTrend(repo)
  }));

  trendData.lastUpdated = new Date();
  console.log(`[${new Date().toISOString()}] Updated ${repos.length} trending repos`);
}

// Initial update
updateTrends();

// Auto-update every 1 hour
setInterval(updateTrends, trendData.updateInterval);

// Routes
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
  const sortedRepos = [...trendData.repos].sort((a, b) => {
    return b.scores.aiAgent - a.scores.aiAgent;
  });

  res.render('index', {
    repos: sortedRepos,
    lastUpdated: trendData.lastUpdated.toLocaleString('ja-JP'),
    totalRepos: sortedRepos.length
  });
});

app.get('/api/trends', (req, res) => {
  res.json({
    repos: trendData.repos,
    lastUpdated: trendData.lastUpdated,
    summary: {
      total: trendData.repos.length,
      aiAgentCount: trendData.repos.filter(r => r.scores.trend === 'AI Agent').length,
      securityCount: trendData.repos.filter(r => r.scores.trend === 'Security').length,
      avgAiAgentScore: (trendData.repos.reduce((sum, r) => sum + r.scores.aiAgent, 0) / trendData.repos.length).toFixed(1)
    }
  });
});

app.listen(PORT, () => {
  console.log(`🚀 Agentic Trend Classifier running on http://localhost:${PORT}`);
  console.log(`📊 Dashboard: http://localhost:${PORT}/`);
  console.log(`📡 API: http://localhost:${PORT}/api/trends`);
});
