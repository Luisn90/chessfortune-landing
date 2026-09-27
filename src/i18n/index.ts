export const locales = ['es', 'en'] as const;
export type Lang = (typeof locales)[number];
export const defaultLang: Lang = 'es';
export const langNames: Record<Lang, string> = { es: 'Español', en: 'English' };

/** Idioma a partir de Astro.currentLocale (español si no hay otro). */
export const getLang = (locale?: string): Lang => (locale === 'en' ? 'en' : 'es');

/** Quita el prefijo de idioma y la barra final: '/en/seeds/' → '/seeds'. */
export const stripLang = (pathname: string): string => {
  const p = pathname.replace(/^\/en(?=\/|$)/, '').replace(/\/+$/, '');
  return p || '/';
};

/** Ruta en el idioma indicado, siempre con barra final: ('/seeds', 'en') → '/en/seeds/'. */
export const localize = (path: string, lang: Lang): string => {
  const clean = stripLang(path);
  const prefix = lang === defaultLang ? '' : '/en';
  return clean === '/' ? `${prefix}/` : `${prefix}${clean}/`;
};

/** Convierte 'línea uno|línea *acento*.' en HTML con <br /> y texto dorado. */
export const rich = (s: string): string =>
  s
    .replace(/&/g, '&amp;').replace(/</g, '&lt;')
    .replace(/\*(.+?)\*/g, '<span class="text-gilded">$1</span>')
    .replace(/\|/g, '<br /> ');
