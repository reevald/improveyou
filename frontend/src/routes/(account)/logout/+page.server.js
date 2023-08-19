import { cookieNameJWT } from '$lib/stores.js';

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
