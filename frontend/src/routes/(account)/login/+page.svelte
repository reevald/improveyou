<script>
  import { goto } from '$app/navigation';
  import { tryAccessWithAuth } from '$lib/api.js';
  import { onMount } from 'svelte';

  // console.log('[page login] Its run server?');
  export let form;

  onMount(() => {
    if (form) {
      if (typeof localStorage !== 'undefined' && form?.data?.jwt) {
        localStorage.setItem('jwt', form.data.jwt);
      }
      if (form?.status == 200) {
        goto('home');
      } else if (form?.status == 429) {
        const detail = form?.data?.detail;
        goto(`429-too-many-requests?sec=${detail.match(/\d+/)}`);
      } else {
        const msgElem = document.getElementById('messageBox');
        msgElem.style.display = 'flex';
        msgElem.children[1].innerText = form?.data?.detail;
      }
    } else {
      tryAccessWithAuth('GOIN');
    }

    const inputElem = document.querySelectorAll('.input-group input');
    const getLabelElem = (id) => document.querySelector(`label[for='${id}']`);
    if (inputElem) {
      inputElem.forEach((elem) => {
        elem.addEventListener('focus', (event) => {
          getLabelElem(event.target.getAttribute('id')).classList.add('animate-label');
        });
        elem.addEventListener('blur', (event) => {
          if (event.target.value == '') {
            getLabelElem(event.target.getAttribute('id')).classList.remove(
              'animate-label'
            );
          }
        });
      });
    }
  });
</script>

<div
  class="bg-sky-950 flex flex-col justify-center w-full xs:w-96 rounded-md xs:shadow-gray-950/80 shadow-2xl z-20 max-h-screen h-full xs:h-auto"
>
  <div class="flex flex-row justify-center mb-6 px-8 mt-8 z-20">
    <img src="/img/logo.png" class="w-auto xs:w-56" alt="" />
  </div>
  <form class="px-8 mb-8 z-30 overflow-y-auto" method="POST" action="?/process">
    <div
      id="messageBox"
      class="bg-red-200 hidden p-2 mb-4 flex-row items-start rounded-md"
    >
      <div class="w-10 mr-2">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
          ><path
            d="M12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22ZM12 20C16.4183 20 20 16.4183 20 12C20 7.58172 16.4183 4 12 4C7.58172 4 4 7.58172 4 12C4 16.4183 7.58172 20 12 20ZM11 15H13V17H11V15ZM11 7H13V13H11V7Z"
            fill="rgba(239,68,68,1)"
          /></svg
        >
      </div>
      <div class="text-sm w-full"></div>
    </div>
    <div class="input-group group mb-4 mt-2">
      <label
        for="email"
        class="bg-sky-950 z-30 m-3 px-1 text-gray-400 cursor-text group-focus-within:cursor-default pointer-events-none"
        >Email</label
      >
      <input
        class="border-2 bg-sky-950 autofill:shadow-[inset_0_0_0px_1000px_rgb(8,47,73)] autofill:transition-colors autofill:duration-[5000000ms] border-sky-900 p-2.5 text-gray-300 focus:border-sky-400 outline-none rounded-md"
        type="email"
        name="email"
        id="email"
        required
      />
    </div>
    <div class="input-group group mb-4">
      <label
        for="password"
        class="bg-sky-950 m-3 px-1 text-gray-400 group-focus-within:cursor-default pointer-events-none"
        >Password</label
      >
      <input
        class="border-2 bg-sky-950 border-sky-900 p-2.5 text-gray-300 focus:border-sky-400 outline-none rounded-md"
        type="password"
        name="password"
        id="password"
        required
      />
    </div>
    <button
      type="submit"
      class="bg-amber-500 hover:bg-amber-600 rounded-md text-lg font-bold flex flex-row items-center justify-center w-full h-12 mb-4"
    >
      Login
    </button>
    <div class="text-gray-400">
      Not a member yet? <a
        href="signup"
        class="text-amber-500 hover:text-amber-600 font-semibold">Sign Up</a
      >
    </div>
  </form>
</div>
