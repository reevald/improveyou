<script>
  import { goto } from '$app/navigation';
  import { tryAccessWithAuth } from '$lib/api.js';
  import { onMount } from 'svelte';

  // console.log('[page signup] Its run server?');
  export let form;

  const capitalize = (string) => string.charAt(0).toUpperCase() + string.slice(1);
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
      } else if (form?.status == 400) {
        const msgUsername = form?.data?.username;
        const msgEmail = form?.data?.email;
        const msgPassword = form?.data?.password;

        const msgUsernameElem = document.getElementById('msgUsernameBox');
        const msgEmailElem = document.getElementById('msgEmailBox');
        const msgPasswordElem = document.getElementById('msgPasswordBox');

        const inpUsernameElem = document.querySelector('input[name="username"]');
        const inpEmailElem = document.querySelector('input[name="email"]');
        const inpPasswordElem = document.querySelector('input[name="password"]');

        inpUsernameElem.value = form?.req.username;
        inpEmailElem.value = form?.req.email;

        if (msgUsername) {
          msgUsernameElem.style.display = 'block';
          msgUsernameElem.innerText = msgUsername
            .map((msg) => capitalize(msg))
            .join(' ');
          inpUsernameElem.classList.add('ring-1', 'ring-red-500');
        } else {
          msgUsernameElem.style.display = 'none';
          inpUsernameElem.classList.remove('ring-1', 'ring-red-500');
        }

        if (msgEmail) {
          msgEmailElem.style.display = 'block';
          msgEmailElem.innerText = msgEmail.map((msg) => capitalize(msg)).join(' ');
          inpEmailElem.classList.add('ring-1', 'ring-red-500');
        } else {
          msgEmailElem.style.display = 'none';
          inpEmailElem.classList.remove('ring-1', 'ring-red-500');
        }

        if (msgPassword) {
          msgPasswordElem.style.display = 'block';
          msgPasswordElem.innerText = msgPassword
            .map((msg) => capitalize(msg))
            .join(' ');
          inpPasswordElem.classList.add('ring-1', 'ring-red-500');
        } else {
          msgPasswordElem.style.display = 'none';
          inpPasswordElem.classList.remove('ring-1', 'ring-red-500');
        }
      }
    } else {
      tryAccessWithAuth('GOIN');
    }
    const inputElem = document.querySelectorAll('.input-group input');
    const getLabelElem = (id) => document.querySelector(`label[for='${id}']`);
    if (inputElem) {
      inputElem.forEach((elem) => {
        if (elem.value != '') {
          getLabelElem(elem.getAttribute('id')).classList.add('animate-label');
        }
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
  <div class="flex flex-row justify-center mb-8 px-8 mt-8 z-20">
    <img src="/img/logo.png" class="w-auto xs:w-56" alt="" />
  </div>
  <form class="px-8 mb-8 z-20" method="POST" action="?/process">
    <div class="mb-4">
      <div class="input-group group">
        <label
          for="username"
          class="bg-sky-950 m-3 px-1 text-gray-400 cursor-text group-focus-within:cursor-default pointer-events-none"
          >Username</label
        >
        <input
          class="border-2 bg-sky-950 autofill:shadow-[inset_0_0_0px_1000px_rgb(8,47,73)] autofill:transition-colors autofill:duration-[5000000ms] border-sky-900 p-2.5 text-gray-300 focus:border-sky-400 outline-none rounded-md"
          type="text"
          name="username"
          id="username"
          required
        />
      </div>
      <div class="hidden text-xs pt-1 text-red-500" id="msgUsernameBox"></div>
    </div>
    <div class="mb-4">
      <div class="input-group group">
        <label
          for="email"
          class="bg-sky-950 m-3 px-1 text-gray-400 cursor-text group-focus-within:cursor-default pointer-events-none"
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
      <div class="hidden text-xs pt-1 text-red-500" id="msgEmailBox"></div>
    </div>
    <div class="mb-4">
      <div class="input-group group">
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
      <div class="hidden text-xs pt-1 text-red-500" id="msgPasswordBox"></div>
    </div>
    <button
      type="submit"
      class="bg-amber-500 hover:bg-amber-600 rounded-md text-lg font-bold flex flex-row items-center justify-center w-full h-12 mb-4"
    >
      Sign Up
    </button>
    <div class="text-gray-400">
      Already a member? <a
        href="login"
        class="text-amber-500 hover:text-amber-600 font-semibold">Login</a
      >
    </div>
  </form>
</div>
