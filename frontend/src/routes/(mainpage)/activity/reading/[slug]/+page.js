import { baseAPI } from '$lib/const';
import { apiSSRWithAuth } from '$lib/ssr';

/** @type {import('../$types').PageLoad} */
export async function load({ fetch, params }) {
  const resolver = async () => {
    const jwt = localStorage.getItem('jwt');
    return await fetch(baseAPI + `activities/reading/${params.slug}`, {
      method: 'GET',
      headers: new Headers({
        Authorization: `Bearer ${jwt}`
      })
    });
  };

  return await apiSSRWithAuth(resolver);
}
