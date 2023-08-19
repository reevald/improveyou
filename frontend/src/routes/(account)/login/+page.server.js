export const ssr = true;
import { cookieNameJWT } from '$lib/stores.js';
// const urlLogin = 'http://127.0.0.1:8000/user/login';
// const urlLogin = 'https://api.improveyou.fun/user/login';
// const urlRefresh = 'https://api.improveyou.fun/user/refresh';
const testLogin = async (url = '', credType = 'same-origin', data = {}) => {
  const response = await fetch(url, {
    method: 'POST', // *GET, POST, PUT, DELETE, etc.
    mode: 'cors', // no-cors, *cors, same-origin
    cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    credentials: credType, // include, *same-origin, omit
    headers: {
      'Content-Type': 'application/json'
    },
    redirect: 'follow', // manual, *follow, error
    referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
    body: JSON.stringify(data) // body data type must match "Content-Type" header
  });
  return response; // parses JSON response into native JavaScript objects
};

// /** @type {import('./$types').Actions} */
export const actions = {
  login: async ({ cookies, request }) => {
    const data = await request.formData();
    const email = data.get('email');
    const password = data.get('password');
    const endpoint = data.get('endpoint');
    const credType = data.get('credType');
    const cookieName = data.get('cookieName');
    const response = await testLogin(endpoint, credType, {
      email,
      password
    });
    cookies.set('test cookie1', 'value cookie1');
    const cookieku = response.headers.get('set-cookie');
    if (cookieku) {
      const values = cookieku.split(';').reduce((res, item) => {
        const data = item.trim().split('=');
        return { ...res, [data[0]]: data[1] };
      }, {});
      cookieNameJWT.update(() => cookieName);
      cookies.set(cookieName, values[cookieName], {
        expires: new Date(values['expires']),
        maxAge: values['Max-Age'],
        path: '/',
        httpOnly: true,
        sameSite: 'lax', // true = Strict
        secure: true,
        domain: 'improveyou.fun'
      });
      // return { success: true };
    }
    return await response.json();
  }
};
