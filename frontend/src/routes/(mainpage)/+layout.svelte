<script>
  // console.log('[Layout mainpage] its run server?');
  import { tryAccessWithAuth } from '$lib/api';
  export let data;
</script>

{#await tryAccessWithAuth('GOOUT') then isAccess}
  {#if isAccess}
    <div class="flex flex-row justify-center max-h-screen h-full w-full">
      <div
        id="bigWrapBox"
        class="relative w-[480px] flex-col items-center drop-shadow-xl"
      >
        <slot />
        <div
          class="absolute bottom-0 bg-white w-full h-16 rounded-t-xl flex flex-row items-center justify-between p-0.5 xxs:p-2 xs:p-4 text-xs xs:text-sm z-30"
        >
          <a
            href="/home"
            class="flex flex-row items-center p-1 rounded-3xl cursor-pointer group {data.isPageHome
              ? 'w-[90px] xs:w-[96px] bg-amber-400'
              : 'bg-amber-300 hover:bg-amber-400 w-[48px] hover:w-[90px] xs:hover:w-[96px] transition-all ease-in-out duration-300 overflow-hidden'}"
          >
            <div
              class="rounded-full p-1.5 {data.isPageHome
                ? 'bg-amber-300'
                : 'bg-amber-200 group-hover:bg-amber-300'} fill-amber-500"
            >
              <svg
                class="w-7 h-7"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 576 512"
                ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                  d="M543.8 287.6c17 0 32-14 32-32.1c1-9-3-17-11-24L512 185V64c0-17.7-14.3-32-32-32H448c-17.7 0-32 14.3-32 32v36.7L309.5 7c-6-5-14-7-21-7s-15 1-22 8L10 231.5c-7 7-10 15-10 24c0 18 14 32.1 32 32.1h32V448c0 35.3 28.7 64 64 64H448.5c35.5 0 64.2-28.8 64-64.3l-.7-160.2h32zM288 160a64 64 0 1 1 0 128 64 64 0 1 1 0-128zM176 400c0-44.2 35.8-80 80-80h64c44.2 0 80 35.8 80 80c0 8.8-7.2 16-16 16H192c-8.8 0-16-7.2-16-16z"
                /></svg
              >
            </div>
            <div
              class="font-semibold mx-1 {data.isPageHome
                ? 'text-gray-900'
                : 'text-gray-600 group-hover:text-gray-900'} whitespace-nowrap flex"
            >
              Home
            </div>
          </a>
          <a
            href="/activities"
            class="flex flex-row items-center p-1 rounded-3xl cursor-pointer group {data.isPageActivity
              ? 'w-[98px] xs:w-[106px] bg-amber-400'
              : 'bg-amber-300 hover:bg-amber-400 w-[48px] hover:w-[98px] xs:hover:w-[106px] transition-all ease-in-out duration-300 overflow-hidden'}"
          >
            <div
              class="rounded-full p-1.5 {data.isPageActivity
                ? 'bg-amber-300'
                : 'bg-amber-200 group-hover:bg-amber-300'} fill-amber-500"
            >
              <svg
                class="w-7 h-7"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 320 512"
                ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                  d="M160 48a48 48 0 1 1 96 0 48 48 0 1 1 -96 0zM126.5 199.3c-1 .4-1.9 .8-2.9 1.2l-8 3.5c-16.4 7.3-29 21.2-34.7 38.2l-2.6 7.8c-5.6 16.8-23.7 25.8-40.5 20.2s-25.8-23.7-20.2-40.5l2.6-7.8c11.4-34.1 36.6-61.9 69.4-76.5l8-3.5c20.8-9.2 43.3-14 66.1-14c44.6 0 84.8 26.8 101.9 67.9L281 232.7l21.4 10.7c15.8 7.9 22.2 27.1 14.3 42.9s-27.1 22.2-42.9 14.3L247 287.3c-10.3-5.2-18.4-13.8-22.8-24.5l-9.6-23-19.3 65.5 49.5 54c5.4 5.9 9.2 13 11.2 20.8l23 92.1c4.3 17.1-6.1 34.5-23.3 38.8s-34.5-6.1-38.8-23.3l-22-88.1-70.7-77.1c-14.8-16.1-20.3-38.6-14.7-59.7l16.9-63.5zM68.7 398l25-62.4c2.1 3 4.5 5.8 7 8.6l40.7 44.4-14.5 36.2c-2.4 6-6 11.5-10.6 16.1L54.6 502.6c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L68.7 398z"
                /></svg
              >
            </div>
            <div
              class="font-semibold mx-1 {data.isPageActivity
                ? 'text-gray-900'
                : 'text-gray-600 group-hover:text-gray-900'} whitespace-nowrap flex"
            >
              Activity
            </div>
          </a>
          <a
            href="/leaderboard"
            class="flex flex-row items-center p-1 rounded-3xl cursor-pointer group {data.isPageLeaderboard
              ? 'w-[130px] xs:w-[144px] bg-amber-400'
              : 'bg-amber-300 hover:bg-amber-400 w-[48px] hover:w-[130px] xs:hover:w-[144px] transition-all ease-in-out duration-300 overflow-hidden'}"
          >
            <div
              class="rounded-full p-1.5 {data.isPageLeaderboard
                ? 'bg-amber-300'
                : 'bg-amber-200 group-hover:bg-amber-300'} fill-amber-500"
            >
              <svg
                class="w-7 h-7"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 640 512"
                ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                  d="M353.8 54.1L330.2 6.3c-3.9-8.3-16.1-8.6-20.4 0L286.2 54.1l-52.3 7.5c-9.3 1.4-13.3 12.9-6.4 19.8l38 37-9 52.1c-1.4 9.3 8.2 16.5 16.8 12.2l46.9-24.8 46.6 24.4c8.6 4.3 18.3-2.9 16.8-12.2l-9-52.1 38-36.6c6.8-6.8 2.9-18.3-6.4-19.8l-52.3-7.5zM256 256c-17.7 0-32 14.3-32 32V480c0 17.7 14.3 32 32 32H384c17.7 0 32-14.3 32-32V288c0-17.7-14.3-32-32-32H256zM32 320c-17.7 0-32 14.3-32 32V480c0 17.7 14.3 32 32 32H160c17.7 0 32-14.3 32-32V352c0-17.7-14.3-32-32-32H32zm416 96v64c0 17.7 14.3 32 32 32H608c17.7 0 32-14.3 32-32V416c0-17.7-14.3-32-32-32H480c-17.7 0-32 14.3-32 32z"
                /></svg
              >
            </div>
            <div
              class="font-semibold mx-1 {data.isPageLeaderboard
                ? 'text-gray-900'
                : 'text-gray-600 group-hover:text-gray-900'} whitespace-nowrap flex"
            >
              Leaderboard
            </div>
          </a>
          <a
            href="/tracker"
            class="flex flex-row items-center p-1 rounded-3xl cursor-pointer group {data.isPageTracker
              ? 'w-[98px] xs:w-[108px] bg-amber-400'
              : 'bg-amber-300 hover:bg-amber-400 w-[48px] hover:w-[98px] xs:hover:w-[108px] transition-all ease-in-out duration-300 overflow-hidden'}"
          >
            <div
              class="rounded-full p-1.5 {data.isPageTracker
                ? 'bg-amber-300'
                : 'bg-amber-200 group-hover:bg-amber-300'} fill-amber-500"
            >
              <svg
                class="w-7 h-7"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 448 512"
                ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                  d="M128 0c13.3 0 24 10.7 24 24V64H296V24c0-13.3 10.7-24 24-24s24 10.7 24 24V64h40c35.3 0 64 28.7 64 64v16 48V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V192 144 128C0 92.7 28.7 64 64 64h40V24c0-13.3 10.7-24 24-24zM400 192H48V448c0 8.8 7.2 16 16 16H384c8.8 0 16-7.2 16-16V192zM329 297L217 409c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47 95-95c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"
                /></svg
              >
            </div>
            <div
              class="font-semibold mx-1 {data.isPageTracker
                ? 'text-gray-900'
                : 'text-gray-600 group-hover:text-gray-900'} whitespace-nowrap flex"
            >
              Tracker
            </div>
          </a>
        </div>
      </div>
    </div>
  {/if}
{/await}
