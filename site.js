(() => {
  'use strict';
  const downloadPickers = [...document.querySelectorAll('.download-picker')];
  const setDownloadOpen = (picker, open) => {
    picker.querySelector('[data-download-toggle]').setAttribute('aria-expanded', String(open));
    picker.querySelector('.download-options').hidden = !open;
  };
  downloadPickers.forEach(picker => {
    const toggle = picker.querySelector('[data-download-toggle]');
    picker.addEventListener('pointerenter', event => {
      if (event.pointerType === 'mouse') setDownloadOpen(picker, true);
    });
    picker.addEventListener('pointerleave', event => {
      if (event.pointerType === 'mouse' && !picker.contains(document.activeElement)) setDownloadOpen(picker, false);
    });
    if (toggle.tagName === 'BUTTON') {
      toggle.addEventListener('click', () => setDownloadOpen(picker, toggle.getAttribute('aria-expanded') !== 'true'));
    }
    picker.addEventListener('focusin', event => {
      if (event.target.matches(':focus-visible')) setDownloadOpen(picker, true);
    });
    picker.addEventListener('focusout', event => {
      if (!picker.contains(event.relatedTarget)) setDownloadOpen(picker, false);
    });
    picker.addEventListener('keydown', event => {
      if (event.key === 'Escape') {
        toggle.focus();
        setDownloadOpen(picker, false);
        event.preventDefault();
      }
    });
  });
  document.addEventListener('click', event => {
    downloadPickers.forEach(picker => {
      if (!picker.contains(event.target)) setDownloadOpen(picker, false);
    });
  });
  const advantageDialog = document.querySelector('#advantage-dialog');
  if (advantageDialog) {
    const detailTitle = advantageDialog.querySelector('h2');
    const detailImage = advantageDialog.querySelector('.advantage-dialog-image');
    document.querySelectorAll('.advantage-trigger').forEach(trigger => {
      trigger.addEventListener('click', () => {
        const title = trigger.querySelector('.advantage-title');
        const picture = trigger.querySelector('img');
        detailTitle.textContent = title.textContent;
        detailTitle.dataset.zh = title.dataset.zh;
        detailTitle.dataset.en = title.dataset.en;
        detailImage.src = picture.getAttribute('src');
        detailImage.width = picture.width;
        detailImage.height = picture.height;
        const picturePath = picture.getAttribute('src');
        const detailKey = picturePath.includes('/no-bundles.') ? 'no-bundles'
          : picturePath.includes('/easy-to-use') ? 'easy-to-use' : 'pending';
        advantageDialog.querySelectorAll('[data-advantage-content]').forEach(content => {
          content.hidden = content.dataset.advantageContent !== detailKey;
        });
        advantageDialog.showModal();
      });
    });
    advantageDialog.querySelector('.advantage-close').addEventListener('click', () => advantageDialog.close());
    advantageDialog.addEventListener('click', event => {
      if (event.target !== advantageDialog) return;
      const bounds = advantageDialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) advantageDialog.close();
    });
  }
  let language = 'zh';
  const languageKey = 'jy-sysprep-language';
  const requestedLanguage = new URLSearchParams(window.location.search).get('lang');
  try {
    const savedLanguage = localStorage.getItem(languageKey);
    if (savedLanguage === 'en' || savedLanguage === 'zh') language = savedLanguage;
  } catch {}
  if (requestedLanguage === 'en' || requestedLanguage === 'zh') language = requestedLanguage;
  const translations = [...document.querySelectorAll('[data-zh][data-en]')];
  if (advantageDialog) {
    const title = advantageDialog.querySelector('h2');
    title.dataset.zh = '';
    title.dataset.en = '';
    translations.push(title);
  }
  const languageButton = document.querySelector('#language');
  const copyStatus = document.querySelector('#copy-status');
  const applyLanguage = () => {
    translations.forEach(element => { element.textContent = element.dataset[language]; });
    document.querySelectorAll('[data-investigation-link]').forEach(link => {
      link.setAttribute('href', language === 'zh' ? './investigation.html' : './investigation-en.html');
    });
    document.querySelectorAll('a[href]').forEach(link => {
      const href = link.getAttribute('href');
      if (!/^\.\/[^?#]+\.html(?:[?#]|$)/.test(href)) return;
      const target = new URL(href, window.location.href);
      target.searchParams.set('lang', language);
      link.setAttribute('href', href.split(/[?#]/)[0] + target.search + target.hash);
    });
    document.documentElement.lang = language === 'zh' ? 'zh-CN' : 'en';
    document.title = document.querySelector('title').dataset.page === 'download'
      ? (language === 'zh' ? 'JY Sysprep · 下载' : 'JY Sysprep · Downloads')
      : language === 'zh' ? 'JY Sysprep · 把 Windows 封装变简单' : 'JY Sysprep · Windows preparation, made clearer';
    languageButton.textContent = language === 'zh' ? 'EN' : '中文';
    languageButton.setAttribute('aria-label', language === 'zh' ? 'Switch to English' : '切换到中文');
    copyStatus.textContent = '';
    try { localStorage.setItem(languageKey, language); } catch {}
  };
  applyLanguage();
  languageButton.addEventListener('click', () => {
    language = language === 'zh' ? 'en' : 'zh';
    applyLanguage();
  });
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#nav-links');
  menu.addEventListener('click', () => {
    const expanded = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(expanded));
    nav.classList.toggle('open', expanded);
  });
  nav.querySelectorAll('a').forEach(link => link.addEventListener('click', () => {
    nav.classList.remove('open');
    menu.setAttribute('aria-expanded', 'false');
  }));
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const selectTab = selected => {
    tabs.forEach(tab => {
      const active = tab === selected;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
      tab.classList.toggle('active', active);
      document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
    });
  };
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectTab(tab));
    tab.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + 1) % tabs.length;
      selectTab(tabs[next]);
      tabs[next].focus();
    });
  });
  document.querySelector('#copy-checksum').addEventListener('click', async () => {
    const checksum = document.querySelector('#checksum');
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(checksum.textContent.trim());
      copyStatus.textContent = language === 'zh' ? '已复制 SHA256 校验值。' : 'SHA256 checksum copied.';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(checksum);
      selection.removeAllRanges();
      selection.addRange(range);
      copyStatus.textContent = language === 'zh' ? '已选中校验值，请按 Ctrl+C 复制。' : 'Checksum selected. Press Ctrl+C to copy.';
    }
  });
})();
