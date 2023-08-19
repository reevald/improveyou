<script>
  export let form;
  if (typeof localStorage !== 'undefined' && form) {
    localStorage.setItem('jwt', form?.jwt);
  }
</script>

<a href="/logout">Logout</a>
<a href="/home">Home</a>
<h1>Login page attempt 1</h1>

<form method="POST" action="?/login">
  <label>
    Url endpoint
    <input name="endpoint" type="text" />
  </label>
  <label>
    Cookie name
    <input name="cookieName" type="text" />
  </label>
  <label>
    Credential type
    <input name="credType" type="text" />
  </label>
  <label>
    Email
    <input name="email" type="email" />
  </label>
  <label>
    Password
    <input name="password" type="password" />
  </label>
  <button>Log in</button>
</form>
