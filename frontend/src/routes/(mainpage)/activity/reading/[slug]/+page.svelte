<script>
  import { postWithAuth, putWithAuth } from '$lib/api.js';
  import { onMount } from 'svelte';
  export let data;

  // See: https://stackoverflow.com/a/19270021
  const getRandom = (arr, n) => {
    const result = new Array(n);
    let len = arr.length;
    let taken = new Array(len);

    if (n > len) throw new RangeError('getRandom: more elements taken than available');
    while (n--) {
      var x = Math.floor(Math.random() * len);
      result[n] = arr[x in taken ? taken[x] : x];
      taken[x] = --len in taken ? taken[len] : len;
    }
    return result;
  };

  const resizeWrap = (wrapElem) => {
    wrapElem.style.height = `${window.innerHeight}px`;
  };

  let currQnaIdx = 0;
  let dataOpt;

  let currHeart = data?.iyData?.resources?.data?.attempt;
  let currStar = 0;

  let orderQna;

  onMount(async () => {
    const wrapActElem = document.getElementById('wrapActivityBox');

    resizeWrap(wrapActElem);
    window.addEventListener('resize', () => {
      resizeWrap(wrapActElem);
    });

    const articleElem = document.getElementById('articleBox');
    const wrapLoaderElem = document.getElementById('wrapLoaderBox');
    const coverArticleElem = document.getElementById('coverArticleBox');
    const mainPanelElem = document.getElementById('mainPanelBox');
    const startPanelElem = document.getElementById('startPanelBox');
    const startBtnElem = document.getElementById('startBtn');
    const heartElem = document.getElementById('heartBox');
    const starTrackElem = document.getElementById('starTrackBox');
    const wrapOptionElem = document.getElementById('wrapOptionBox');
    const closeOptionBtnElem = document.getElementById('closeOptionBtn');
    const mainOptionElem = document.getElementById('mainOptionBox');
    const wrapErrorElem = document.getElementById('wrapErrorBox');
    const okErrorBtnElem = document.getElementById('okErrorBtn');
    const wrapAnswerWrongElem = document.getElementById('wrapAnswerWrongBox');
    const wrapAnswerCorrectElem = document.getElementById('wrapAnswerCorrectBox');
    const okAnswerWrongBtnElem = document.getElementById('okAnswerWrongBtn');
    const okAnswerCorrectBtnElem = document.getElementById('okAnswerCorrectBtn');
    const wrapActDoneElem = document.getElementById('wrapActDoneBox');
    const okActDoneBtnElem = document.getElementById('okActDoneBtn');
    const progressBarElem = document.getElementById('progressBarBox');

    okActDoneBtnElem.addEventListener('click', () => {
      wrapActDoneElem.classList.add('hidden');
      wrapActDoneElem.classList.remove('flex');
      wrapOptionElem.classList.add('hidden');
      wrapOptionElem.classList.remove('flex');
    });

    okAnswerCorrectBtnElem.addEventListener('click', () => {
      wrapAnswerCorrectElem.classList.add('hidden');
      wrapAnswerCorrectElem.classList.remove('flex');
      wrapOptionElem.classList.add('hidden');
      wrapOptionElem.classList.remove('flex');
    });

    okAnswerWrongBtnElem.addEventListener('click', () => {
      wrapAnswerWrongElem.classList.add('hidden');
      wrapAnswerWrongElem.classList.remove('flex');
      wrapOptionElem.classList.add('hidden');
      wrapOptionElem.classList.remove('flex');
    });

    const determineContinueOrFinish = (respData) => {
      const targetElem = document.getElementById(`qna-${respData?.activity_quiz?.id}`);
      if (respData?.activity_finished) {
        wrapActDoneElem.classList.add('flex');
        wrapActDoneElem.classList.remove('hidden');
      } else {
        currQnaIdx += 1; // Since start with 0
        if (currQnaIdx < data?.iyData?.resources?.data?.target?.values[0]) {
          renderQnaBtn(orderQna[currQnaIdx]);
        }
      }

      if (respData?.answer_status) {
        currStar += 1;
        wrapAnswerCorrectElem.classList.add('flex');
        wrapAnswerCorrectElem.classList.remove('hidden');
        targetElem.outerHTML = `
          <span class="inline-flex align-middle bg-amber-400 p-1 rounded-full">
            <svg class="w-6 h-6 fill-amber-900" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512">
              <path class="fill-amber-900" d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z"/>
            </svg>
          </span>
        `;
      } else {
        currHeart -= 1;
        wrapAnswerWrongElem.classList.add('flex');
        wrapAnswerWrongElem.classList.remove('hidden');
        targetElem.remove();
      }

      progressBarElem.style.width = `${
        (currStar / data?.iyData?.resources?.data?.target?.values[0]) * 100
      }%`;
      heartElem.innerHTML = `&#215; ${currHeart}`;
      starTrackElem.innerText = `${currStar}/${data?.iyData?.resources?.data?.target?.values[0]}`;
    };

    const judgeAnswer = async (id, answer) => {
      const objAnswer = {
        activity_id: data?.iyData?.id,
        activity_quiz: { id, answer }
      };

      const respStatus = await putWithAuth(
        'user/me/activity/quiz',
        objAnswer,
        false,
        determineContinueOrFinish
      );

      if (respStatus != 200) {
        wrapErrorElem.classList.add('flex');
        wrapErrorElem.classList.remove('hidden');
      }
    };

    const qnaHandler = (num) => {
      wrapOptionElem.classList.remove('hidden');
      wrapOptionElem.classList.add('flex');

      const orderOption = getRandom(['A', 'B', 'C', 'D'], 4);
      let htmlOption = '';
      orderOption.forEach((opt) => {
        htmlOption += `
          <div
            data-answer="${opt}"
            class="bg-white p-2 shadow-sm shadow-amber-400 cursor-pointer hover:text-amber-900 hover:bg-amber-100 rounded-xl mb-2"
          >
            ${dataOpt.qna[num - 1].options[opt]}
          </div>
        `;
      });

      mainOptionElem.innerHTML = htmlOption;

      for (let i = 0; i < 4; i++) {
        mainOptionElem.children[i].addEventListener('click', async (event) => {
          await judgeAnswer(num, event.target.getAttribute('data-answer'));
        });
      }
    };

    closeOptionBtnElem.addEventListener('click', () => {
      wrapOptionElem.classList.add('hidden');
      wrapOptionElem.classList.remove('flex');
    });

    okErrorBtnElem.addEventListener('click', () => {
      wrapErrorElem.classList.add('hidden');
      wrapErrorElem.classList.remove('flex');
    });

    const renderQnaBtn = (num) => {
      const targetElem = document.getElementById(`qna-${num}`);
      targetElem.addEventListener('click', () => {
        qnaHandler(num);
      });
      targetElem.innerHTML = `
          <span class="bg-amber-300 hover:bg-amber-400 cursor-pointer text-sm font-semibold py-1 px-2 rounded-xl text-amber-900">
            Get Star
          </span>
        `;
    };

    const successStartCB = (data) => {};

    const initStart = async () => {
      wrapLoaderElem.classList.remove('hidden');
      wrapLoaderElem.classList.add('flex');

      const objInitData = {
        activity_id: data?.iyData?.id,
        activity_data: {
          target: {
            type: data?.iyData?.resources?.data?.target?.type,
            value_choosed: data?.iyData?.resources?.data?.target?.values[0],
            unit: data?.iyData?.resources?.data?.target?.unit
          }
        }
      };

      const respStatus = await postWithAuth(
        'user/me/activity/start',
        objInitData,
        false,
        successStartCB
      );
      const respArticle = await fetch(data?.iyData?.resources?.data?.articlePath);
      const respQna = await fetch(data?.iyData?.resources?.data?.qnaPath);
      if (respArticle.ok && respQna.ok && respStatus == 200) {
        const htmlArticle = await respArticle.text();
        dataOpt = await respQna.json();
        articleElem.innerHTML = htmlArticle;
        articleElem.classList.remove('hidden');
        articleElem.classList.add('flex');
        wrapLoaderElem.classList.add('hidden');
        wrapLoaderElem.classList.remove('flex');
        orderQna = getRandom(
          Array.from({ length: dataOpt.qna.length }, (_, i) => i + 1),
          data?.iyData?.resources?.data?.target?.values[0]
        ).sort((a, b) => a - b);
        renderQnaBtn(orderQna[currQnaIdx]);
        heartElem.innerHTML = `&#215; ${currHeart}`;
        starTrackElem.innerText = `${currStar}/${data?.iyData?.resources?.data?.target?.values[0]}`;
      } else {
        wrapErrorElem.classList.add('flex');
        wrapErrorElem.classList.remove('hidden');
      }
    };

    startBtnElem.addEventListener('click', async () => {
      await initStart();
      coverArticleElem.classList.add('hidden');
      coverArticleElem.classList.remove('flex');
      startPanelElem.classList.add('hidden');
      startPanelElem.classList.remove('flex');
      mainPanelElem.classList.remove('hidden');
      mainPanelElem.classList.add('flex');
    });
  });
</script>

<div id="wrapActivityBox" class="relative max-h-screen pb-32 bg-amber-50 text-gray-600">
  <div
    id="coverArticleBox"
    class="flex h-full overflow-y-auto w-full px-1.5 xxs:px-2.5 xs:px-4 pt-6 pb-6 flex-col items-center"
  >
    <div class="flex flex-row items-center w-full mb-2">
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
    </div>
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
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M0 96C0 60.7 28.7 32 64 32H448c35.3 0 64 28.7 64 64V416c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V96zM323.8 202.5c-4.5-6.6-11.9-10.5-19.8-10.5s-15.4 3.9-19.8 10.5l-87 127.6L170.7 297c-4.6-5.7-11.5-9-18.7-9s-14.2 3.3-18.7 9l-64 80c-5.8 7.2-6.9 17.1-2.9 25.4s12.4 13.6 21.6 13.6h96 32H424c8.9 0 17.1-4.9 21.2-12.8s3.6-17.4-1.4-24.7l-120-176zM112 192a48 48 0 1 0 0-96 48 48 0 1 0 0 96z"
          /></svg
        >
      </div>
      <div class=" absolute top-0 left-0">
        <img
          class="group-hover:scale-110 transition-all ease-in duration-300"
          src={data?.iyData?.thumbnail_path}
          alt="Exercise"
        />
      </div>
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
  <!-- Main -->
  <div
    id="articleBox"
    class="hidden h-full overflow-y-auto w-full px-1.5 xxs:px-2.5 xs:px-4 pt-6 pb-6 flex-col items-center"
  ></div>
  <!-- Panel -->
  <div
    class="absolute bottom-0 left-0 bg-amber-500 pb-16 w-full px-1.5 xxs:px-2.5 xs:px-4 rounded-t-xl pt-3"
  >
    <div id="mainPanelBox" class="w-full hidden flex-col items-center">
      <div
        class="flex flex-row w-full justify-between font-semibold text-amber-900 mb-1"
      >
        <div class="flex flex-row items-center">
          <div class="mr-1">
            <svg
              class="w-5 h-5 fill-amber-900"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 512 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M47.6 300.4L228.3 469.1c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9L464.4 300.4c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141C347 36.5 300.6 51.4 268 84L256 96 244 84c-32.6-32.6-79-47.5-124.6-39.9C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z"
              /></svg
            >
          </div>
          <div id="heartBox"></div>
        </div>
        <div class="flex flex-row items-center">
          <div class="mr-1">
            <svg
              class="w-5 h-5 fill-amber-900"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 576 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z"
              /></svg
            >
          </div>
          <div id="starTrackBox"></div>
        </div>
      </div>
      <div class="relative bg-amber-300 w-full h-2 rounded-full overflow-hidden mb-4">
        <div
          id="progressBarBox"
          class="h-full absolute bg-amber-900"
          style="width:0%;"
        ></div>
      </div>
    </div>
    <div
      id="startPanelBox"
      class="flex mb-3 w-full flex-row justify-center items-center"
    >
      <div
        id="startBtn"
        class="bg-amber-300 py-2 px-12 rounded-xl font-semibold text-amber-900 hover:bg-amber-400 hover:text-amber-950 cursor-pointer"
      >
        Start
      </div>
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

<!-- Wrap option -->
<div
  id="wrapOptionBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div class="w-full overflow-y-auto flex flex-col items-center">
    <div
      class="relative max-w-xs bg-white py-4 px-0 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
    >
      <div class="mb-3 flex flex-row justify-between">
        <div class="font-semibold ml-4">What is the conclusion of the paragraph?</div>
        <div id="closeOptionBtn" class="fill-amber-400 cursor-pointer ml-2 mr-3 -mt-1">
          <svg class="w-7 h-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
            ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
              d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c9.4-9.4 24.6-9.4 33.9 0l47 47 47-47c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-47 47 47 47c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-47-47-47 47c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l47-47-47-47c-9.4-9.4-9.4-24.6 0-33.9z"
            /></svg
          >
        </div>
      </div>
      <div
        id="mainOptionBox"
        class="px-2 pt-2 bg-gray-100 shadow-inner rounded-xl h-full w-full"
      ></div>
    </div>
  </div>
</div>

<!-- Wrap notification wrong answer -->
<div
  id="wrapAnswerWrongBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="text-md font-bold mb-3">Your answer is wrong</div>
    <div class="flex flex-row items-center justify-center text-sm text-center mb-3">
      <div class="mr-1">
        <svg
          class="w-5 h-5 fill-amber-900"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 512 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M47.6 300.4L228.3 469.1c7.5 7 17.4 10.9 27.7 10.9s20.2-3.9 27.7-10.9L464.4 300.4c30.4-28.3 47.6-68 47.6-109.5v-5.8c0-69.9-50.5-129.5-119.4-141C347 36.5 300.6 51.4 268 84L256 96 244 84c-32.6-32.6-79-47.5-124.6-39.9C50.5 55.6 0 115.2 0 185.1v5.8c0 41.5 17.2 81.2 47.6 109.5z"
          /></svg
        >
      </div>
      <div class="text-lg font-semibold">-1</div>
    </div>
    <div
      id="okAnswerWrongBtn"
      class="px-5 py-1.5 rounded-xl bg-amber-400 cursor-pointer hover:bg-amber-500 font-semibold"
    >
      Ok
    </div>
  </div>
</div>

<!-- Wrap notification wrong answer -->
<div
  id="wrapAnswerCorrectBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="text-md font-bold mb-3">Your answer is correct</div>
    <div class="flex flex-row items-center justify-center text-sm text-center mb-3">
      <div class="mr-1">
        <svg
          class="w-5 h-5 fill-amber-900"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 576 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z"
          /></svg
        >
      </div>
      <div class="text-lg font-semibold">+1</div>
    </div>
    <div
      id="okAnswerCorrectBtn"
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
