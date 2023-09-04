<script>
  import { postWithAuth, putWithAuth } from '$lib/api.js';
  import AudioHandler from '$lib/audioHandler.js';
  import TimerHandler from '$lib/timerHandler.js';
  import { onDestroy, onMount } from 'svelte';
  export let data;
  let audMed;
  let timePickedIdx = 0; // As default

  const timeFormater = (secTime) => {
    return `${`0${Math.floor(secTime / 60)}`.slice(-2)}:${`0${secTime % 60}`.slice(
      -2
    )}`;
  };

  const rawTimeToSeconds = (rawTime) => {
    return rawTime.minutes * 60 + rawTime.seconds;
  };

  let IYTimer;
  let isDelayFinished = false;
  let isPostStart = true;
  onMount(async () => {
    const resizeWrap = () => {
      const wrapActElem = document.getElementById('wrapActivityBox');
      wrapActElem.style.height = `${window.innerHeight}px`;
    };
    resizeWrap();
    window.addEventListener('resize', () => {
      resizeWrap();
    });

    const ctrlPlayPauseBtnElem = document.getElementById('ctrlPlayPauseBtn');
    const ctrlReplayBtnElem = document.getElementById('ctrlReplayBtn');
    const trackTimeElem = document.getElementById('trackTimeBox');
    const delayTimerElem = document.getElementById('delayTimerBox');
    const progressBarElem = document.getElementById('progressBarBox');
    const wrapActDoneElem = document.getElementById('wrapActDoneBox');
    const okActDoneBtnElem = document.getElementById('okActDoneBtn');
    const wrapLoaderElem = document.getElementById('wrapLoaderBox');
    const wrapErrorElem = document.getElementById('wrapErrorBox');
    const okErrorBtnElem = document.getElementById('okErrorBtn');

    const targetTimeElem = document.getElementById('targetTimeBox');
    const secTime = data?.iyData?.resources?.data?.target?.values[timePickedIdx];
    targetTimeElem.innerText = timeFormater(secTime);
    trackTimeElem.innerText = '00:00';
    audMed = new AudioHandler({
      src: data?.iyData?.resources?.data?.audioPath
    });

    wrapLoaderElem.classList.remove('hidden');
    wrapLoaderElem.classList.add('flex');
    await audMed.setup();
    wrapLoaderElem.classList.add('hidden');
    wrapLoaderElem.classList.remove('flex');

    IYTimer = new TimerHandler();
    IYTimer.setup({
      interval: 1000,
      duration: data?.iyData?.resources?.data?.target?.values[timePickedIdx],
      type: 'INC',
      firstDelayDuration: 3
    });

    // Condition for re-play, done, and change duration
    const resetAll = () => {
      IYTimer.pause();
      IYTimer.reset();
      IYTimer.remove();
      if (audMed.audioCtx.state === 'suspended') {
        audMed.audioCtx.resume().then(() => {
          audMed.bufferSource.stop();
        });
      }
      audMed.bufferSource.stop();
      delayTimerElem.innerText = '';
      isPostStart = true;
      isDelayFinished = false;
      trackTimeElem.innerText = '00:00';
      progressBarElem.style.width = '0%';
      ctrlPlayPauseBtnElem.children[0].classList.remove('hidden');
      ctrlPlayPauseBtnElem.children[1].classList.add('hidden');
      ctrlPlayPauseBtnElem.setAttribute('data-btn', 'play');
      delayTimerElem.classList.remove('flex');
      delayTimerElem.classList.add('hidden');
      ctrlReplayBtnElem.classList.remove('flex');
      ctrlReplayBtnElem.classList.add('hidden');
    };

    const delayCB = (time) => {
      delayTimerElem.innerText = time;
    };

    const finishDelayCB = () => {
      delayTimerElem.classList.remove('flex');
      delayTimerElem.classList.add('hidden');
      ctrlPlayPauseBtnElem.children[1].classList.remove('hidden');
      ctrlPlayPauseBtnElem.setAttribute('data-btn', 'pause');
      isDelayFinished = true;

      if (audMed.audioCtx.state === 'suspended') {
        audMed.audioCtx.resume().then(() => {
          // audMed.bufferSource.stop();
          audMed.play();
        });
      } else {
        audMed.play();
      }
    };

    const timerCB = (time) => {
      progressBarElem.style.width = `${
        (rawTimeToSeconds(time) /
          data?.iyData?.resources?.data?.target?.values[timePickedIdx]) *
        100
      }%`;

      trackTimeElem.innerText = timeFormater(rawTimeToSeconds(time));
    };

    const finishTimerCB = async () => {
      const objFinishData = {
        activity_id: data?.iyData?.id
      };
      wrapLoaderElem.classList.remove('hidden');
      wrapLoaderElem.classList.add('flex');
      const respStatus = await putWithAuth(
        'user/me/activity/finish',
        objFinishData,
        false,
        (data) => {
          if (data?.activity_finished) {
            wrapLoaderElem.classList.add('hidden');
            wrapLoaderElem.classList.remove('flex');
            wrapActDoneElem.classList.remove('hidden');
            wrapActDoneElem.classList.add('flex');
          }
        }
      );
      // If error caused by glitch (activity already finished but double request finish)
      if (respStatus != 200) {
        wrapErrorElem.classList.remove('hidden');
        wrapErrorElem.classList.add('flex');
      }
      resetAll();
    };

    okActDoneBtnElem.addEventListener('click', () => {
      wrapActDoneElem.classList.add('hidden');
      wrapActDoneElem.classList.remove('flex');
    });

    okErrorBtnElem.addEventListener('click', () => {
      wrapErrorElem.classList.add('hidden');
      wrapErrorElem.classList.remove('flex');
    });

    ctrlReplayBtnElem.addEventListener('click', () => {
      resetAll();
    });

    const successStartCB = (data) => {
      IYTimer.start(delayCB, finishDelayCB, timerCB, finishTimerCB);
      wrapLoaderElem.classList.add('hidden');
      wrapLoaderElem.classList.remove('flex');
    };

    ctrlPlayPauseBtnElem.addEventListener('click', async (event) => {
      if (event.target.getAttribute('data-btn') == 'play') {
        event.target.children[0].classList.add('hidden');
        if (isDelayFinished) {
          event.target.children[1].classList.remove('hidden');
          if (audMed.audioCtx.state === 'suspended') {
            await audMed.audioCtx.resume();
          }
          IYTimer.resume();
        } else {
          delayTimerElem.classList.remove('hidden');
          delayTimerElem.classList.add('flex');
          IYTimer.isFirstDelay = true;
          delayTimerElem.innerText = '';
          IYTimer.setup({
            interval: 1000,
            duration: data?.iyData?.resources?.data?.target?.values[timePickedIdx],
            type: 'INC',
            firstDelayDuration: 3
          });

          const objInitData = {
            activity_id: data?.iyData?.id,
            activity_data: {
              target: {
                type: data?.iyData?.resources?.data?.target?.type,
                value_choosed:
                  data?.iyData?.resources?.data?.target?.values[timePickedIdx],
                unit: data?.iyData?.resources?.data?.target?.unit
              }
            }
          };
          if (isPostStart) {
            isPostStart = false;
            wrapLoaderElem.classList.remove('hidden');
            wrapLoaderElem.classList.add('flex');
            const respStatus = await postWithAuth(
              'user/me/activity/start',
              objInitData,
              false,
              successStartCB
            );
            if (respStatus != 200) {
              wrapErrorElem.classList.remove('hidden');
              wrapErrorElem.classList.add('flex');
              resetAll();
            }
          } else {
            IYTimer.start(delayCB, finishDelayCB, timerCB, finishTimerCB);
          }
        }
        ctrlReplayBtnElem.classList.remove('flex');
        ctrlReplayBtnElem.classList.add('hidden');
        event.target.setAttribute('data-btn', 'pause');
      } else if (event.target.getAttribute('data-btn') == 'pause') {
        IYTimer.pause();
        if (audMed.audioCtx.state === 'running') {
          await audMed.audioCtx.suspend();
        }
        delayTimerElem.classList.add('hidden');
        event.target.children[0].classList.remove('hidden');
        event.target.children[1].classList.add('hidden');
        event.target.setAttribute('data-btn', 'play');
        if (isDelayFinished) {
          ctrlReplayBtnElem.classList.remove('hidden');
          ctrlReplayBtnElem.classList.add('flex');
        }
      }
    });
  });
  onDestroy(() => {
    IYTimer.pause();
    IYTimer.reset();
    IYTimer.remove();
    if (audMed) {
      audMed?.audioCtx.close();
    }
  });
</script>

<div id="wrapActivityBox" class="relative max-h-screen pb-40 bg-amber-50 text-gray-600">
  <div
    class="h-full overflow-y-auto w-full px-1.5 xxs:px-2.5 xs:px-4 pt-6 pb-14 flex flex-col items-center"
  >
    <a href="/activities" class="flex flex-row items-center w-full mb-2">
      <div class="mr-2">
        <svg
          class="w-4 fill-gray-600"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 512 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M177.5 414c-8.8 3.8-19 2-26-4.6l-144-136C2.7 268.9 0 262.6 0 256s2.7-12.9 7.5-17.4l144-136c7-6.6 17.2-8.4 26-4.6s14.5 12.5 14.5 22l0 72 288 0c17.7 0 32 14.3 32 32l0 64c0 17.7-14.3 32-32 32l-288 0 0 72c0 9.6-5.7 18.2-14.5 22z"
          /></svg
        >
      </div>
      <div class="font-bold text-gray-600">Back</div>
    </a>
    <div class="font-oswald text-2xl font-semibold text-gray-700 mb-4">
      {data?.iyData?.name}
    </div>
    <div
      class="h-[160px] w-[160px] xs:w-[240px] xs:h-[240px] xxs:w-[200px] xxs:h-[200px] bg-amber-100 relative rounded-xl mb-6 shadow-md shadow-amber-300 overflow-hidden shrink-0"
    >
      <div class="w-full h-full flex flex-row justify-center items-center">
        <svg
          class="w-16 h-16 fill-amber-200 animate-pulse"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 512 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M0 96C0 60.7 28.7 32 64 32H448c35.3 0 64 28.7 64 64V416c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V96zM323.8 202.5c-4.5-6.6-11.9-10.5-19.8-10.5s-15.4 3.9-19.8 10.5l-87 127.6L170.7 297c-4.6-5.7-11.5-9-18.7-9s-14.2 3.3-18.7 9l-64 80c-5.8 7.2-6.9 17.1-2.9 25.4s12.4 13.6 21.6 13.6h96 32H424c8.9 0 17.1-4.9 21.2-12.8s3.6-17.4-1.4-24.7l-120-176zM112 192a48 48 0 1 0 0-96 48 48 0 1 0 0 96z"
          /></svg
        >
      </div>
      <div class=" absolute top-0 left-0">
        <img
          class="group-hover:scale-110 transition-all ease-in duration-300"
          src={data?.iyData?.thumbnail_path}
          alt="Meditation"
        />
      </div>
      <!-- <img src={data?.activity?.thumbnail_path} alt="" /> -->
    </div>
    <div class="text-lg font-oswald font-semibold text-gray-700 mb-2">Instructions</div>
    <div
      class="w-full bg-amber-100 pt-4 pb-2 pr-2 shadow-inner rounded-xl shrink-0 text-sm text-amber-950 mb-6"
    >
      <ul class="list-disc ml-7">
        {#each data?.iyData?.resources?.data?.instructions as step}
          <li class="mb-2">
            {step}
          </li>
        {/each}
      </ul>
    </div>
    <div class="text-lg font-oswald font-semibold text-gray-700 mb-2">Credits</div>
    <div
      class="w-full bg-amber-100 pt-4 pb-2 pr-2 shadow-inner rounded-xl shrink-0 text-sm text-amber-950"
    >
      <ul class="list-disc ml-7">
        {#each data?.iyData?.resources?.data?.credits as credit}
          <li class="mb-2">
            <a
              target="_blank"
              rel="noopener noreferrer"
              class="hover:underline"
              href={credit.link}>{credit.title}</a
            >
          </li>
        {/each}
      </ul>
    </div>
  </div>
  <!-- Control Time Panel -->
  <div
    class="absolute bottom-0 left-0 bg-amber-500 pb-16 w-full flex flex-col items-center px-1.5 xxs:px-2.5 xs:px-4 rounded-t-xl"
  >
    <div class="-mt-9 relative">
      <div
        id="ctrlPlayPauseBtn"
        data-btn="play"
        class="bg-amber-400 rounded-full p-4 flex flex-row justify-center items-center ring-8 ring-amber-500 cursor-pointer group"
      >
        <!-- Play Button -->
        <svg
          class=" h-10 w-10 pl-1 fill-amber-200 group-hover:fill-amber-100 pointer-events-none"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 384 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M73 39c-14.8-9.1-33.4-9.4-48.5-.9S0 62.6 0 80V432c0 17.4 9.4 33.4 24.5 41.9s33.7 8.1 48.5-.9L361 297c14.3-8.7 23-24.2 23-41s-8.7-32.2-23-41L73 39z"
          /></svg
        >
        <!-- Pause Button -->
        <svg
          class="hidden h-10 w-10 fill-amber-200 animate-spin group-hover:fill-amber-100 pointer-events-none"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 320 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M48 64C21.5 64 0 85.5 0 112V400c0 26.5 21.5 48 48 48H80c26.5 0 48-21.5 48-48V112c0-26.5-21.5-48-48-48H48zm192 0c-26.5 0-48 21.5-48 48V400c0 26.5 21.5 48 48 48h32c26.5 0 48-21.5 48-48V112c0-26.5-21.5-48-48-48H240z"
          /></svg
        >
        <!-- Delay -->
        <div
          id="delayTimerBox"
          class="hidden w-10 h-10 flex-row justify-center items-center text-5xl font-oswald font-bold text-amber-200 pointer-events-none"
        ></div>
      </div>
      <!-- Replay Button -->
      <div
        id="ctrlReplayBtn"
        class="absolute top-4 -left-16 hidden flex-row justify-center items-center"
      >
        <div
          class="bg-amber-400 rounded-full p-2 flex flex-row justify-center items-center ring-8 ring-amber-500 group cursor-pointer"
        >
          <svg
            class="h-7 w-7 fill-amber-200 group-hover:fill-amber-100"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 512 512"
            ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
              d="M48.5 224H40c-13.3 0-24-10.7-24-24V72c0-9.7 5.8-18.5 14.8-22.2s19.3-1.7 26.2 5.2L98.6 96.6c87.6-86.5 228.7-86.2 315.8 1c87.5 87.5 87.5 229.3 0 316.8s-229.3 87.5-316.8 0c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0c62.5 62.5 163.8 62.5 226.3 0s62.5-163.8 0-226.3c-62.2-62.2-162.7-62.5-225.3-1L185 183c6.9 6.9 8.9 17.2 5.2 26.2s-12.5 14.8-22.2 14.8H48.5z"
            /></svg
          >
        </div>
      </div>
    </div>
    <div
      class="flex flex-row w-full justify-between text-md font-semibold text-amber-900"
    >
      <div id="trackTimeBox"></div>
      <div id="targetTimeBox"></div>
    </div>
    <div class="relative bg-amber-200 w-full h-2 rounded-full overflow-hidden mb-7">
      <div
        id="progressBarBox"
        class="h-full absolute bg-amber-600"
        style="width:0%;"
      ></div>
    </div>
  </div>
</div>

<!-- Wrap notification activity done -->
<div
  id="wrapActDoneBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="text-lg font-bold mb-3">Info</div>
    <div class="text-sm text-center mb-3">
      The <span class="font-semibold">{data?.iyData?.name}</span>
      {data?.iyData?.category} activity was successfully completed.
    </div>
    <div
      id="okActDoneBtn"
      class="px-5 py-1.5 rounded-xl bg-amber-400 cursor-pointer hover:bg-amber-500 font-semibold"
    >
      Ok
    </div>
  </div>
</div>

<!-- Wrap notification somthing wrong -->
<div
  id="wrapErrorBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="text-lg font-bold mb-3">Something wrong!</div>
    <div class="text-sm text-center mb-3">Please try again.</div>
    <div
      id="okErrorBtn"
      class="px-5 py-1.5 rounded-xl bg-amber-400 cursor-pointer hover:bg-amber-500 font-semibold"
    >
      Ok
    </div>
  </div>
</div>

<!-- Loading Wrap -->
<div
  id="wrapLoaderBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-30 pb-16"
>
  <div class="animate-spin fill-amber-500">
    <svg class="w-14 h-14" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
      ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
        d="M304 48a48 48 0 1 0 -96 0 48 48 0 1 0 96 0zm0 416a48 48 0 1 0 -96 0 48 48 0 1 0 96 0zM48 304a48 48 0 1 0 0-96 48 48 0 1 0 0 96zm464-48a48 48 0 1 0 -96 0 48 48 0 1 0 96 0zM142.9 437A48 48 0 1 0 75 369.1 48 48 0 1 0 142.9 437zm0-294.2A48 48 0 1 0 75 75a48 48 0 1 0 67.9 67.9zM369.1 437A48 48 0 1 0 437 369.1 48 48 0 1 0 369.1 437z"
      /></svg
    >
  </div>
  <div class="mt-3 font-semibold text-xl font-oswald text-white">Load audio...</div>
</div>
