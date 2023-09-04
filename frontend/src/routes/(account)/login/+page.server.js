export const ssr = true;
// console.log('[page server login] Its run server?');
import { iyPOST } from '$lib/api';
import { baseAPI, cookieDev } from '$lib/const';
import { cookieNameJWT } from '$lib/stores.js';

// /** @type {import('./$types').Actions} */
export const actions = {
  process: async ({ cookies, request }) => {
    // Dev mode
    const cookieName = cookieDev; // Prod mode: cookieProd

    const data = await request.formData();
    const email = data.get('email');
    const password = data.get('password');
    const response = await iyPOST(baseAPI + 'user/login', 'include', {
      email,
      password
    });
    const iyCookie = response.headers.get('set-cookie');
    if (iyCookie) {
      const values = iyCookie.split(';').reduce((res, item) => {
        const data = item.trim().split('=');
        return { ...res, [data[0]]: data[1] };
      }, {});
      cookieNameJWT.update(() => cookieName);

      // Prod Mode
      cookies.set(cookieName, values[cookieName], {
        expires: new Date(values['expires']),
        maxAge: values['Max-Age'],
        path: '/',
        httpOnly: true,
        sameSite: 'lax', // true = Strict
        secure: true,
        domain: 'improveyou.fun'
      });

      // Dev Mode
      // cookies.set(cookieName, values[cookieName], {
      //   expires: new Date(values['expires']),
      //   maxAge: values['Max-Age'],
      //   path: '/',
      //   httpOnly: true,
      //   sameSite: 'lax', // true = Strict
      //   secure: false,
      //   domain: 'localimproveyou.fun' // with custom hosts
      // });
    }
    return {
      status: response.status,
      data: await response.json()
    };
  }
};
