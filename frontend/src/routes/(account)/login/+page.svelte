<script>
  // https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
  const testLogin = async (url = '', data = {}) => {
    const response = await fetch(url, {
      method: 'POST', // *GET, POST, PUT, DELETE, etc.
      mode: 'cors', // no-cors, *cors, same-origin
      cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
      credentials: 'same-origin', // include, *same-origin, omit
      headers: {
        'Content-Type': 'application/json'
      },
      redirect: 'follow', // manual, *follow, error
      referrerPolicy: 'no-referrer', // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
      body: JSON.stringify(data) // body data type must match "Content-Type" header
    });
    return response.json(); // parses JSON response into native JavaScript objects
  };

  const testRefresh1 = async () => {
    await fetch('https://api.improveyou.fun/user/refresh', {
      credentials: 'same-origin'
    }).then(async (newjwt) => {
      console.log('Test 1: Refresh jwt', await newjwt.json());
    });
  };

  const testRefresh2 = async () => {
    await fetch('https://api.improveyou.fun/user/refresh', {
      credentials: 'include'
    }).then(async (newjwt) => {
      console.log('Test 2: Refresh jwt', await newjwt.json());
    });
  };

  testLogin('https://api.improveyou.fun/user/login', {
    email: 'bulelu@gmail.com',
    password: 'hilihwkwk'
  }).then(async (data) => {
    console.log('Test 1: Return LOGIN 🔐', data);
    await testRefresh1();
    console.log('----');
    await testRefresh2();
  });

  testLogin('https://improveyou-api-v1-1-qguw2amrfq-uc.a.run.app/user/login', {
    email: 'bulelu@gmail.com',
    password: 'hilihwkwk'
  }).then(async (data) => {
    console.log('Test 2: Return LOGIN 🔐', data);
    await testRefresh1();
    console.log('----');
    await testRefresh2();
  });
</script>

<h1>Login page attempt 1</h1>
<button on:click={testRefresh1}>Test refresh 1</button>
<button on:click={testRefresh2}>Test refresh 2</button>
