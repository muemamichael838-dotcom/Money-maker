// ── Model Catalogs ──
const MODEL_CATALOGS = {
  "LLM_MODEL": {
    "Anthropic": [
      "anthropic/claude-3-5-sonnet",
      "anthropic/claude-3-opus",
      "anthropic/claude-3-haiku"
    ],
    "Gemini": [
      "gemini/gemini-2.0-flash",
      "gemini/gemini-1.5-pro",
      "gemini/gemini-1.5-flash"
    ],
    "OpenAI": [
      "openai/gpt-4o",
      "openai/gpt-4o-mini",
      "openai/o1-preview"
    ],
    "Groq": [
      "groq/llama-3.3-70b-versatile",
      "groq/mixtral-8x7b-32768",
      "groq/gemma2-9b-it"
    ],
    "DeepSeek": [
      "deepseek/deepseek-chat",
      "deepseek/deepseek-reasoner"
    ],
    "HuggingFace": [
      "huggingface/meta-llama/Llama-3.3-70B-Instruct",
      "huggingface/Qwen/Qwen2.5-72B-Instruct"
    ],
    "Custom": [
      "custom"
    ]
  }
};

const ICONS = {
  "All":       "🌐",
  "Core":      "⚡",
  "Backup":    "💾",
  "Telegram":  "📱",
  "Terminal":  "💻",
  "Providers": "🔑",
  "Cloudflare":"☁️",
  "Advanced":  "⚙️",
  "Custom Env":"🔧"
};

const FIELDS = [
  // ── Core ──
  {
    "g": "Core", "icon": "⚡",
    "k": "GATEWAY_TOKEN",
    "lbl": "Gateway token — protects the Money Maker 🤑 web UI",
    "type": "password", "secret": 1, "common": 1, "tag": "critical"
  },
  {
    "g": "Core", "icon": "⚡",
    "k": "LLM_MODEL",
    "lbl": "Default model (provider/model-name format)",
    "type": "model", "options_key": "LLM_MODEL",
    "ph": "groq/llama-3.3-70b-versatile", "common": 1, "tag": "critical"
  },
  {
    "g": "Core", "icon": "⚡",
    "k": "POSTGRES_URL",
    "lbl": "Postgres/Supabase connection string (enables persistent memory)",
    "type": "password", "secret": 1, "common": 1, "tag": "optional"
  },

  // ── Backup ──
  {
    "g": "Backup", "icon": "💾",
    "k": "HF_TOKEN",
    "lbl": "HuggingFace token — enables state backup to a private dataset",
    "type": "password", "secret": 1, "common": 1, "tag": "credential"
  },
  {
    "g": "Backup", "icon": "💾",
    "k": "BACKUP_DATASET_NAME",
    "lbl": "Name of the HF dataset used for backups",
    "type": "text", "ph": "money-maker-memory", "common": 1, "tag": "optional"
  },

  // ── Providers ──
  {
    "g": "Providers", "icon": "🔑",
    "k": "GROQ_API_KEYS",
    "lbl": "Groq API keys (comma-separated pool for failover)",
    "type": "password", "secret": 1, "tag": "credential"
  },
  {
    "g": "Providers", "icon": "🔑",
    "k": "GOOGLE_API_KEYS",
    "lbl": "Google/Gemini API keys (comma-separated pool)",
    "type": "password", "secret": 1, "tag": "credential"
  },
  {
    "g": "Providers", "icon": "🔑",
    "k": "HUGGINGFACE_API_KEYS",
    "lbl": "Hugging Face API keys (comma-separated pool)",
    "type": "password", "secret": 1, "tag": "credential"
  },
  {
    "g": "Providers", "icon": "🔑",
    "k": "OPENAI_API_KEYS",
    "lbl": "OpenAI API keys (comma-separated pool)",
    "type": "password", "secret": 1, "tag": "credential"
  },
  {
    "g": "Providers", "icon": "🔑",
    "k": "ANTHROPIC_API_KEYS",
    "lbl": "Anthropic API keys (comma-separated pool)",
    "type": "password", "secret": 1, "tag": "credential"
  },
  {
    "g": "Providers", "icon": "🔑",
    "k": "ODDS_API_KEYS",
    "lbl": "Odds API keys (comma-separated pool for betting skills)",
    "type": "password", "secret": 1, "tag": "credential"
  },
  {
    "g": "Providers", "icon": "🔑",
    "k": "APIFY_TOKEN",
    "lbl": "Apify token (for advanced web scraping)",
    "type": "password", "secret": 1, "tag": "credential"
  },

  // ── Telegram ──
  {
    "g": "Telegram", "icon": "📱",
    "k": "TELEGRAM_BOT_TOKEN",
    "lbl": "Telegram bot token from @BotFather",
    "type": "password", "secret": 1, "common": 1, "tag": "credential"
  },
  {
    "g": "Telegram", "icon": "📱",
    "k": "TELEGRAM_ALLOWED_USERS",
    "lbl": "Allowed Telegram user IDs (comma-separated)",
    "type": "text", "ph": "123456789", "common": 1, "tag": "feature"
  },

  // ── Terminal ──
  {
    "g": "Terminal", "icon": "💻",
    "k": "DEV_MODE",
    "lbl": "Enable root-access terminal (JupyterLab)",
    "type": "toggle", "ph": "true", "common": 1, "tag": "feature"
  },

  // ── Advanced ──
  {
    "g": "Advanced", "icon": "⚙️",
    "k": "AUTO_SKILL_CREATION",
    "lbl": "Allow agent to create its own Python skills",
    "type": "toggle", "ph": "true", "tag": "feature"
  }
];

const BUNDLE_KEY = 'MONEY_MAKER_ENV_BUNDLE';
const $ = id => document.getElementById(id);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[c]));
const safeKey = k => /^[A-Z_][A-Z0-9_]*$/.test(k) && ![BUNDLE_KEY, 'ENV_BUNDLE'].includes(k);

function encodeBundle(obj) {
  const j = JSON.stringify(obj);
  let b = '';
  for (const x of new TextEncoder().encode(j)) b += String.fromCharCode(x);
  return btoa(b).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

function decodeBundle(raw) {
  try {
    raw = String(raw || '').trim();
    if (!raw) return {};
    if (raw.includes(BUNDLE_KEY + '=')) raw = raw.split(BUNDLE_KEY + '=').pop().trim();
    if ((raw.startsWith('"') && raw.endsWith('"')) || (raw.startsWith("'") && raw.endsWith("'"))) raw = raw.slice(1, -1);
    const p = raw + '='.repeat((4 - raw.length % 4) % 4);
    const b = atob(p.replace(/-/g, '+').replace(/_/g, '/'));
    const bytes = Uint8Array.from(b, c => c.charCodeAt(0));
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch { return {}; }
}

function parseEnv(text) {
  text = String(text || '').trim();
  if (!text) return {};
  if (text.startsWith('{') || /^[A-Za-z0-9_-]{20,}$/.test(text) || text.includes(BUNDLE_KEY + '=')) {
    return decodeBundle(text);
  }
  const out = {};
  for (let line of text.split(/\r?\n/)) {
    line = line.trim();
    if (!line || line.startsWith('#')) continue;
    const i = line.indexOf('=');
    if (i < 1) continue;
    const key = line.slice(0, i).trim();
    let val = line.slice(i + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) val = val.slice(1, -1);
    if (safeKey(key)) out[key] = val;
  }
  return out;
}

function showToast(msg = 'Copied!') {
  const t = $('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 1500);
}

let activeGroup = 'All';
let customCount = 0;
const GROUPS = ['All', ...[...new Set(FIELDS.map(f => f.g))], 'Custom Env'];

function renderSidebar() {
  const sb = $('sidebar');
  if (!sb) return;
  sb.innerHTML = '<div class="sb-label">Groups</div>';
  GROUPS.forEach(g => {
    const btn = document.createElement('button');
    btn.className = 'nav-btn' + (activeGroup === g ? ' active' : '');
    btn.dataset.group = g;
    const id = 'nc_' + g.replace(/\W/g, '_');
    btn.innerHTML = `<span class="nav-icon">${ICONS[g] || '📁'}</span><span class="nav-label">${esc(g)}</span><span class="nav-count" id="${id}">0</span>`;
    btn.onclick = () => { activeGroup = g; renderSidebar(); filter(); };
    sb.appendChild(btn);
  });
}

function renderOptionsHTML(field) {
  if (field.options_key === 'LLM_MODEL') {
    const groups = MODEL_CATALOGS.LLM_MODEL || {};
    return Object.entries(groups).map(([group, items]) => {
      const options = items.map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
      return `<optgroup label="${esc(group)}">${options}</optgroup>`;
    }).join('');
  }
  return (field.options || []).map(v => `<option value="${esc(v)}">${esc(v)}</option>`).join('');
}

function defaultValueFor(field) {
  if (field.type === 'toggle') return (field.ph === 'true' ? 'true' : 'false');
  return (field.ph || '');
}

function valueControlHTML(field) {
  const key = esc(field.k);
  const ph = esc(field.ph || '');
  const inputType = field.secret ? 'password' : (field.type === 'number' ? 'number' : 'text');

  if (field.type === 'toggle') {
    const initial = defaultValueFor(field);
    return `<div class="toggle-shell" data-toggle-row="1" data-field="${key}">
      <input type="hidden" data-key="${key}" value="${initial}">
      <button type="button" class="tog ${initial === 'true' ? 'on' : ''}" data-toggle="${key}">${initial === 'true' ? 'On' : 'Off'}</button>
    </div>`;
  }
  if (field.type === 'model' || field.options) {
    return `<select data-key="${key}" class="card-input">${renderOptionsHTML(field)}</select>`;
  }
  return `<input type="${inputType}" data-key="${key}" placeholder="${ph || field.lbl}" />`;
}

function tagBadgeHTML(f) {
  const t = f.tag || 'optional';
  return `<span class="badge badge-${t}">${t}</span>`;
}

function cardHTML(f) {
  return `<div class="env-card" data-row data-group="${esc(f.g)}" data-search="${esc((f.k + ' ' + (f.lbl || '')).toLowerCase())}">
    <div class="card-top">
      <input type="checkbox" class="card-check" data-check="${esc(f.k)}" ${f.tag === 'critical' ? 'checked' : ''}>
      <div class="card-info">
        <div class="card-key">${esc(f.k)}</div>
        <div class="card-lbl">${esc(f.lbl || '')}</div>
      </div>
      ${tagBadgeHTML(f)}
    </div>
    <div class="card-input-wrap">${valueControlHTML(f)}</div>
  </div>`;
}

function collect() {
  const obj = {};
  document.querySelectorAll('[data-key]').forEach(el => {
    const key = el.dataset.key;
    const chk = document.querySelector(`[data-check="${CSS.escape(key)}"]`);
    if (chk && chk.checked) obj[key] = el.value;
  });
  return obj;
}

function filter() {
  const q = ($('search')?.value || '').trim().toLowerCase();
  document.querySelectorAll('.sec').forEach(sec => {
    const grp = sec.dataset.section;
    const gMatch = activeGroup === 'All' || activeGroup === grp;
    if (!gMatch) { sec.style.display = 'none'; return; }
    let any = false;
    sec.querySelectorAll('[data-row]').forEach(card => {
      const m = !q || card.dataset.search.includes(q);
      card.style.display = m ? '' : 'none';
      if (m) any = true;
    });
    sec.style.display = any ? '' : 'none';
  });
}

function renderSections() {
  const grouped = {};
  FIELDS.forEach(f => { (grouped[f.g] ||= []).push(f); });
  const wrap = $('sections');
  if (!wrap) return;
  wrap.innerHTML = '';
  Object.entries(grouped).forEach(([grp, items]) => {
    const sec = document.createElement('div');
    sec.className = 'sec';
    sec.dataset.section = grp;
    sec.innerHTML = `<div class="sec-header">
      <span class="sec-icon">${ICONS[grp] || '📁'}</span>
      <span class="sec-title">${esc(grp)}</span>
      <div class="sec-line"></div>
    </div>
    <div class="cards">${items.map(cardHTML).join('')}</div>`;
    wrap.appendChild(sec);
  });

  document.querySelectorAll('[data-toggle]').forEach(btn => btn.onclick = () => {
    const key = btn.dataset.toggle;
    const inp = document.querySelector(`input[data-key="${CSS.escape(key)}"]`);
    const on = inp.value !== 'true';
    inp.value = on ? 'true' : 'false';
    btn.textContent = on ? 'On' : 'Off';
    btn.classList.toggle('on', on);
  });
}

function generateBundle() {
  const obj = collect();
  const bundle = encodeBundle(obj);
  $('bundleOut').value = bundle;
  $('envLineOut').value = `${BUNDLE_KEY}=${bundle}`;
  showToast('Bundle generated ✓');
}

renderSidebar();
renderSections();
filter();

if ($('generateBundle')) $('generateBundle').onclick = generateBundle;
if ($('copyBundle')) $('copyBundle').onclick = () => { navigator.clipboard.writeText($('bundleOut').value); showToast('Copied ✓'); };
if ($('search')) $('search').oninput = filter;
