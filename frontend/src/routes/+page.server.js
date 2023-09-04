import { redirect } from '@sveltejs/kit';

export function load({ url }) {
  console.log('URL root', url);
  if (url.pathname == '/') {
    throw redirect(308, '/login');
  }
}
// console.log('[page server signup] Its run server?');
