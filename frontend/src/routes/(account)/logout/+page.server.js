import { cookieDev } from '$lib/const';
export const ssr = true;
// console.log('[page server logout] Its run server?');
// import { redirect } from '@sveltejs/kit';
export function load({ cookies }) {
  // Remove cookie by make expired
  // Dev mode
  // cookies.set(cookieDev, '', {
  //   expires: new Date('Thu, 01 Jan 1970 00:00:01 GMT'),
  //   path: '/',
  //   httpOnly: true,
  //   sameSite: 'lax', // true = Strict
  //   secure: false,
  //   domain: 'localimproveyou.fun' // with custom hosts
  // });

  // Prod mode
  cookies.set(cookieDev, '', {
    expires: new Date('Thu, 01 Jan 1970 00:00:01 GMT'),
    path: '/',
    httpOnly: true,
    sameSite: 'lax', // true = Strict
    secure: true,
    domain: 'improveyou.fun'
  });

  return {
    status: 'success'
  };
}
