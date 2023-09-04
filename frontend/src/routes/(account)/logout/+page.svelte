<script>
  import { onMount } from 'svelte';

  export let data;
  onMount(() => {
    if (typeof localStorage !== 'undefined' && data?.status == 'success')
      localStorage.removeItem('jwt');
  });
</script>

<div class="flex flex-col items-center">
  <h1 class="mb-6 font-oswald text-3xl text-white">Logout Successfully</h1>
  <a
    href="/login"
    class="bg-white p-2 rounded-xl text-gray-900 font-semibold cursor-pointer"
    >Go to Login</a
  >
</div>
