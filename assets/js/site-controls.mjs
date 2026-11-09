export const nextLanguage = language => language === 'en' ? 'zh' : 'en';
export const nextTheme = theme => theme === 'dark' ? 'light' : 'dark';

export async function copyCitation(text, clipboard = globalThis.navigator?.clipboard, doc = globalThis.document) {
  if (clipboard?.writeText) {
    try {
      await clipboard.writeText(text);
      return;
    } catch { /* The selection command may still be permitted. */ }
  }
  const area = doc.createElement('textarea');
  area.value = text;
  area.setAttribute('readonly', '');
  area.style.position = 'fixed';
  area.style.opacity = '0';
  doc.body.appendChild(area);
  area.select();
  try {
    if (!doc.execCommand('copy')) throw new Error('Copy command failed');
  } finally {
    area.remove();
  }
}

function updateControlLabels(doc) {
  const root = doc.documentElement;
  const language = root.dataset.lang || 'zh';
  root.lang = language === 'en' ? 'en' : 'zh-CN';
  const languageButton = doc.querySelector('[data-language-toggle]');
  languageButton?.replaceChildren(language === 'zh' ? 'EN' : '中');
  languageButton?.setAttribute('aria-label', language === 'zh' ? 'Switch to English' : '切换到中文');
  const themeButton = doc.querySelector('[data-theme-toggle]');
  if (themeButton) {
    themeButton.innerHTML = root.dataset.theme === 'dark'
      ? '<i class="fa-solid fa-sun" aria-hidden="true"></i>'
      : '<i class="fa-regular fa-moon" aria-hidden="true"></i>';
  }
  themeButton?.setAttribute('aria-label', root.dataset.theme === 'dark' ? 'Switch to light theme' : '切换到深色模式');
}

export function initializeSiteControls(doc = document, storage) {
  const root = doc.documentElement;
  if (storage === undefined) {
    try { storage = globalThis.localStorage; } catch { storage = null; }
  }
  const getSaved = key => { try { return storage?.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { storage?.setItem(key, value); } catch { /* Browsing storage may be disabled. */ } };
  root.dataset.lang = getSaved('site-language') === 'en' ? 'en' : 'zh';
  root.dataset.theme = getSaved('site-theme') === 'dark' ? 'dark' : 'light';
  updateControlLabels(doc);

  doc.querySelector('[data-language-toggle]')?.addEventListener('click', () => {
    root.dataset.lang = nextLanguage(root.dataset.lang);
    save('site-language', root.dataset.lang);
    updateControlLabels(doc);
  });
  doc.querySelector('[data-theme-toggle]')?.addEventListener('click', () => {
    root.dataset.theme = nextTheme(root.dataset.theme);
    save('site-theme', root.dataset.theme);
    updateControlLabels(doc);
  });
  doc.querySelectorAll('.citation-copy').forEach(button => {
    const original = button.innerHTML;
    const status = button.nextElementSibling;
    let timer;
    button.addEventListener('click', async () => {
      const language = root.dataset.lang;
      if (status?.classList.contains('citation-status')) status.textContent = '';
      let message;
      try {
        await copyCitation(button.dataset.citation || '');
        message = language === 'zh' ? '已复制' : 'Copied';
      } catch {
        message = language === 'zh' ? '复制失败' : 'Copy failed';
      }
      button.textContent = message;
      if (status?.classList.contains('citation-status')) status.textContent = message;
      clearTimeout(timer);
      timer = setTimeout(() => { button.innerHTML = original; }, 1600);
    });
  });
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initializeSiteControls(), { once: true });
  } else {
    initializeSiteControls();
  }
}
