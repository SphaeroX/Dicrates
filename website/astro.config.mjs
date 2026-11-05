// @ts-check
import { defineConfig } from 'astro/config';

// Deployed to GitHub Pages: https://sphaerox.github.io/Dicrates/
// Change `site`/`base` together when a custom domain is added.
export default defineConfig({
  site: 'https://sphaerox.github.io',
  base: '/Dicrates',
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
});
