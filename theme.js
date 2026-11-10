(() => {
  'use strict';
  const key = 'jy-sysprep-theme';
  const root = document.documentElement;
  const system = window.matchMedia('(prefers-color-scheme: dark)');
  let preference = 'system';
  try { preference = localStorage.getItem(key) || 'system'; } catch {}
  if (!['system', 'light', 'dark'].includes(preference)) preference = 'system';
  let controls;
  const apply = () => {
    root.dataset.theme = preference === 'system' ? (system.matches ? 'dark' : 'light') : preference;
    if (!controls) return;
    const english = root.lang.startsWith('en');
    controls.setAttribute('aria-label', english ? 'Appearance' : '外观设置');
    const labels = english ? ['Follow system', 'Light mode', 'Dark mode'] : ['跟随系统', '浅色模式', '深色模式'];
    controls.querySelectorAll('button').forEach((button, index) => {
      button.title = labels[index];
      button.setAttribute('aria-label', labels[index]);
      button.setAttribute('aria-pressed', String(button.dataset.mode === preference));
    });
  };
  apply();
  if (system.addEventListener) system.addEventListener('change', apply);
  else system.addListener(apply);
  window.addEventListener('storage', event => {
    if (event.key !== key && event.key !== null) return;
    preference = ['light', 'dark'].includes(event.newValue) ? event.newValue : 'system';
    apply();
  });
  document.addEventListener('DOMContentLoaded', () => {
    controls = document.createElement('div');
    controls.className = 'theme-switcher';
    controls.setAttribute('role', 'group');
    const icons = [
      '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
      '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5"/>',
      '<path d="M20.8 13A9 9 0 0 1 11 3.2 9 9 0 1 0 20.8 13Z"/>'
    ];
    ['system', 'light', 'dark'].forEach((mode, index) => {
      const button = document.createElement('button');
      button.type = 'button';
      button.dataset.mode = mode;
      button.innerHTML = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + icons[index] + '</svg>';
      button.addEventListener('click', () => {
        preference = mode;
        try { localStorage.setItem(key, mode); } catch {}
        apply();
      });
      controls.append(button);
    });
    document.body.append(controls);
    new MutationObserver(apply).observe(root, { attributes: true, attributeFilter: ['lang'] });
    apply();
  });
})();
