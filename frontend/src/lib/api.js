import { goto } from '$app/navigation';
import { baseAPI } from '$lib/const';

export const iyPOST = async (url = '', credType = 'same-origin', data = {}) => {
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

export const tryAccessWithAuth = async (type = 'GOIN') => {
  let isFailByAccessJwt = true;
  let isFailByRefreshJwt = true;
  let isTooManyRequest = false;
  let isAccess = false;

  if (typeof localStorage !== 'undefined' && localStorage.getItem('jwt') !== null) {
    const jwt = localStorage.getItem('jwt');

    // Try to validate access jwt
    await fetch(baseAPI + 'user/validate', {
      method: 'GET',
      headers: new Headers({
        Authorization: `Bearer ${jwt}`
      })
    })
      .then((resp) => {
        if (resp.ok) {
          isFailByAccessJwt = false;
          isAccess = true;
          if (type == 'GOIN') {
            goto('home');
          }
        } else if (resp.status == 429) {
          isTooManyRequest = true;
        }
      })
      .catch((e) => {
        console.error(e);
      });
  }

  // Try to resolve login by cookie even localstorage jwt empty, invalid, or expired
  if (isFailByAccessJwt && !isTooManyRequest) {
    await fetch(baseAPI + 'user/refresh', {
      method: 'GET',
      credentials: 'include'
    })
      .then((resp) => {
        if (resp.ok) {
          resp.json().then((data) => {
            if (typeof localStorage !== 'undefined' && data?.jwt) {
              localStorage.setItem('jwt', data?.jwt);
            }
            isAccess = true;
            isFailByRefreshJwt = false;
            if (type == 'GOIN') {
              goto('home');
            }
          });
        } else if (resp.status == 429) {
          isTooManyRequest = true;
        }
      })
      .catch((e) => {
        console.error(e);
      });
  }

  if (type == 'GOOUT' && isTooManyRequest) {
    isAccess = false;
    goto(`429-too-many-requests`);
  } else if (type == 'GOOUT' && isFailByAccessJwt && isFailByRefreshJwt) {
    isAccess = false;
    goto('login');
  }
  return isAccess;
};

const apiWithAuth = async (resolver, successCB, autoRedirect = true) => {
  let isTooManyRequest = false;
  let isFailByAccessJwt = true;
  let isFailByRefreshJwt = true;
  let respStatus = 200;
  if (typeof localStorage !== 'undefined' && localStorage.getItem('jwt') !== null) {
    const resp = await resolver();
    respStatus = resp.status;
    if (resp.ok) {
      const respData = await resp.json();
      isFailByAccessJwt = false;
      successCB(respData);
    } else if (resp.status == 429) {
      isTooManyRequest = true;
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
          respStatus = respGet.status;
          if (respGet.ok) {
            const respData = await respGet.json();
            isFailByAccessJwt = false;
            isFailByRefreshJwt = false;
            successCB(respData);
          } else if (respGet.status == 429) {
            isTooManyRequest = true;
          }
        }
      });
    } else if (resp.status == 429) {
      isTooManyRequest = true;
    }
  }
  if (autoRedirect) {
    if (isTooManyRequest) {
      goto('429-too-many-requests');
    } else if (isFailByAccessJwt && isFailByRefreshJwt) {
      goto('login');
      return;
    }
  } else {
    return respStatus;
  }
};

export const getWithAuth = async (endpoint, successCB) => {
  const resolveGET = async () => {
    const jwt = localStorage.getItem('jwt');
    const resp = await fetch(baseAPI + endpoint, {
      method: 'GET',
      headers: new Headers({
        Authorization: `Bearer ${jwt}`
      })
    });
    return resp;
  };
  return await apiWithAuth(resolveGET, successCB);
};

export const postWithAuth = async (
  endpoint,
  objData,
  autoRedirect = true,
  successCB
) => {
  const resolvePOST = async () => {
    const jwt = localStorage.getItem('jwt');

    const resp = await fetch(baseAPI + endpoint, {
      method: 'POST',
      mode: 'cors',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${jwt}`
      }),
      body: JSON.stringify(objData)
    });
    return resp;
  };
  return await apiWithAuth(resolvePOST, successCB, autoRedirect);
};

export const putWithAuth = async (
  endpoint,
  objData,
  autoRedirect = true,
  successCB
) => {
  const resolvePUT = async () => {
    const jwt = localStorage.getItem('jwt');

    const resp = await fetch(baseAPI + endpoint, {
      method: 'PUT',
      mode: 'cors',
      headers: new Headers({
        'Content-Type': 'application/json',
        Authorization: `Bearer ${jwt}`
      }),
      body: JSON.stringify(objData)
    });
    return resp;
  };
  return await apiWithAuth(resolvePUT, successCB, autoRedirect);
};
