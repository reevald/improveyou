<script>
  let endpoint = '';
  let credType = '';
  const testRefresh = async () => {
    console.log('Test rest refresh 1 [BEGIN]');
    await fetch(endpoint, {
      method: 'GET',
      credentials: credType
    }).then(async (newjwt) => {
      console.log('Refresh jwt', await newjwt.json());
    });
  };

  const testGetGameStat = async () => {
    console.log('Test get GameStat [BEGIN]');
    console.log('Bearer ' + localStorage.getItem('jwt'));
    await fetch(endpoint, {
      method: 'GET',
      headers: new Headers({
        Authorization: `Bearer ${localStorage.getItem('jwt')}`
      })
    }).then(async (newjwt) => {
      console.log('Refresh jwt', await newjwt.json());
    });
    console.log('Test get GameStat [END]');
  };

  const testPutPublicity = async () => {
    console.log('Test put publicity [BEGIN]');
    console.log('Bearer ' + localStorage.getItem('jwt'));
    await fetch(endpoint, {
      method: 'PUT',
      headers: new Headers({
        Authorization: `Bearer ${localStorage.getItem('jwt')}`,
        'Content-Type': 'application/json'
      }),
      body: JSON.stringify({
        is_public_mode: true
      })
    }).then(async (data) => {
      console.log('New publicity', await data.json());
    });
    console.log('Test put publicity [END]');
  };
</script>

<h1>Home page</h1>
<a href="/login">Login</a>
<a href="/logout">Logout</a>
<input type="text" bind:value={endpoint} placeholder="endpoint" />
<input type="text" bind:value={credType} placeholder="cred type" />
<button on:click={testRefresh}>##Test Refresh##</button>
<button on:click={testGetGameStat}>##Test Get GameStat##</button>
<button on:click={testPutPublicity}>##Test Put Publicity##</button>
