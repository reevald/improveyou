import { cookieNameJWT } from '$lib/stores.js';
export const ssr = true;
let cookieName;

cookieNameJWT.subscribe((value) => {
  cookieName = value;
});
export function load({ cookies }) {
  cookies.delete(cookieName);
  return {
    status: 'success'
  };
}
