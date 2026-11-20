/* Only entry URLs choose a locale. Localized policy pages never redirect. */
(() => {
  const page = document.body.dataset.entry;
  if (!['index', 'privacy', 'terms', 'support'].includes(page)) return;
  const supported = ['zh-Hans', 'en', 'zh-Hant', 'ja', 'ko', 'th', 'tr', 'vi', 'ru'];
  function match(value) {
    if (!value) return null;
    const tag = String(value).replaceAll('_', '-').toLowerCase();
    const exact = supported.find(x => x.toLowerCase() === tag);
    if (exact) return exact;
    if (tag.startsWith('zh-')) {
      if (tag.includes('hant') || /(^|-)(tw|hk|mo)(-|$)/.test(tag)) return 'zh-Hant';
      return 'zh-Hans';
    }
    if (tag === 'zh') return 'zh-Hans';
    return supported.find(x => x === tag.split('-')[0]) || null;
  }
  const requested = new URLSearchParams(location.search).get('lang');
  const code = match(requested) || (navigator.languages || [navigator.language]).map(match).find(Boolean) || 'en';
  const target = new URL(`${code}/${page}.html`, location.href);
  target.hash = location.hash;
  location.replace(target.href);
})();
