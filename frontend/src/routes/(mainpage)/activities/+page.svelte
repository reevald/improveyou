<script>
  import { getWithAuth } from '$lib/api';
  import { onMount } from 'svelte';

  const resizeWrap = (wrapElem) => {
    wrapElem.style.height = `${screen.height}px`;
    if (screen.width <= 480) {
      wrapElem.style.width = `${screen.width}px`;
    } else {
      wrapElem.style.width = '480px';
    }
  };

  onMount(() => {
    const wrapActElem = document.getElementById('wrapActivitiesBox');
    resizeWrap(wrapActElem);
    window.addEventListener('resize', () => {
      resizeWrap(wrapActElem);
    });
    let idRecom = [];
    let htmlActExe = '';
    let htmlActMed = '';
    let htmlActRead = '';
    const renderActivities = (data) => {
      data?.recommendations.forEach((act) => {
        idRecom.push(act.id);
      });

      data?.activities.forEach((act) => {
        const htmlAct = `
        <a href="/activity/${act?.category}/${act?.slug}" class="cursor-pointer group">
          <div
            class="bg-gray-500 border-b-4 border-gray-300 shrink-0 w-48 h-48 m mr-3 rounded-xl relative overflow-hidden pointer-events-none"
          >
            <div class="w-full h-full flex flex-row justify-center items-center">
              <svg
                class="w-16 h-16 fill-gray-200 animate-pulse"
                xmlns="http://www.w3.org/2000/svg"
                height="1em"
                viewBox="0 0 512 512"
                ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                  d="M0 96C0 60.7 28.7 32 64 32H448c35.3 0 64 28.7 64 64V416c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V96zM323.8 202.5c-4.5-6.6-11.9-10.5-19.8-10.5s-15.4 3.9-19.8 10.5l-87 127.6L170.7 297c-4.6-5.7-11.5-9-18.7-9s-14.2 3.3-18.7 9l-64 80c-5.8 7.2-6.9 17.1-2.9 25.4s12.4 13.6 21.6 13.6h96 32H424c8.9 0 17.1-4.9 21.2-12.8s3.6-17.4-1.4-24.7l-120-176zM112 192a48 48 0 1 0 0-96 48 48 0 1 0 0 96z"
                /></svg
              >
            </div>
            <div class="absolute top-0 left-0 z-10">
              <img
                class="w-48 h-48 group-hover:scale-110 transition-all ease-in duration-300"
                src="${act?.thumbnail_path}"
                alt="Exercise"
              />
            </div>
            <div
              class="absolute z-20 top-0 left-0 w-full h-full flex flex-col justify-end"
            >
              <div
                class="font-oswald text-xl px-3 pb-2 pt-4 bg-gradient-to-t from-gray-900 to-gray-900/0 text-white"
              >
                ${act?.name}
              </div>
            </div>
            ${
              idRecom.includes(act?.id)
                ? `<div
              class="absolute z-20 top-2.5 -left-10 w-32 text-center bg-amber-500 px-2 py-1.5 text-xs font-semibold text-white -rotate-45"
            >
              For You
            </div>`
                : ''
            }
          </div>
        </a>
        `;
        if (idRecom.includes(act?.id)) {
          htmlActExe = act?.category == 'exercise' ? htmlAct + htmlActExe : htmlActExe;
          htmlActMed =
            act?.category == 'meditation' ? htmlAct + htmlActMed : htmlActMed;
          htmlActRead =
            act?.category == 'reading' ? htmlAct + htmlActRead : htmlActRead;
        } else {
          htmlActExe = act?.category == 'exercise' ? htmlActExe + htmlAct : htmlActExe;
          htmlActMed =
            act?.category == 'meditation' ? htmlActMed + htmlAct : htmlActMed;
          htmlActRead =
            act?.category == 'reading' ? htmlActRead + htmlAct : htmlActRead;
        }
      });
      const actExeElem = document.getElementById('actExeBox');
      const actMedElem = document.getElementById('actMedBox');
      const actReadElem = document.getElementById('actReadBox');
      actExeElem.innerHTML = htmlActExe;
      actMedElem.innerHTML = htmlActMed;
      actReadElem.innerHTML = htmlActRead;
    };
    getWithAuth('activities/recommendations', renderActivities);
  });
</script>

<div
  id="wrapActivitiesBox"
  class="max-h-screen w-[480] pb-16 bg-gray-100 text-gray-600"
>
  <div class="h-full overflow-y-auto w-full px-1.5 xxs:px-2.5 xs:px-4 py-6">
    <div class="mb-2 text-2xl font-oswald font-semibold">Activities</div>
    <div class="text-sm mb-4">
      Engaging in exercise, meditation, and reading can help prevent excessive
      masturbation by redirecting energy, enhancing self-control, and providing
      constructive distractions from urges.
    </div>
    <div class="text-lg font-oswald mb-2 font-semibold">Exercises</div>
    <div id="actExeBox" class="flex flex-row w-full overflow-x-auto pb-2 mb-4"></div>
    <div class="text-lg font-oswald mb-2 font-semibold">Meditations</div>
    <div id="actMedBox" class="flex flex-row w-full overflow-x-auto pb-2 mb-4"></div>
    <div class="text-lg font-oswald mb-2 font-semibold">Reading</div>
    <div id="actReadBox" class="flex flex-row w-full overflow-x-auto pb-2 mb-4"></div>
  </div>
</div>
