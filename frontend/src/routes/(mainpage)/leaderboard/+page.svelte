<script>
  import { getWithAuth } from '$lib/api';
  import { onMount } from 'svelte';

  const loadImage = (url) => {
    return new Promise((resolve) => {
      const image = new Image();
      image.addEventListener('load', () => {
        resolve(image);
      });
      image.src = url;
    });
  };

  onMount(() => {
    const resizeWrap = () => {
      const wrapActElem = document.getElementById('wrapActivitiesBox');
      wrapActElem.style.height = `${screen.height}px`;
      if (screen.width <= 480) {
        wrapActElem.style.width = `${screen.width}px`;
      } else {
        wrapActElem.style.width = '480px';
      }
    };
    resizeWrap();
    window.addEventListener('resize', () => {
      resizeWrap();
    });

    // These are default of objets
    const dataCharacter = {
      head: {
        universal: './sprite-default/character/head/rabit/light/universal/light.png'
      },
      body: {
        universal: './sprite-default/character/body/teen/light/universal/light.png'
      }
    };
    const dataHat = {
      universal: './sprite-default/hat/head_band_tied/universal/orange.png'
    };

    const dataShirt = {
      up: {
        universal: './sprite-default/shirt/up/clothes/longsleeve/universal/orange.png'
      },
      bottom: {
        universal: './sprite-default/shirt/bottom/pants/universal/black.png'
      }
    };

    const dataShoes = {
      universal: './sprite-default/shoes/sandals/universal/brown.png'
    };

    const wrapLeaderboardExeElem = document.getElementById('wrapLeaderboardExeBox');
    const wrapLeaderboardMedElem = document.getElementById('wrapLeaderboardMedBox');
    const wrapLeaderboardReadElem = document.getElementById('wrapLeaderboardReadBox');
    const menuLeaderboardExeElem = document.getElementById('menuLeaderboardExeBox');
    const menuLeaderboardMedElem = document.getElementById('menuLeaderboardMedBox');
    const menuLeaderboardReadElem = document.getElementById('menuLeaderboardReadBox');

    menuLeaderboardExeElem.addEventListener('click', () => {
      wrapLeaderboardExeElem.classList.add('flex');
      wrapLeaderboardExeElem.classList.remove('hidden');
      wrapLeaderboardMedElem.classList.add('hidden');
      wrapLeaderboardMedElem.classList.remove('flex');
      wrapLeaderboardReadElem.classList.add('hidden');
      wrapLeaderboardReadElem.classList.remove('flex');

      menuLeaderboardExeElem.classList.add('bg-amber-500');
      menuLeaderboardExeElem.classList.remove('bg-amber-400');
      menuLeaderboardMedElem.classList.add('bg-amber-400');
      menuLeaderboardMedElem.classList.remove('bg-amber-500');
      menuLeaderboardReadElem.classList.add('bg-amber-400');
      menuLeaderboardReadElem.classList.remove('bg-amber-500');
    });

    menuLeaderboardMedElem.addEventListener('click', () => {
      wrapLeaderboardMedElem.classList.add('flex');
      wrapLeaderboardMedElem.classList.remove('hidden');
      wrapLeaderboardExeElem.classList.add('hidden');
      wrapLeaderboardExeElem.classList.remove('flex');
      wrapLeaderboardReadElem.classList.add('hidden');
      wrapLeaderboardReadElem.classList.remove('flex');

      menuLeaderboardMedElem.classList.add('bg-amber-500');
      menuLeaderboardMedElem.classList.remove('bg-amber-400');
      menuLeaderboardExeElem.classList.add('bg-amber-400');
      menuLeaderboardExeElem.classList.remove('bg-amber-500');
      menuLeaderboardReadElem.classList.add('bg-amber-400');
      menuLeaderboardReadElem.classList.remove('bg-amber-500');
    });

    menuLeaderboardReadElem.addEventListener('click', () => {
      wrapLeaderboardReadElem.classList.add('flex');
      wrapLeaderboardReadElem.classList.remove('hidden');
      wrapLeaderboardExeElem.classList.add('hidden');
      wrapLeaderboardExeElem.classList.remove('flex');
      wrapLeaderboardMedElem.classList.add('hidden');
      wrapLeaderboardMedElem.classList.remove('flex');

      menuLeaderboardReadElem.classList.add('bg-amber-500');
      menuLeaderboardReadElem.classList.remove('bg-amber-400');
      menuLeaderboardMedElem.classList.add('bg-amber-400');
      menuLeaderboardMedElem.classList.remove('bg-amber-500');
      menuLeaderboardExeElem.classList.add('bg-amber-400');
      menuLeaderboardExeElem.classList.remove('bg-amber-500');
    });

    const leaderboardHandler = (data) => {
      const dictObj = {};
      data?.leaderboard_object.forEach((dataObj) => {
        dictObj[dataObj?.id] = {
          objHatSprite: dataObj?.obj_hat_sprite,
          objClotSprite: dataObj?.obj_clothes_sprite,
          objShoesSprite: dataObj?.obj_shoes_sprite
        };
      });

      let htmlLeaderboardExe = '';
      let htmlLeaderboardMed = '';
      let htmlLeaderboardRead = '';

      const formatEmojiSkor = (dataUser) => {
        if (dataUser?.category == 'exercise') {
          return `💪 ${dataUser?.poin_muscle}`;
        } else if (dataUser?.category == 'meditation') {
          return `🧘 ${dataUser?.poin_heart}`;
        } else if (dataUser?.category == 'reading') {
          return `🧠 ${dataUser?.poin_brain}`;
        }
      };

      let currRankExe = 1;
      let currRankMed = 1;
      let currRankRead = 1;

      data?.leaderboard_data.forEach((dataUser) => {
        let userRank = 0;
        if (dataUser?.category == 'exercise') {
          userRank = currRankExe;
        } else if (dataUser?.category == 'meditation') {
          userRank = currRankMed;
        } else if (dataUser?.category == 'reading') {
          userRank = currRankRead;
        }

        const htmlUser = `
          <div
            class="bg-white rounded-full shadow-md flex flex-row w-full py-1 px-5 items-center font-semibold text-gray-700 mb-3"
          >
            <div class="w-8 flex flex-row justify-center items-center font-bold">
              ${
                userRank <= 3
                  ? `<img class="mr-3 mt-1" src="/icon/pin${userRank}.svg" alt="pin"/>`
                  : `<span class="mr-3 mt-1">${userRank}</span>`
              }
            </div>
            <div>
              <canvas
                data-${dataUser?.category}-id="${dataUser?.id}"
                class="my-1.5 w-10 h-10 bg-gray-100 rounded-full mr-3 ring-4 ring-gray-200"
              ></canvas>
            </div>
            <div class="flex-1">${dataUser?.username}</div>
            <div>${formatEmojiSkor(dataUser)}</div>
          </div>
        `;

        if (dataUser?.category == 'exercise') {
          currRankExe += 1;
          htmlLeaderboardExe += htmlUser;
        } else if (dataUser?.category == 'meditation') {
          currRankMed += 1;
          htmlLeaderboardMed += htmlUser;
        } else if (dataUser?.category == 'reading') {
          currRankRead += 1;
          htmlLeaderboardRead += htmlUser;
        }
      });

      wrapLeaderboardExeElem.innerHTML = htmlLeaderboardExe;
      wrapLeaderboardMedElem.innerHTML = htmlLeaderboardMed;
      wrapLeaderboardReadElem.innerHTML = htmlLeaderboardRead;
      data?.leaderboard_data.forEach((dataUser) => {
        const cnv = document.querySelector(
          `canvas[data-${dataUser?.category}-id="${dataUser?.id}"]`
        );
        const ctx = cnv.getContext('2d');
        loadImage(dataCharacter.body.universal).then((img) => {
          ctx.drawImage(img, 1 * 64, 10 * 64, 64, 64, 0, 0, cnv.width, cnv.height);
        });
        loadImage(dictObj[dataUser?.id].objClotSprite || dataShirt.up.universal).then(
          (img) => {
            ctx.drawImage(img, 1 * 64, 10 * 64, 64, 64, 0, 0, cnv.width, cnv.height);
          }
        );
        loadImage(dataShirt.bottom.universal).then((img) => {
          ctx.drawImage(img, 1 * 64, 10 * 64, 64, 64, 0, 0, cnv.width, cnv.height);
        });
        loadImage(dictObj[dataUser?.id].objShoesSprite || dataShoes.universal).then(
          (img) => {
            ctx.drawImage(img, 1 * 64, 10 * 64, 64, 64, 0, 0, cnv.width, cnv.height);
          }
        );
        loadImage(dataCharacter.head.universal).then((img) => {
          ctx.drawImage(img, 1 * 64, 10 * 64, 64, 64, 0, 0, cnv.width, cnv.height);
        });
        loadImage(dictObj[dataUser?.id].objHatSprite || dataHat.universal).then(
          (img) => {
            ctx.drawImage(img, 1 * 64, 10 * 64, 64, 64, 0, 0, cnv.width, cnv.height);
          }
        );
      });
    };
    getWithAuth('user/leaderboard', leaderboardHandler);
  });
</script>

<div
  id="wrapActivitiesBox"
  class="max-h-screen w-[480] pb-16 bg-gray-100 text-gray-600"
>
  <div class="h-full overflow-y-auto w-full py-6 flex flex-col">
    <div
      class="mb-6 px-1.5 xxs:px-2.5 xs:px-4 text-2xl font-oswald font-semibold flex flex-row justify-between"
    >
      <div>Leaderboard</div>
      <div class="p-1 bg-gray-300 rounded-full cursor-not-allowed">
        <svg
          class="fill-gray-600 w-6 h-6"
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 320 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M80 160c0-35.3 28.7-64 64-64h32c35.3 0 64 28.7 64 64v3.6c0 21.8-11.1 42.1-29.4 53.8l-42.2 27.1c-25.2 16.2-40.4 44.1-40.4 74V320c0 17.7 14.3 32 32 32s32-14.3 32-32v-1.4c0-8.2 4.2-15.8 11-20.2l42.2-27.1c36.6-23.6 58.8-64.1 58.8-107.7V160c0-70.7-57.3-128-128-128H144C73.3 32 16 89.3 16 160c0 17.7 14.3 32 32 32s32-14.3 32-32zm80 320a40 40 0 1 0 0-80 40 40 0 1 0 0 80z"
          /></svg
        >
      </div>
    </div>
    <div
      class="w-full px-1.5 xxs:px-2.5 xs:px-4 flex flex-row justify-center text-amber-900 font-semibold"
    >
      <div
        id="menuLeaderboardExeBox"
        class="bg-amber-500 px-4 py-1.5 rounded-t-xl cursor-pointer"
      >
        Exercise
      </div>
      <div
        id="menuLeaderboardMedBox"
        class="bg-amber-400 px-4 py-1.5 rounded-t-xl cursor-pointer"
      >
        Meditation
      </div>
      <div
        id="menuLeaderboardReadBox"
        class="bg-amber-400 px-4 py-1.5 rounded-t-xl cursor-pointer"
      >
        Reading
      </div>
    </div>

    <div
      id="wrapLeaderboardExeBox"
      class="flex-1 flex flex-col px-1.5 xxs:px-2.5 xs:px-4 py-6 w-full bg-gradient-to-b from-amber-500 to-gray-100 rounded-t-2xl"
    ></div>
    <div
      id="wrapLeaderboardMedBox"
      class="hidden flex-col flex-1 px-1.5 xxs:px-2.5 xs:px-4 py-6 w-full bg-gradient-to-b from-amber-500 to-gray-100 rounded-t-2xl"
    ></div>
    <div
      id="wrapLeaderboardReadBox"
      class="hidden flex-col flex-1 px-1.5 xxs:px-2.5 xs:px-4 py-6 w-full bg-gradient-to-b from-amber-500 to-gray-100 rounded-t-2xl"
    ></div>
  </div>
</div>
