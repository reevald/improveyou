import { baseAPI } from '$lib/const';
import { error, redirect } from '@sveltejs/kit';

export const apiSSRWithAuth = async (resolver) => {
  let isTooManyRequest = false;
  let isFailByAccessJwt = true;
  let isFailByRefreshJwt = true;
  let isNotFound = false;
  let iyData;

  if (typeof localStorage !== 'undefined' && localStorage.getItem('jwt') !== null) {
    const resp = await resolver();
    if (resp.ok) {
      iyData = await resp.json();
    } else if (resp.status == 429) {
      isTooManyRequest = true;
    } else if (resp.status == 400) {
      isNotFound = true;
    }
  }

  // Try resolve with cookie (fix access jwt first)
  if (isFailByAccessJwt && !isTooManyRequest) {
    const resp = await fetch(baseAPI + 'user/refresh', {
      method: 'GET',
      credentials: 'include'
    });
    if (resp.ok) {
      await resp.json().then(async (data) => {
        if (typeof localStorage !== 'undefined' && data?.jwt) {
          localStorage.setItem('jwt', data?.jwt);
          // Try resolve again with new jwt
          const respGet = await resolver();
          if (respGet.ok) {
            iyData = respGet.json();
            isFailByAccessJwt = false;
            isFailByRefreshJwt = false;
          } else if (respGet.status == 429) {
            isTooManyRequest = true;
          } else if (resp.status == 400) {
            isNotFound = true;
          }
        }
      });
    } else if (resp.status == 429) {
      isTooManyRequest = true;
    } else if (resp.status == 400) {
      isNotFound = true;
    }
  }
  if (isTooManyRequest) {
    throw redirect(308, '/429-too-many-requests');
  } else if (isNotFound) {
    throw error(404, 'Not found');
  } else if (isFailByAccessJwt && isFailByRefreshJwt) {
    throw redirect(308, '/login');
  }

  return { iyData };
};
