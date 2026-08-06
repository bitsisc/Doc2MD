# Script to update web/app.js with robust Drag & Drop, FileReader fallback, and immediate loading indicators

APP_JS_V2 = '''// 24 Official EU Languages Configuration
const LANGUAGES = [
  { code: "el", name: "Ελληνικά", country: "gr" },
  { code: "en", name: "English", country: "gb" },
  { code: "sl", name: "Slovenščina", country: "si" },
  { code: "fr", name: "Français", country: "fr" },
  { code: "de", name: "Deutsch", country: "de" },
  { code: "es", name: "Español", country: "es" },
  { code: "it", name: "Italiano", country: "it" },
  { code: "pt", name: "Português", country: "pt" },
  { code: "nl", name: "Nederlands", country: "nl" },
  { code: "pl", name: "Polski", country: "pl" },
  { code: "ro", name: "Română", country: "ro" },
  { code: "sv", name: "Svenska", country: "se" },
  { code: "da", name: "Dansk", country: "dk" },
  { code: "fi", name: "Suomi", country: "fi" },
  { code: "cs", name: "Čeština", country: "cz" },
  { code: "hu", name: "Magyar", country: "hu" },
  { code: "sk", name: "Slovenčina", country: "sk" },
  { code: "bg", name: "Български", country: "bg" },
  { code: "hr", name: "Hrvatski", country: "hr" },
  { code: "lt", name: "Lietuvių", country: "lt" },
  { code: "lv", name: "Latviešu", country: "lv" },
  { code: "et", name: "Eesti", country: "ee" },
  { code: "mt", name: "Malti", country: "mt" },
  { code: "ga", name: "Gaeilge", country: "ie" }
];

// SVG flags (viewBox normalized for 44x30 uniform tile display)
const SVG_FLAGS = {
  gr: `<svg viewBox="0 0 27 18"><rect width="27" height="18" fill="#005BAE"/><path d="M0 2h27M0 6h27M0 10h27M0 14h27" stroke="#FFF" stroke-width="2"/><rect width="10" height="10" fill="#005BAE"/><path d="M5 0v10M0 5h10" stroke="#FFF" stroke-width="2"/></svg>`,
  gb: `<svg viewBox="0 0 60 30"><clipPath id="s"><path d="M0 0v30h60V0z"/></clipPath><clipPath id="t"><path d="M30 15h30v15H30zM0 0h30v15H0zM30 0h30v15H30zM0 15h30v15H0z"/></clipPath><g clip-path="url(#s)"><path d="M0 0v30h60V0z" fill="#012169"/><path d="M0 0l60 30M60 0L0 30" stroke="#fff" stroke-width="6"/><path d="M0 0l60 30M60 0L0 30" stroke="#C8102E" stroke-width="4" clip-path="url(#t)"/><path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/><path d="M30 0v30M0 15h60" stroke="#C8102E" stroke-width="6"/></g></svg>`,
  si: `<svg viewBox="0 0 6 4"><rect width="6" height="1.33" fill="#fff"/><rect y="1.33" width="6" height="1.33" fill="#0000ed"/><rect y="2.66" width="6" height="1.34" fill="#ff0000"/><g transform="translate(1.2, 0.4) scale(0.75)"><path d="M 1.2,0.6 L 2.0,0.6 C 2.2,1.3 1.8,1.7 1.6,1.7 C 1.4,1.7 1.0,1.3 1.2,0.6 Z" fill="#0000ed" stroke="#ff0000" stroke-width="0.06"/><path d="M 1.35,1.2 L 1.6,0.85 L 1.85,1.2 Z" fill="#fff"/><polygon points="1.6,0.65 1.5,0.78 1.7,0.78" fill="#ffcc00"/><polygon points="1.35,0.75 1.25,0.88 1.45,0.88" fill="#ffcc00"/><polygon points="1.85,0.75 1.75,0.88 1.95,0.88" fill="#ffcc00"/></g></svg>`,
  fr: `<svg viewBox="0 0 3 2"><rect width="1" height="2" fill="#002395"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#ED2939"/></svg>`,
  de: `<svg viewBox="0 0 5 3"><rect width="5" height="1" fill="#000"/><rect y="1" width="5" height="1" fill="#DD0000"/><rect y="2" width="5" height="1" fill="#FFCE00"/></svg>`,
  es: `<svg viewBox="0 0 750 500"><rect width="750" height="500" fill="#c60b1e"/><rect y="125" width="750" height="250" fill="#ffc400"/><g transform="translate(180, 200) scale(1.5)"><rect x="0" y="0" width="30" height="40" fill="#ad1519" rx="3"/><rect x="30" y="0" width="30" height="40" fill="#fabd00" rx="3"/><circle cx="30" cy="20" r="10" fill="#005293"/></g></svg>`,
  it: `<svg viewBox="0 0 3 2"><rect width="1" height="2" fill="#009246"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#ce2b37"/></svg>`,
  pt: `<svg viewBox="0 0 600 400"><rect width="240" height="400" fill="#046A38"/><rect x="240" width="360" height="400" fill="#DA291C"/><circle cx="240" cy="200" r="80" fill="#FFC72C"/><rect x="210" y="160" width="60" height="80" fill="#FFF" rx="10"/><rect x="220" y="170" width="40" height="60" fill="#046A38" rx="5"/></svg>`,
  nl: `<svg viewBox="0 0 3 2"><rect width="3" height="0.67" fill="#AE1C28"/><rect y="0.67" width="3" height="0.67" fill="#fff"/><rect y="1.33" width="3" height="0.67" fill="#21468B"/></svg>`,
  pl: `<svg viewBox="0 0 16 10"><rect width="16" height="5" fill="#fff"/><rect y="5" width="16" height="5" fill="#dc143c"/></svg>`,
  ro: `<svg viewBox="0 0 3 2"><rect width="1" height="2" fill="#002B7F"/><rect x="1" width="1" height="2" fill="#FCD116"/><rect x="2" width="1" height="2" fill="#CE1126"/></svg>`,
  se: `<svg viewBox="0 0 16 10"><rect width="16" height="10" fill="#006aa7"/><rect x="5" width="2" height="10" fill="#fecc00"/><rect y="4" width="16" height="2" fill="#fecc00"/></svg>`,
  dk: `<svg viewBox="0 0 37 28"><rect width="37" height="28" fill="#C8102E"/><rect x="12" width="4" height="28" fill="#fff"/><rect y="12" width="37" height="4" fill="#fff"/></svg>`,
  fi: `<svg viewBox="0 0 18 11"><rect width="18" height="11" fill="#fff"/><rect x="5" width="3" height="11" fill="#003580"/><rect y="4" width="18" height="3" fill="#003580"/></svg>`,
  cz: `<svg viewBox="0 0 3 2"><rect width="3" height="1" fill="#fff"/><rect y="1" width="3" height="1" fill="#d7141a"/><polygon points="0,0 1.5,1 0,2" fill="#11457e"/></svg>`,
  hu: `<svg viewBox="0 0 3 2"><rect width="3" height="0.67" fill="#CD2A3E"/><rect y="0.67" width="3" height="0.67" fill="#fff"/><rect y="1.33" width="3" height="0.67" fill="#436F4D"/></svg>`,
  sk: `<svg viewBox="0 0 6 4"><rect width="6" height="1.33" fill="#fff"/><rect y="1.33" width="6" height="1.33" fill="#0B4EA2"/><rect y="2.66" width="6" height="1.34" fill="#EE1C25"/><g transform="translate(1.2, 0.4) scale(0.75)"><path d="M 0,0 L 2,0 C 2.3,2.5 1.5,3.5 1,3.5 C 0.5,3.5 -0.3,2.5 0,0 Z" fill="#EE1C25" stroke="#fff" stroke-width="0.2"/><path d="M 1,1 L 1,2.8 M 0.4,1.6 L 1.6,1.6 M 0.5,2.2 L 1.5,2.2" stroke="#fff" stroke-width="0.35" stroke-linecap="round"/></g></svg>`,
  bg: `<svg viewBox="0 0 5 3"><rect width="5" height="1" fill="#fff"/><rect y="1" width="5" height="1" fill="#00966E"/><rect y="2" width="5" height="1" fill="#D62612"/></svg>`,
  hr: `<svg viewBox="0 0 6 4"><rect width="6" height="1.33" fill="#FF0000"/><rect y="1.33" width="6" height="1.33" fill="#fff"/><rect y="2.66" width="6" height="1.34" fill="#171796"/><g transform="translate(2.2, 0.7) scale(0.4)"><rect width="4" height="5" fill="#FFF" stroke="#FF0000" stroke-width="0.3"/><rect x="0" y="0" width="0.8" height="1" fill="#FF0000"/><rect x="1.6" y="0" width="0.8" height="1" fill="#FF0000"/><rect x="3.2" y="0" width="0.8" height="1" fill="#FF0000"/><rect x="0.8" y="1" width="0.8" height="1" fill="#FF0000"/><rect x="2.4" y="1" width="0.8" height="1" fill="#FF0000"/><rect x="0" y="2" width="0.8" height="1" fill="#FF0000"/><rect x="1.6" y="2" width="0.8" height="1" fill="#FF0000"/><rect x="3.2" y="2" width="0.8" height="1" fill="#FF0000"/><rect x="0.8" y="3" width="0.8" height="1" fill="#FF0000"/><rect x="2.4" y="3" width="0.8" height="1" fill="#FF0000"/></g></svg>`,
  lt: `<svg viewBox="0 0 5 3"><rect width="5" height="1" fill="#FDB913"/><rect y="1" width="5" height="1" fill="#006A44"/><rect y="2" width="5" height="1" fill="#C1272D"/></svg>`,
  lv: `<svg viewBox="0 0 5 3"><rect width="5" height="1.2" fill="#9E3039"/><rect y="1.2" width="5" height="0.6" fill="#fff"/><rect y="1.8" width="5" height="1.2" fill="#9E3039"/></svg>`,
  ee: `<svg viewBox="0 0 3 2"><rect width="3" height="0.67" fill="#4891D9"/><rect y="0.67" width="3" height="0.67" fill="#000"/><rect y="1.33" width="3" height="0.67" fill="#fff"/></svg>`,
  mt: `<svg viewBox="0 0 6 4"><rect width="3" height="4" fill="#fff"/><rect x="3" width="3" height="4" fill="#CF142B"/><g transform="translate(0.3, 0.3) scale(0.6)"><path d="M 1,0 L 1.3,0.7 L 2,1 L 1.3,1.3 L 1,2 L 0.7,1.3 L 0,1 L 0.7,0.7 Z" fill="#888" stroke="#CF142B" stroke-width="0.15"/></g></svg>`,
  ie: `<svg viewBox="0 0 3 2"><rect width="1" height="2" fill="#169B62"/><rect x="1" width="1" height="2" fill="#fff"/><rect x="2" width="1" height="2" fill="#FF883E"/></svg>`
};

let currentLang = 'el';
let currentMarkdown = '';

document.addEventListener('DOMContentLoaded', () => {
  initUI();
  initLanguageGrid();
  updateLanguage(currentLang);
});

function initUI() {
  document.getElementById('kidmedia-link').addEventListener('click', (e) => {
    e.preventDefault();
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.open_url('https://kidmedia.eu');
    }
  });

  document.getElementById('lang-btn').addEventListener('click', () => {
    document.getElementById('lang-modal').classList.remove('hidden');
  });

  document.getElementById('close-lang-btn').addEventListener('click', () => {
    document.getElementById('lang-modal').classList.add('hidden');
  });

  // Select File Button
  document.getElementById('select-file-btn').addEventListener('click', (e) => {
    e.stopPropagation();
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.select_file().then(res => {
        if (res && res.status === 'success') {
          showLoading(true);
          setTimeout(() => handleFileResult(res), 50);
        } else if (res && res.status === 'error') {
          alert(res.message);
        }
      });
    } else {
      document.getElementById('hidden-file-input').click();
    }
  });

  // Hidden File Input Change Event
  document.getElementById('hidden-file-input').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      processHtmlFileObject(file);
    }
  });

  // Drag & Drop
  const dropZone = document.getElementById('drop-zone');

  ['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.add('dragover');
    }, false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropZone.classList.remove('dragover');
    }, false);
  });

  dropZone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      const file = files[0];
      showLoading(true);

      // If PyWebView native path is available
      if (file.path && window.pywebview && window.pywebview.api) {
        window.pywebview.api.convert_file_by_path(file.path).then(handleFileResult);
      } else {
        processHtmlFileObject(file);
      }
    }
  });

  // Preview modal controls
  document.getElementById('close-preview-x').addEventListener('click', closePreview);
  document.getElementById('close-preview-btn').addEventListener('click', closePreview);

  document.getElementById('save-md-btn').addEventListener('click', () => {
    if (window.pywebview && window.pywebview.api && currentMarkdown) {
      window.pywebview.api.save_file(currentMarkdown);
    }
  });
}

function processHtmlFileObject(file) {
  showLoading(true);
  const reader = new FileReader();
  reader.onload = function(e) {
    const base64Data = e.target.result;
    if (window.pywebview && window.pywebview.api) {
      window.pywebview.api.convert_file_by_data(file.name, base64Data).then(handleFileResult);
    } else {
      showLoading(false);
      alert("Python backend not connected.");
    }
  };
  reader.onerror = function() {
    showLoading(false);
    alert("Error reading file.");
  };
  reader.readAsDataURL(file);
}

function initLanguageGrid() {
  const grid = document.getElementById('lang-grid');
  grid.innerHTML = '';

  LANGUAGES.forEach(lang => {
    const tile = document.createElement('div');
    tile.className = `lang-tile ${lang.code === currentLang ? 'active' : ''}`;
    tile.dataset.code = lang.code;
    tile.innerHTML = SVG_FLAGS[lang.country] || '';
    
    tile.addEventListener('click', () => {
      updateLanguage(lang.code);
      document.getElementById('lang-modal').classList.add('hidden');
    });

    grid.appendChild(tile);
  });
}

function updateLanguage(code) {
  currentLang = code;

  document.querySelectorAll('.lang-tile').forEach(t => {
    t.classList.toggle('active', t.dataset.code === code);
  });

  const langObj = LANGUAGES.find(l => l.code === code) || LANGUAGES[0];
  document.getElementById('current-flag').innerHTML = SVG_FLAGS[langObj.country] || '';
  document.getElementById('current-lang-name').textContent = langObj.name;

  if (window.pywebview && window.pywebview.api) {
    window.pywebview.api.get_translation(code).then(applyTranslations);
  }
}

function applyTranslations(dict) {
  if (!dict) return;
  for (const [key, val] of Object.entries(dict)) {
    const el = document.getElementById(`txt-${key}`);
    if (el) {
      el.textContent = val;
    }
  }
}

function handleFileResult(res) {
  showLoading(false);
  if (!res) return;

  if (res.status === 'success') {
    currentMarkdown = res.content;
    document.getElementById('markdown-output').value = currentMarkdown;
    document.getElementById('preview-modal').classList.remove('hidden');
  } else if (res.status === 'error') {
    alert(res.message || 'Error converting file');
  }
}

function closePreview() {
  document.getElementById('preview-modal').classList.add('hidden');
}

function showLoading(show) {
  const el = document.getElementById('loading-modal');
  if (show) {
    el.classList.remove('hidden');
  } else {
    el.classList.add('hidden');
  }
}
'''

with open('web/app.js', 'w', encoding='utf-8') as f:
    f.write(APP_JS_V2.strip())

print("Updated web/app.js with robust Drag&Drop, FileReader fallback, and loading feedback!")
