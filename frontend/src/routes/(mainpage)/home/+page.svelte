<script>
  import { getWithAuth, postWithAuth, putWithAuth } from '$lib/api';
  import { onMount } from 'svelte';

  // console.log('[page home] Its run server?');

  const resizeScreenHander = (skyElem, canvasElem, groundElem, wrapElem) => {
    const stdHeightMenu = 64; // in pixel
    const stdHeightAll = 740; // based on modern phone (samsung S8+/S8+) [most suitable]
    const stdHeightBG = 530;
    const stdWidthAll = 480;

    let skyElemHeight = 0;
    let groundElemHeight = 0;
    let wrapElemMarginTop = 0;

    if (window.innerHeight < stdHeightBG + stdHeightMenu) {
      groundElemHeight = stdHeightMenu;
      wrapElemMarginTop = -(stdHeightMenu + stdHeightBG - window.innerHeight);
    } else if (
      window.innerHeight >= stdHeightBG + stdHeightMenu &&
      window.innerHeight < stdHeightAll
    ) {
      groundElemHeight = window.innerHeight - stdHeightBG;
    } else if (window.innerHeight >= stdHeightAll) {
      const equalPart = (window.innerHeight - stdHeightAll) / 2;
      skyElemHeight = equalPart;
      groundElemHeight = stdHeightAll - stdHeightBG + equalPart;
    }

    if (window.innerWidth < stdWidthAll) {
      // By congruence theory: https://mathworld.wolfram.com/GeometricCongruence.html
      // New canvas ≅ old canvas
      // [length cnv new / length cnv old = width cnv new / width cnv old]
      // Note: even new canvas has same width and height attribute with old canvas,
      // Actual size new canvas is changing by css class w-full
      const newHeightCnv = (window.innerWidth * stdHeightBG) / stdWidthAll;
      // Old rest is equal with stdHeightAll - stdHeightBG
      // By using congruence, new rest ≅ old canvas (with same analogy above)
      const newHeightRest = ((stdHeightAll - stdHeightBG) * newHeightCnv) / stdHeightBG;
      const equalPart = (window.innerHeight - (newHeightCnv + newHeightRest)) / 2;
      skyElemHeight = equalPart;
      groundElemHeight = newHeightRest + equalPart;
      wrapElemMarginTop = 0;
      if (window.innerHeight < newHeightCnv + newHeightRest) {
        skyElemHeight = 0;
        groundElemHeight = window.innerHeight - newHeightCnv;
      }
      if (window.innerHeight < newHeightCnv + stdHeightMenu) {
        skyElemHeight = 0;
        groundElemHeight = stdHeightMenu;
        wrapElemMarginTop = -(stdHeightMenu + newHeightCnv - window.innerHeight);
      }
    }

    canvasElem.height = stdHeightBG;
    canvasElem.width = stdWidthAll;

    wrapElem.style.marginTop = `${wrapElemMarginTop}px`;
    skyElem.style.height = `${skyElemHeight}px`;
    groundElem.style.height = `${groundElemHeight}px`;
  };

  // ========================= [Begin] Canvas handler =========================
  let canvasElem = null;
  let ctx = null;
  let listObjId;
  const loadImg = (path) => {
    // Non-gif image
    const img = new Image();
    img.onerror = (e) => {
      console.error(e);
    };
    img.src = path;
    return img;
  };

  class ParallaxBG {
    constructor(listDataLayer) {
      // Schema of listDataLayer
      // [
      //   {
      //     pathImg: './path.jpg',
      //     distFromTop: 240,
      //     speedFrame: 4
      //   }
      // ];
      this.listDataLayer = listDataLayer.map((dataLayer) => {
        return {
          img: loadImg(dataLayer.pathImg),
          distFromTop: dataLayer.distFromTop,
          speedFrame: dataLayer.speedFrame,
          posX1: 0,
          posX2: canvasElem.width
        };
      });
    }

    updatePosition(fps) {
      const dist = (speed) => (fps > 0 ? (60 / fps) * speed : 0);
      this.listDataLayer.forEach((data) => {
        if (data.speedFrame != 0) {
          // Reference: https://www.youtube.com/watch?v=4wz1zrbTAo0
          data.posX1 =
            data.posX1 < -canvasElem.width
              ? canvasElem.width - dist(data.speedFrame) + data.posX2
              : data.posX1 - dist(data.speedFrame);

          data.posX2 =
            data.posX2 < -canvasElem.width
              ? canvasElem.width - dist(data.speedFrame) + data.posX1
              : data.posX2 - dist(data.speedFrame);
        }
      });
    }

    draw() {
      this.listDataLayer.forEach((data) => {
        if (data.img.complete) {
          ctx.drawImage(
            data.img,
            data.posX1,
            data.distFromTop,
            canvasElem.width,
            data.img.height
          );
          if (data.speedFrame != 0) {
            ctx.drawImage(
              data.img,
              data.posX2,
              data.distFromTop,
              canvasElem.width,
              data.img.height
            );
          }
        }
      });
    }
  }

  class SpriteObj {
    // Size box per image in sprite: 64x64 (px)
    constructor(dataCharacter, dataHat, dataShirt, dataShoes) {
      // Schema of data character
      // {
      //   head: {
      //     universal: "./sprite.png",
      //   },
      //   body: {
      //     universal: "./sprite.png",
      //   }
      // }

      this.dataCharacter = {
        head: {
          universal: loadImg(dataCharacter.head.universal)
        },
        body: {
          universal: loadImg(dataCharacter.body.universal)
        }
      };

      // Schema of data hat
      // {
      //   universal: "./sprite.png",
      // }
      this.dataHat = {
        universal: loadImg(dataHat.universal)
      };

      // Schema of data shirt
      // {
      //   up: {
      //     universal: "./sprite.png",
      //   },
      //   bottom {
      //     universal: "./sprite.png",
      //   },
      // },
      this.dataShirt = {
        up: {
          universal: loadImg(dataShirt.up.universal)
        },
        bottom: {
          universal: loadImg(dataShirt.bottom.universal)
        }
      };

      // Schema of data shoes
      // {
      //   universal: "./sprite.png",
      // },
      this.dataShoes = {
        universal: loadImg(dataShoes.universal)
      };

      this.frameRate = 10; // Change img each 15 frame

      this.walkFrame = 0;
      this.walkData = {
        currIdxStage: 1, // Max idx = 8
        numStage: 9,
        spriteIdxPos: 11, // Since start from 0
        originSize: 64, // Square (pixel)
        displaySize: 120,
        stdDistFromTop: 375,
        external: {
          shadow: loadImg('./sprite-default/shadow/walk/shadow.png')
        }
      };
    }

    drawPartOfWalk(img) {
      if (img.complete) {
        ctx.drawImage(
          img,
          this.walkData.currIdxStage * this.walkData.originSize,
          this.walkData.spriteIdxPos * this.walkData.originSize,
          this.walkData.originSize,
          this.walkData.originSize,
          (canvasElem.width - this.walkData.displaySize) / 2,
          this.walkData.stdDistFromTop,
          this.walkData.displaySize,
          this.walkData.displaySize
        );
      }
    }

    animateWalk(fps) {
      if (this.walkData.external.shadow.complete) {
        ctx.drawImage(
          this.walkData.external.shadow,
          0,
          0,
          this.walkData.originSize,
          this.walkData.originSize,
          (canvasElem.width - this.walkData.displaySize) / 2,
          this.walkData.stdDistFromTop + 8,
          this.walkData.displaySize,
          this.walkData.displaySize
        );
      }
      this.drawPartOfWalk(this.dataCharacter.body.universal);
      this.drawPartOfWalk(this.dataShirt.up.universal);
      this.drawPartOfWalk(this.dataShirt.bottom.universal);
      this.drawPartOfWalk(this.dataShoes.universal);
      this.drawPartOfWalk(this.dataCharacter.head.universal);
      this.drawPartOfWalk(this.dataHat.universal);
      if (this.walkFrame == 0) {
        this.walkData.currIdxStage += 1;
        if (this.walkData.currIdxStage == this.walkData.numStage - 1) {
          this.walkData.currIdxStage = 1;
        }
      }

      this.walkFrame += 1;
      if (this.walkFrame >= Math.round((fps / 60) * this.frameRate)) {
        this.walkFrame = 0;
      }
    }
  }

  // ========================= [End] Canvas handler =========================
  onMount(() => {
    const skyElem = document.getElementById('skyBox');
    const groundElem = document.getElementById('groundBox');
    const wrapElem = document.getElementById('wrapBox');
    const toggleTaskBtn = document.getElementById('toggleTaskBtn');
    const wrapTaskElem = document.getElementById('wrapTaskBox');
    const fpsElem = document.getElementById('fpsBox');
    const wrapDailyCheckElem = document.getElementById('wrapDailyCheckBox');
    const closeDailyCheckBtnElem = document.getElementById('closeDailyCheckBtn');
    const negAnsBtnElem = document.getElementById('negAnsBtn');
    const posAnsBtnElem = document.getElementById('posAnsBtn');
    const mainDailyCheckElem = document.getElementById('mainDailyCheckBox');
    const warnDailyCheckElem = document.getElementById('warnDailyCheckBox');
    const dailyCheckBtnElem = document.getElementById('dailyCheckBtn');
    const pingDailyCheckBox = document.getElementById('pingDailyCheckBox');
    const shopBtnElem = document.getElementById('shopBtn');
    const bagBtnElem = document.getElementById('bagBtn');
    const closeWrapShopBtnElem = document.getElementById('closeWrapShopBtn');
    const shopGoldElem = document.getElementById('shopGoldBox');
    const wrapShopElem = document.getElementById('wrapShopBox');
    const shopMenuHatElem = document.getElementById('shopMenuHatBox');
    const shopMenuClothesElem = document.getElementById('shopMenuClothesBox');
    const shopMenuShoesElem = document.getElementById('shopMenuShoesBox');
    const itemShopHatElem = document.getElementById('itemShopHatBox');
    const itemShopClothesElem = document.getElementById('itemShopClothesBox');
    const itemShopShoesElem = document.getElementById('itemShopShoesBox');
    const wrapConfirmBuyElem = document.getElementById('wrapConfirmBuyBox');
    const confirmBuyBtnElem = document.getElementById('confirmBuyBtn');
    const cancelBuyBtnElem = document.getElementById('cancelBuyBtn');
    const wrapNotifNotEnoughGoldElem = document.getElementById(
      'wrapNotifNotEnoughGoldBox'
    );
    const wrapNotifSuccessBuyElem = document.getElementById('wrapNotifSuccessBuyBox');
    const okNotifNotEnoughBtnElem = document.getElementById('okNotifNotEnoughBtn');
    const okNotifSuccessBtnElem = document.getElementById('okNotifSuccessBtn');
    const wrapErrorElem = document.getElementById('wrapErrorBox');
    const okErrorBtnElem = document.getElementById('okErrorBtn');
    const wrapLoaderElem = document.getElementById('wrapLoaderBox');
    const confirmNameElem = document.getElementById('confirmNameBox');
    const confirmPercentValueElem = document.getElementById('confirmPercentValueBox');
    const confirmPriceElem = document.getElementById('confirmPriceBox');
    const confirmThumbnailElem = document.getElementById('confirmThumbnailBox');
    const bagMenuHatElem = document.getElementById('bagMenuHatBox');
    const bagMenuClothesElem = document.getElementById('bagMenuClothesBox');
    const bagMenuShoesElem = document.getElementById('bagMenuShoesBox');
    const itemBagHatElem = document.getElementById('itemBagHatBox');
    const itemBagClothesElem = document.getElementById('itemBagClothesBox');
    const itemBagShoesElem = document.getElementById('itemBagShoesBox');
    const wrapBagElem = document.getElementById('wrapBagBox');
    const closeBagBtnElem = document.getElementById('closeBagBtn');
    const triggerShopFromBagBtnElem = document.getElementById('triggerShopFromBagBtn');
    const wrapNotifSuccessDCElem = document.getElementById('wrapNotifSuccessDCBox');
    const okNotifSuccessDCBtnElem = document.getElementById('okNotifSuccessDCBtn');
    const dateTargetDCElem = document.getElementById('dateTargetDCBox');

    const targetDate = new Date();
    targetDate.setDate(targetDate.getDate() - 1);
    const nameMonths = [
      'Jan',
      'Feb',
      'Mar',
      'Apr',
      'May',
      'Jun',
      'Jul',
      'Aug',
      'Sep',
      'Oct',
      'Nov',
      'Dec'
    ];
    dateTargetDCElem.innerText = `(${targetDate.getUTCDate()} ${
      nameMonths[targetDate.getUTCMonth()]
    } ${targetDate.getUTCFullYear()})`;

    okNotifSuccessDCBtnElem.addEventListener('click', () => {
      wrapNotifSuccessDCElem.classList.remove('flex');
      wrapNotifSuccessDCElem.classList.add('hidden');
      wrapDailyCheckElem.classList.remove('flex');
      wrapDailyCheckElem.classList.add('hidden');
    });

    closeBagBtnElem.addEventListener('click', () => {
      wrapBagElem.classList.remove('flex');
      wrapBagElem.classList.add('hidden');
    });

    triggerShopFromBagBtnElem.addEventListener('click', () => {
      wrapBagElem.classList.remove('flex');
      wrapBagElem.classList.add('hidden');
      wrapShopElem.classList.add('flex');
      wrapShopElem.classList.remove('hidden');
    });

    bagBtnElem.addEventListener('click', () => {
      wrapBagElem.classList.add('flex');
      wrapBagElem.classList.remove('hidden');
    });

    okErrorBtnElem.addEventListener('click', () => {
      wrapErrorElem.classList.remove('flex');
      wrapErrorElem.classList.add('hidden');
    });

    okNotifSuccessBtnElem.addEventListener('click', () => {
      wrapNotifSuccessBuyElem.classList.remove('flex');
      wrapNotifSuccessBuyElem.classList.add('hidden');
    });

    okNotifNotEnoughBtnElem.addEventListener('click', () => {
      wrapNotifNotEnoughGoldElem.classList.remove('flex');
      wrapNotifNotEnoughGoldElem.classList.add('hidden');
    });

    cancelBuyBtnElem.addEventListener('click', () => {
      wrapConfirmBuyElem.classList.remove('flex');
      wrapConfirmBuyElem.classList.add('hidden');
    });

    bagMenuHatElem.addEventListener('click', (event) => {
      itemBagHatElem.classList.add('flex');
      itemBagHatElem.classList.remove('hidden');
      itemBagClothesElem.classList.remove('flex');
      itemBagClothesElem.classList.add('hidden');
      itemBagShoesElem.classList.remove('flex');
      itemBagShoesElem.classList.add('hidden');

      event.target.classList.add('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      bagMenuClothesElem.classList.remove(
        'rounded-t-xl',
        'shadow-inner',
        'bg-gray-100'
      );
      bagMenuShoesElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
    });

    bagMenuClothesElem.addEventListener('click', (event) => {
      itemBagClothesElem.classList.add('flex');
      itemBagClothesElem.classList.remove('hidden');
      itemBagHatElem.classList.remove('flex');
      itemBagHatElem.classList.add('hidden');
      itemBagShoesElem.classList.remove('flex');
      itemBagShoesElem.classList.add('hidden');

      event.target.classList.add('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      bagMenuHatElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      bagMenuShoesElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
    });

    bagMenuShoesElem.addEventListener('click', (event) => {
      itemBagShoesElem.classList.add('flex');
      itemBagShoesElem.classList.remove('hidden');
      itemBagHatElem.classList.remove('flex');
      itemBagHatElem.classList.add('hidden');
      itemBagClothesElem.classList.remove('flex');
      itemBagClothesElem.classList.add('hidden');

      event.target.classList.add('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      bagMenuClothesElem.classList.remove(
        'rounded-t-xl',
        'shadow-inner',
        'bg-gray-100'
      );
      bagMenuHatElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
    });

    shopMenuHatElem.addEventListener('click', (event) => {
      itemShopHatElem.classList.add('flex');
      itemShopHatElem.classList.remove('hidden');
      itemShopClothesElem.classList.remove('flex');
      itemShopClothesElem.classList.add('hidden');
      itemShopShoesElem.classList.remove('flex');
      itemShopShoesElem.classList.add('hidden');

      event.target.classList.add('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      shopMenuClothesElem.classList.remove(
        'rounded-t-xl',
        'shadow-inner',
        'bg-gray-100'
      );
      shopMenuShoesElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
    });

    shopMenuClothesElem.addEventListener('click', (event) => {
      itemShopClothesElem.classList.add('flex');
      itemShopClothesElem.classList.remove('hidden');
      itemShopHatElem.classList.remove('flex');
      itemShopHatElem.classList.add('hidden');
      itemShopShoesElem.classList.remove('flex');
      itemShopShoesElem.classList.add('hidden');

      event.target.classList.add('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      shopMenuHatElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      shopMenuShoesElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
    });

    shopMenuShoesElem.addEventListener('click', (event) => {
      itemShopShoesElem.classList.add('flex');
      itemShopShoesElem.classList.remove('hidden');
      itemShopHatElem.classList.remove('flex');
      itemShopHatElem.classList.add('hidden');
      itemShopClothesElem.classList.remove('flex');
      itemShopClothesElem.classList.add('hidden');

      event.target.classList.add('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
      shopMenuClothesElem.classList.remove(
        'rounded-t-xl',
        'shadow-inner',
        'bg-gray-100'
      );
      shopMenuHatElem.classList.remove('rounded-t-xl', 'shadow-inner', 'bg-gray-100');
    });

    shopBtnElem.addEventListener('click', () => {
      wrapShopElem.classList.add('flex');
      wrapShopElem.classList.remove('hidden');
    });

    closeWrapShopBtnElem.addEventListener('click', () => {
      wrapShopElem.classList.remove('flex');
      wrapShopElem.classList.add('hidden');
    });

    dailyCheckBtnElem.addEventListener('click', () => {
      wrapDailyCheckElem.classList.add('flex');
      wrapDailyCheckElem.classList.remove('hidden');
    });

    closeDailyCheckBtnElem.addEventListener('click', () => {
      wrapDailyCheckElem.classList.remove('flex');
      wrapDailyCheckElem.classList.add('hidden');
    });

    const successDailyCheck = (data) => {};

    const dailyCheckResolver = async (streak_status) => {
      const objDailyCheck = {
        qna: [],
        streak_status: streak_status
      };
      wrapLoaderElem.classList.remove('hidden');
      wrapLoaderElem.classList.add('flex');
      const respStatus = await postWithAuth(
        'user/me/dailycheck',
        objDailyCheck,
        false,
        successDailyCheck
      );
      wrapLoaderElem.classList.add('hidden');
      wrapLoaderElem.classList.remove('flex');

      if (respStatus != 200) {
        mainDailyCheckElem.classList.remove('flex');
        mainDailyCheckElem.classList.add('hidden');
        warnDailyCheckElem.classList.add('flex');
        warnDailyCheckElem.classList.remove('hidden');
      } else {
        wrapNotifSuccessDCElem.classList.add('flex');
        wrapNotifSuccessDCElem.classList.remove('hidden');
      }
      pingDailyCheckBox.classList.remove('flex');
      pingDailyCheckBox.classList.add('hidden');
    };

    negAnsBtnElem.addEventListener('click', async () => {
      await dailyCheckResolver('continue');
    });

    posAnsBtnElem.addEventListener('click', async () => {
      await dailyCheckResolver('discontinue');
    });

    canvasElem = document.getElementById('canvasBox');

    resizeScreenHander(skyElem, canvasElem, groundElem, wrapElem);
    window.addEventListener('resize', () => {
      resizeScreenHander(skyElem, canvasElem, groundElem, wrapElem);
    });

    toggleTaskBtn.addEventListener('click', (event) => {
      if (event.target.getAttribute('data-toggle') == 'active') {
        wrapTaskElem.style.height = '96px'; // h-16 (menu) + h-8 (toggler) [h-1 = 4px]
        event.target.setAttribute('data-toggle', 'deactive');
        event.target.children[0].classList.remove('hidden');
        event.target.children[1].classList.add('hidden');
      } else if (event.target.getAttribute('data-toggle') == 'deactive') {
        wrapTaskElem.style.height = 'auto';
        event.target.setAttribute('data-toggle', 'active');
        event.target.children[0].classList.add('hidden');
        event.target.children[1].classList.remove('hidden');
      }
    });

    // [GET] handler, mostly to render data
    const gameStatHandler = (data) => {
      const oneDay = 24 * 60 * 60 * 1000;
      const currDate = new Date();
      const targetDate = new Date(Date.UTC(2023, currDate.getMonth() + 1, 1, 0, 0, 0));
      const diffDays = Math.round(Math.abs((targetDate - currDate) / oneDay));
      document.getElementById('usernameBox').innerText = data?.username;
      document.getElementById('daysBox').innerText = `${diffDays} days left`;
      document.getElementById('goldBox').innerText = data?.gold;
      document.getElementById('poinMuscleBox').innerText = data?.poin_muscle;
      document.getElementById('poinHeartBox').innerText = data?.poin_heart;
      document.getElementById('poinBrainBox').innerText = data?.poin_brain;
      shopGoldElem.innerText = data?.gold;
      const strikeElem = document.getElementById('strikeBox');
      strikeElem.children[0].innerText = data?.streak_current;
      strikeElem.children[1].innerText = data?.streak_percent_interest;
    };

    const userTasksHandler = (data) => {
      const wrapTasksElem = document.getElementById('wrapTasksBox');
      const guideCat = (cat, quant) => {
        let guide = '';
        if (cat == 'exercise' || cat == 'meditation') {
          guide = `Do ${cat} ${quant} times`;
        } else if (cat == 'reading') {
          guide = `Get ${quant} stars by reading`;
        }
        return guide;
      };

      const iconPoinCat = (cat) => {
        let icon = '';
        if (cat == 'exercise') {
          icon = '💪';
        } else if (cat == 'meditation') {
          icon = '🧘';
        } else if (cat == 'reading') {
          icon = '🧠';
        }
        return icon;
      };

      let htmlTasks = '';
      data.forEach((task) => {
        htmlTasks += `
        <div class="bg-white/80 mb-3 rounded-xl p-3 flex flex-col">
          <div
            class="text-gray-800 text-sm font-semibold mb-1.5 flex flex-row justify-between items-center"
          >
            <div>${task?.name}</div>
            <div>${task?.current_progress}/${task?.target_value}</div>
          </div>
          <div class="relative bg-amber-200 w-full h-2 rounded-full mb-1 overflow-hidden">
            <div class="h-full absolute bg-amber-500" style="width:${
              (task?.current_progress / task?.target_value) * 100
            }%;"></div>
          </div>
          <div class="text-xs text-gray-800 flex flex-row justify-between items-center">
            <div>${guideCat(task?.activity_category, task?.target_value)}</div>
            <div>${iconPoinCat(task?.activity_category)}+${
              task?.reward_poin_value
            }</div>
          </div>
        </div>
        `;
      });
      wrapTasksElem.innerHTML = htmlTasks;
    };

    const buyShopItemHandler = async (itemId) => {
      wrapLoaderElem.classList.remove('hidden');
      wrapLoaderElem.classList.add('flex');
      const respStatus = await putWithAuth(
        'shop/buy/item',
        { item_id: itemId },
        false,
        (data) => {}
      );
      wrapLoaderElem.classList.add('hidden');
      wrapLoaderElem.classList.remove('flex');

      if (respStatus != 200) {
        if (respStatus == 400) {
          wrapNotifNotEnoughGoldElem.classList.remove('hidden');
          wrapNotifNotEnoughGoldElem.classList.add('flex');
        } else {
          wrapErrorElem.classList.remove('hidden');
          wrapErrorElem.classList.add('flex');
        }
      } else {
        getWithAuth('user/me/gamestat', gameStatHandler);
        getWithAuth('user/me/bag/items', bagItemHandler);
        wrapNotifSuccessBuyElem.classList.remove('hidden');
        wrapNotifSuccessBuyElem.classList.add('flex');
      }
    };

    confirmBuyBtnElem.addEventListener('click', async (event) => {
      wrapConfirmBuyElem.classList.remove('flex');
      wrapConfirmBuyElem.classList.add('hidden');

      const itemId = event.target.getAttribute('data-item-id');
      await buyShopItemHandler(itemId);
    });

    const confirmBuyHandler = async (event) => {
      confirmBuyBtnElem.setAttribute(
        'data-item-id',
        event.target.getAttribute('data-item-id')
      );
      confirmNameElem.innerText = event.target.getAttribute('data-item-name');
      confirmThumbnailElem.src = event.target.getAttribute('data-item-thumbnail-path');
      const discountType = event.target.getAttribute('data-item-discount-type');
      if (discountType == 'percent') {
        confirmPercentValueElem.innerText = `-${event.target.getAttribute(
          'data-item-discount-value'
        )}%`;
      } else {
        confirmPercentValueElem.innerText = '';
      }

      if (discountType) {
        confirmPriceElem.innerHTML = `🪙 ${event.target.getAttribute(
          'data-item-total-price'
        )} <span class="line-through text-gray-300" style="font-size:8pt">${event.target.getAttribute(
          'data-item-raw-price'
        )}</span>`;
      } else {
        confirmPriceElem.innerText = `🪙 ${event.target.getAttribute(
          'data-item-raw-price'
        )}`;
      }
      wrapConfirmBuyElem.classList.remove('hidden');
      wrapConfirmBuyElem.classList.add('flex');
    };

    const shopItemHandler = (data) => {
      let htmlHatItems = '';
      let htmlClothesItems = '';
      let htmlShoesItems = '';

      data.forEach((item) => {
        let colorBaseTier = '';
        switch (item?.rarity) {
          case 'common':
            colorBaseTier = 'shadow-green-500';
            break;
          case 'rare':
            colorBaseTier = 'shadow-blue-500';
            break;
          case 'epic':
            colorBaseTier = 'shadow-red-500';
            break;
          case 'mythic':
            colorBaseTier = 'shadow-purple-500';
            break;
          default:
            colorBaseTier = 'shadow-amber-500';
        }
        const htmlItem = `
          <div
            class="flex-0 shrink-0 basis-auto w-24 shadow-sm ${colorBaseTier} bg-white rounded-xl p-2 flex flex-col items-center mr-4 h-full justify-between"
          >
            <div class="w-full text-center">${item?.name}</div>
            <div class="relative">
              <img
                src="${item?.thumbnail_path}"
                alt="Thumbnail"
              />
              ${
                item?.discount_type == 'percent' && item?.discount_value > 0
                  ? `
              <div class="absolute bottom-1 right-0 text-red-500" style="font-size:8pt">
                -${item?.discount_value}%
              </div>`
                  : ''
              }
            </div>
            ${
              item?.discount_type == 'percent' && item?.discount_value > 0
                ? `
            <div class="mb-1.5">
              🪙 ${
                item?.price_value - item?.price_value * (item?.discount_value / 100)
              } <span class="line-through text-gray-300" style="font-size:8pt"
                >${item?.price_value}</span
              >
            </div>
            `
                : `
            <div class="mb-1.5">
              🪙 ${item?.price_value}
            </div>
            `
            }
            <div
              data-item-id="${item?.id}"
              data-item-name="${item?.name}"
              data-item-thumbnail-path="${item?.thumbnail_path}"
              data-item-raw-price="${item?.price_value}"
              data-item-discount-type="${item?.discount_type}"
              data-item-discount-value="${item?.discount_value}"
              data-item-total-price="${
                item?.price_value - item?.price_value * (item?.discount_value / 100)
              }"
              class="bg-amber-400 hover:bg-amber-500 py-1 px-4 rounded-xl cursor-pointer"
            >
              Buy
            </div>
          </div>
        `;

        if (item?.category == 'hat') {
          htmlHatItems += htmlItem;
        } else if (item?.category == 'clothes') {
          htmlClothesItems += htmlItem;
        } else if (item?.category == 'shoes') {
          htmlShoesItems += htmlItem;
        }
      });

      itemShopHatElem.innerHTML = htmlHatItems;
      itemShopClothesElem.innerHTML = htmlClothesItems;
      itemShopShoesElem.innerHTML = htmlShoesItems;

      data.forEach((item) => {
        const itemElem = document.querySelector(`div[data-item-id="${item?.id}"]`);
        itemElem.addEventListener('click', confirmBuyHandler);
      });
    };

    getWithAuth('user/me/gamestat', gameStatHandler);
    getWithAuth('user/me/tasks', userTasksHandler);
    getWithAuth('shop/items', shopItemHandler);

    // These should be from database
    const listDataLayer = [
      {
        pathImg: './sprite-default/background/0_Background.png',
        distFromTop: 0,
        speedFrame: 0
      },
      {
        pathImg: './sprite-default/background/1_Trees_Background.png',
        distFromTop: 240,
        speedFrame: 0
      },
      {
        pathImg: './sprite-default/background/2_Trees.png',
        distFromTop: 250,
        speedFrame: 0.5
      },
      {
        pathImg: './sprite-default/background/3_Trees.png',
        distFromTop: 160,
        speedFrame: 1
      },
      {
        pathImg: './sprite-default/background/4_Trees.png',
        distFromTop: 200,
        speedFrame: 1.5
      },
      {
        pathImg: './sprite-default/background/5_Floor_Platform.png',
        distFromTop: 480,
        speedFrame: 2
      }
    ];
    const PlxBG = new ParallaxBG(listDataLayer);

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
    const SptObj = new SpriteObj(dataCharacter, dataHat, dataShirt, dataShoes);
    const objectHandler = (data) => {
      // Currently only hat, clothes (shirt-up), and shoes
      if (data.obj_hat_sprite) {
        SptObj.dataHat.universal = loadImg(data.obj_hat_sprite);
      } else {
        SptObj.dataHat.universal = loadImg(dataHat.universal);
      }

      if (data.obj_clothes_sprite) {
        SptObj.dataShirt.up.universal = loadImg(data.obj_clothes_sprite);
      } else {
        SptObj.dataShirt.up.universal = loadImg(dataShirt.up.universal);
      }

      if (data.obj_shoes_sprite) {
        SptObj.dataShoes.universal = loadImg(data.obj_shoes_sprite);
      } else {
        SptObj.dataShoes.universal = loadImg(dataShoes.universal);
      }

      listObjId = [data.obj_hat_id, data.obj_clothes_id, data.obj_shoes_id];
    };

    const equipOrUnequipItemHandler = async (event) => {
      const statusItem = event.target.getAttribute('status');
      const itemId = event.target.getAttribute('data-bag-item-id');

      wrapLoaderElem.classList.remove('hidden');
      wrapLoaderElem.classList.add('flex');
      let respStatus;
      if (statusItem == 'equipped') {
        respStatus = await putWithAuth(
          'user/me/bag/unequipitem',
          { category: event.target.getAttribute('category') },
          false,
          (data) => {}
        );
      }
      if (statusItem == 'unequip') {
        respStatus = await putWithAuth(
          'user/me/bag/equipitem',
          { item_id: itemId },
          false,
          (data) => {}
        );
      }
      wrapLoaderElem.classList.add('hidden');
      wrapLoaderElem.classList.remove('flex');

      if (respStatus != 200) {
        wrapErrorElem.classList.remove('hidden');
        wrapErrorElem.classList.add('flex');
      } else {
        getWithAuth('user/me/object', objectHandler).then(() => {
          getWithAuth('user/me/bag/items', bagItemHandler);
        });
      }
    };

    const bagItemHandler = (data) => {
      let htmlHatItems = '';
      let htmlClothesItems = '';
      let htmlShoesItems = '';
      data?.bag_items.forEach((item) => {
        let colorBaseTier = '';
        switch (item?.rarity) {
          case 'common':
            colorBaseTier = 'shadow-green-500';
            break;
          case 'rare':
            colorBaseTier = 'shadow-blue-500';
            break;
          case 'epic':
            colorBaseTier = 'shadow-red-500';
            break;
          case 'mythic':
            colorBaseTier = 'shadow-purple-500';
            break;
          default:
            colorBaseTier = 'shadow-amber-500';
        }
        const htmlItem = `
          <div
            class="flex-0 shrink-0 basis-auto w-24 shadow-sm ${colorBaseTier} bg-white rounded-xl p-2 flex flex-col h-full justify-between items-center mr-4"
          >
            <div class="w-full text-center">${item?.name}</div>
            <div>
              <img
                src="${item?.thumbnail_path}"
                alt="Thumbnail"
              />
            </div>
            ${
              listObjId.includes(item?.id)
                ? `
              <div
                data-bag-item-id="${item?.id}"
                status="equipped"
                category="${item?.category}"
                class="bg-gray-100 shadow-inner py-1 px-4 rounded-xl cursor-pointer">
                Equipped
              </div>
              `
                : `
              <div
                data-bag-item-id="${item?.id}"
                category="${item?.category}"
                status="unequip"
                class="bg-amber-400 hover:bg-amber-500 py-1 px-4 rounded-xl cursor-pointer"
              >
                Equip
              </div>
              `
            }
          </div>
        `;

        if (item?.category == 'hat') {
          htmlHatItems += htmlItem;
        } else if (item?.category == 'clothes') {
          htmlClothesItems += htmlItem;
        } else if (item?.category == 'shoes') {
          htmlShoesItems += htmlItem;
        }
      });

      itemBagHatElem.innerHTML = htmlHatItems;
      itemBagClothesElem.innerHTML = htmlClothesItems;
      itemBagShoesElem.innerHTML = htmlShoesItems;

      data?.bag_items.forEach((item) => {
        const itemElem = document.querySelector(`div[data-bag-item-id="${item?.id}"]`);
        itemElem.addEventListener('click', equipOrUnequipItemHandler);
      });
    };

    getWithAuth('user/me/object', objectHandler).then(() => {
      getWithAuth('user/me/bag/items', bagItemHandler);
    });

    let fps = 0;
    let times = [];
    let fpsRate = 14;
    let frame = 0;
    const drawCnv = () => {
      const now = performance.now();
      while (times.length > 0 && times[0] <= now - 1000) {
        times.shift();
      }
      times.push(now);

      fps = times.length - 1;
      if (frame > Math.round((fps / 60) * fpsRate)) {
        fpsElem.innerText = fps;
        frame = 0;
      }

      frame += 1;
      if (ctx) {
        ctx.clearRect(0, 0, canvasElem.width, canvasElem.height);
        ctx.beginPath();

        PlxBG.updatePosition(fps);
        PlxBG.draw();

        SptObj?.animateWalk(fps);
      }
      window.requestAnimationFrame(drawCnv);
    };
    ctx = canvasElem.getContext('2d');
    drawCnv();
  });
</script>

<div id="wrapBox" class="flex flex-col w-full bg-gray-700">
  <div id="skyBox" class="w-full bg-gradient-to-t from-iy-blue-100 to-sky-600"></div>
  <canvas id="canvasBox" class="w-full bg-amber-950"></canvas>
  <div id="groundBox" class="w-full bg-gradient-to-b from-amber-950 to-amber-900"></div>
</div>

<!-- Task UI -->
<div
  id="wrapTaskBox"
  style="height:96px"
  class="absolute rounded-t-xl bg-white/75 w-full max-h-full h-auto bottom-0 pb-16 flex flex-col z-20"
>
  <div
    id="toggleTaskBtn"
    data-toggle="deactive"
    class="flex flex-row h-8 justify-center items-center cursor-pointer group"
  >
    <div
      class="w-8 h-8 group-hover:fill-gray-900 fill-gray-600 animate-pulse pointer-events-none"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        ><path
          d="M12.0001 4.83594L5.79297 11.043L7.20718 12.4573L12.0001 7.66436L16.793 12.4573L18.2072 11.043L12.0001 4.83594ZM12.0001 10.4858L5.79297 16.6929L7.20718 18.1072L12.0001 13.3143L16.793 18.1072L18.2072 16.6929L12.0001 10.4858Z"
        ></path></svg
      >
    </div>
    <div
      class="hidden w-8 h-8 group-hover:fill-gray-900 fill-gray-600 animate-pulse pointer-events-none"
    >
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
        ><path
          d="M12.0001 19.1643L18.2072 12.9572L16.793 11.543L12.0001 16.3359L7.20718 11.543L5.79297 12.9572L12.0001 19.1643ZM12.0001 13.5144L18.2072 7.30728L16.793 5.89307L12.0001 10.686L7.20718 5.89307L5.79297 7.30728L12.0001 13.5144Z"
        ></path></svg
      >
    </div>
  </div>
  <div id="wrapTasksBox" class="overflow-y-auto px-1 xxs:px-2 xs:px-4"></div>
</div>

<!-- GameStat UI -->
<div class="absolute top-0 w-full flex flex-col h-full z-10 pb-24">
  <div
    class="text-center text-gray-700 mx-1.5 xxs:mx-2.5 xs:mx-4 mt-4 mb-5 rounded-md flex flex-row justify-between items-center"
  >
    <div
      class="flex flex-row items-center ring-4 ring-white/50 bg-white/80 py-0.5 px-1.5 rounded-full"
    >
      <div class="mr-0.5">🪙</div>
      <div id="goldBox" class="text-sm font-semibold"></div>
    </div>
    <div
      class="flex flex-row items-center ring-4 ring-white/50 bg-white/80 py-0.5 px-1.5 rounded-full"
    >
      <div class="mr-0.5">💪</div>
      <div id="poinMuscleBox" class="text-sm font-semibold"></div>
    </div>
    <div
      class="flex flex-row items-center ring-4 ring-white/50 bg-white/80 py-0.5 px-1.5 rounded-full"
    >
      <div class="mr-0.5">🧘</div>
      <div id="poinHeartBox" class="text-sm font-semibold"></div>
    </div>
    <div
      class="flex flex-row items-center ring-4 ring-white/50 bg-white/80 py-0.5 px-1.5 rounded-full"
    >
      <div class="mr-0.5">🧠</div>
      <div id="poinBrainBox" class="text-sm font-semibold"></div>
    </div>
  </div>
  <div class="flex flex-row justify-between items-start">
    <div class="flex flex-col ml-1.5 xxs:ml-2.5 xs:ml-4">
      <div
        class="py-1 pl-2 pr-1 mb-4 bg-white/80 ring-4 ring-white/50 rounded-full text-sm text-gray-700 font-semibold flex flex-row items-center w-fit"
      >
        <div class="mr-1">Strike</div>
        <div class=" bg-orange-200/80 flex flex-row items-center rounded-full px-1.5">
          <div class="relative w-2.5 h-2.5 mr-1 fill-orange-500">
            <svg
              class="absolute"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 448 512"
              ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M159.3 5.4c7.8-7.3 19.9-7.2 27.7 .1c27.6 25.9 53.5 53.8 77.7 84c11-14.4 23.5-30.1 37-42.9c7.9-7.4 20.1-7.4 28 .1c34.6 33 63.9 76.6 84.5 118c20.3 40.8 33.8 82.5 33.8 111.9C448 404.2 348.2 512 224 512C98.4 512 0 404.1 0 276.5c0-38.4 17.8-85.3 45.4-131.7C73.3 97.7 112.7 48.6 159.3 5.4zM225.7 416c25.3 0 47.7-7 68.8-21c42.1-29.4 53.4-88.2 28.1-134.4c-4.5-9-16-9.6-22.5-2l-25.2 29.3c-6.6 7.6-18.5 7.4-24.7-.5c-16.5-21-46-58.5-62.8-79.8c-6.3-8-18.3-8.1-24.7-.1c-33.8 42.5-50.8 69.3-50.8 99.4C112 375.4 162.6 416 225.7 416z"
              /></svg
            >
            <svg
              class="absolute animate-ping"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 448 512"
              ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M159.3 5.4c7.8-7.3 19.9-7.2 27.7 .1c27.6 25.9 53.5 53.8 77.7 84c11-14.4 23.5-30.1 37-42.9c7.9-7.4 20.1-7.4 28 .1c34.6 33 63.9 76.6 84.5 118c20.3 40.8 33.8 82.5 33.8 111.9C448 404.2 348.2 512 224 512C98.4 512 0 404.1 0 276.5c0-38.4 17.8-85.3 45.4-131.7C73.3 97.7 112.7 48.6 159.3 5.4zM225.7 416c25.3 0 47.7-7 68.8-21c42.1-29.4 53.4-88.2 28.1-134.4c-4.5-9-16-9.6-22.5-2l-25.2 29.3c-6.6 7.6-18.5 7.4-24.7-.5c-16.5-21-46-58.5-62.8-79.8c-6.3-8-18.3-8.1-24.7-.1c-33.8 42.5-50.8 69.3-50.8 99.4C112 375.4 162.6 416 225.7 416z"
              /></svg
            >
          </div>
          <div id="strikeBox"><span>5</span>; (<span>0</span>%)</div>
        </div>
      </div>
      <div
        class="flex py-1 px-2 ring-4 ring-white/50 bg-white/80 rounded-full text-sm text-gray-700 font-semibold flex-row items-center w-fit cursor-not-allowed"
      >
        <div id="usernameBox" class="mr-1"></div>
        <div class="w-2.5 h-2.5 fill-gray-700">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
            ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
              d="M410.3 231l11.3-11.3-33.9-33.9-62.1-62.1L291.7 89.8l-11.3 11.3-22.6 22.6L58.6 322.9c-10.4 10.4-18 23.3-22.2 37.4L1 480.7c-2.5 8.4-.2 17.5 6.1 23.7s15.3 8.5 23.7 6.1l120.3-35.4c14.1-4.2 27-11.8 37.4-22.2L387.7 253.7 410.3 231zM160 399.4l-9.1 22.7c-4 3.1-8.5 5.4-13.3 6.9L59.4 452l23-78.1c1.4-4.9 3.8-9.4 6.9-13.3l22.7-9.1v32c0 8.8 7.2 16 16 16h32zM362.7 18.7L348.3 33.2 325.7 55.8 314.3 67.1l33.9 33.9 62.1 62.1 33.9 33.9 11.3-11.3 22.6-22.6 14.5-14.5c25-25 25-65.5 0-90.5L453.3 18.7c-25-25-65.5-25-90.5 0zm-47.4 168l-144 144c-6.2 6.2-16.4 6.2-22.6 0s-6.2-16.4 0-22.6l144-144c6.2-6.2 16.4-6.2 22.6 0s6.2 16.4 0 22.6z"
            /></svg
          >
        </div>
      </div>
    </div>
    <div class="flex flex-col items-end mr-1.5 xxs:mr-2.5 xs:mr-4">
      <div
        class="flex py-1 px-2 mb-4 ring-4 ring-white/50 bg-white/80 rounded-full text-sm text-gray-700 font-semibold flex-row items-center w-fit cursor-pointer"
      >
        <div id="daysBox"></div>
      </div>
      <div
        class="py-1 px-2 ring-4 ring-white/50 bg-white/80 rounded-full text-sm text-gray-700 font-semibold flex flex-row items-center w-fit cursor-pointer"
      >
        <div>FPS: <span id="fpsBox"></span></div>
      </div>
    </div>
  </div>
  <div class="flex-1 w-full flex flex-row items-center justify-between">
    <div
      class="flex flex-col items-center ml-1.5 xxs:ml-2.5 xs:ml-4 bg-white/80 ring-4 ring-white/50 rounded-full"
    >
      <div
        class="fill-amber-500 p-1.5 mb-3 bg-white/80 rounded-full cursor-not-allowed hover:bg-amber-100/80"
      >
        <svg class="w-8 h-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
          ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M495.9 166.6c3.2 8.7 .5 18.4-6.4 24.6l-43.3 39.4c1.1 8.3 1.7 16.8 1.7 25.4s-.6 17.1-1.7 25.4l43.3 39.4c6.9 6.2 9.6 15.9 6.4 24.6c-4.4 11.9-9.7 23.3-15.8 34.3l-4.7 8.1c-6.6 11-14 21.4-22.1 31.2c-5.9 7.2-15.7 9.6-24.5 6.8l-55.7-17.7c-13.4 10.3-28.2 18.9-44 25.4l-12.5 57.1c-2 9.1-9 16.3-18.2 17.8c-13.8 2.3-28 3.5-42.5 3.5s-28.7-1.2-42.5-3.5c-9.2-1.5-16.2-8.7-18.2-17.8l-12.5-57.1c-15.8-6.5-30.6-15.1-44-25.4L83.1 425.9c-8.8 2.8-18.6 .3-24.5-6.8c-8.1-9.8-15.5-20.2-22.1-31.2l-4.7-8.1c-6.1-11-11.4-22.4-15.8-34.3c-3.2-8.7-.5-18.4 6.4-24.6l43.3-39.4C64.6 273.1 64 264.6 64 256s.6-17.1 1.7-25.4L22.4 191.2c-6.9-6.2-9.6-15.9-6.4-24.6c4.4-11.9 9.7-23.3 15.8-34.3l4.7-8.1c6.6-11 14-21.4 22.1-31.2c5.9-7.2 15.7-9.6 24.5-6.8l55.7 17.7c13.4-10.3 28.2-18.9 44-25.4l12.5-57.1c2-9.1 9-16.3 18.2-17.8C227.3 1.2 241.5 0 256 0s28.7 1.2 42.5 3.5c9.2 1.5 16.2 8.7 18.2 17.8l12.5 57.1c15.8 6.5 30.6 15.1 44 25.4l55.7-17.7c8.8-2.8 18.6-.3 24.5 6.8c8.1 9.8 15.5 20.2 22.1 31.2l4.7 8.1c6.1 11 11.4 22.4 15.8 34.3zM256 336a80 80 0 1 0 0-160 80 80 0 1 0 0 160z"
          /></svg
        >
      </div>
      <!-- Daily Check Btn -->
      <div
        id="dailyCheckBtn"
        class="relative fill-amber-500 p-1.5 bg-white rounded-full cursor-pointer hover:bg-amber-100/80"
      >
        <svg class="w-8 h-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 384 512"
          ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M192 0c-41.8 0-77.4 26.7-90.5 64H64C28.7 64 0 92.7 0 128V448c0 35.3 28.7 64 64 64H320c35.3 0 64-28.7 64-64V128c0-35.3-28.7-64-64-64H282.5C269.4 26.7 233.8 0 192 0zm0 64a32 32 0 1 1 0 64 32 32 0 1 1 0-64zM305 273L177 401c-9.4 9.4-24.6 9.4-33.9 0L79 337c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L271 239c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"
          /></svg
        >
        <div id="pingDailyCheckBox" class="absolute top-1 right-2.5">
          <div class="relative">
            <div class="absolute h-2.5 w-2.5 rounded-full bg-red-600"></div>
            <div
              class="absolute h-2.5 w-2.5 rounded-full bg-red-600 animate-ping"
            ></div>
          </div>
        </div>
      </div>
    </div>
    <div
      class="flex flex-col items-center mr-1.5 xxs:mr-2.5 xs:mr-4 bg-white/80 ring-4 ring-white/50 rounded-full"
    >
      <!-- Shop Button -->
      <div
        id="shopBtn"
        class="fill-amber-500 p-1.5 mb-3 bg-white/80 rounded-full cursor-pointer hover:bg-amber-100/80"
      >
        <svg class="w-8 h-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"
          ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M547.6 103.8L490.3 13.1C485.2 5 476.1 0 466.4 0H109.6C99.9 0 90.8 5 85.7 13.1L28.3 103.8c-29.6 46.8-3.4 111.9 51.9 119.4c4 .5 8.1 .8 12.1 .8c26.1 0 49.3-11.4 65.2-29c15.9 17.6 39.1 29 65.2 29c26.1 0 49.3-11.4 65.2-29c15.9 17.6 39.1 29 65.2 29c26.2 0 49.3-11.4 65.2-29c16 17.6 39.1 29 65.2 29c4.1 0 8.1-.3 12.1-.8c55.5-7.4 81.8-72.5 52.1-119.4zM499.7 254.9l-.1 0c-5.3 .7-10.7 1.1-16.2 1.1c-12.4 0-24.3-1.9-35.4-5.3V384H128V250.6c-11.2 3.5-23.2 5.4-35.6 5.4c-5.5 0-11-.4-16.3-1.1l-.1 0c-4.1-.6-8.1-1.3-12-2.3V384v64c0 35.3 28.7 64 64 64H448c35.3 0 64-28.7 64-64V384 252.6c-4 1-8 1.8-12.3 2.3z"
          /></svg
        >
      </div>
      <!-- Bag Button -->
      <div
        id="bagBtn"
        class="fill-amber-500 p-1.5 bg-white rounded-full cursor-pointer hover:bg-amber-100/80"
      >
        <svg class="w-8 h-8" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512"
          ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M160 112c0-35.3 28.7-64 64-64s64 28.7 64 64v48H160V112zm-48 48H48c-26.5 0-48 21.5-48 48V416c0 53 43 96 96 96H352c53 0 96-43 96-96V208c0-26.5-21.5-48-48-48H336V112C336 50.1 285.9 0 224 0S112 50.1 112 112v48zm24 48a24 24 0 1 1 0 48 24 24 0 1 1 0-48zm152 24a24 24 0 1 1 48 0 24 24 0 1 1 -48 0z"
          /></svg
        >
      </div>
    </div>
  </div>
</div>

<!-- Daily Check -->
<div
  id="wrapDailyCheckBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    class="bg-white p-4 max-w-xs w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center"
  >
    <div class="flex flex-row justify-between w-full items-center mb-4">
      <div class=" text-gray-800 font-semibold">
        Daily Check <span
          class="text-sm py-0.5 rounded-xl px-1 bg-orange-100 text-amber-600"
          >🪙+10</span
        >
      </div>
      <div id="closeDailyCheckBtn" class="fill-amber-400 cursor-pointer">
        <svg class="w-7 h-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c9.4-9.4 24.6-9.4 33.9 0l47 47 47-47c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-47 47 47 47c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-47-47-47 47c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l47-47-47-47c-9.4-9.4-9.4-24.6 0-33.9z"
          /></svg
        >
      </div>
    </div>
    <div
      id="mainDailyCheckBox"
      class="flex flex-col w-full shadow-inner bg-gray-100 rounded-xl p-4 text-sm font-semibold text-gray-600"
    >
      <div class="mb-4">
        Did you masturbate yesterday <span id="dateTargetDCBox">(Sun 27 Sep 2023)</span>
        ?
      </div>
      <div class="mb-4 flex flex-row w-full items-center justify-center">
        <div
          id="negAnsBtn"
          class="p-2 mr-4 bg-white rounded-xl shadow-sm shadow-green-400 cursor-pointer hover:bg-green-50"
        >
          I didn't
        </div>
        <div
          id="posAnsBtn"
          class="p-2 bg-white rounded-xl shadow-sm shadow-red-400 cursor-pointer hover:bg-red-50"
        >
          I did
        </div>
      </div>
      <div class="text-xs font-medium text-center">
        By answering this question, your progress will be tracked. Reset each day at
        7am. (GMT+7)
      </div>
    </div>

    <div
      id="warnDailyCheckBox"
      class="hidden flex-col w-full shadow-inner bg-gray-100 rounded-xl p-4 text-sm font-semibold text-gray-600"
    >
      <div class="flex flex-row justify-center py-2 mb-4">
        <img class="w-24 h-24" src="./icon/undraw_no_data_re_kwbl.svg" alt="Empty" />
      </div>
      <div class="text-sm font-medium text-center">
        Dailycheck already filled in today or something wrong
      </div>
    </div>
  </div>
</div>

<!-- Notif Success DailyCheck -->
<div
  id="wrapNotifSuccessDCBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="font-semibold mb-2">Info</div>
    <div class="text-center mb-2">Your data has been successfully recorded.</div>
    <div
      id="okNotifSuccessDCBtn"
      class="px-4 py-1 rounded-xl bg-amber-400 cursor-pointer hover:bg-amber-500 font-semibold"
    >
      Ok
    </div>
  </div>
</div>

<!-- Shop Items -->
<div
  id="wrapShopBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    class="relative bg-white p-4 max-w-xs w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700"
  >
    <div class="absolute top-0 w-full h-auto flex flex-row justify-center">
      <div class="bg-white p-1 -mt-8 rounded-t-xl w-20 text-center font-bold">Shop</div>
    </div>
    <div class="w-full flex flex-row justify-between items-center mb-1">
      <div
        class="text-sm font-semibold text-amber-600 bg-amber-200 py-0.5 px-1 rounded-xl"
      >
        🪙 <span id="shopGoldBox"></span>
      </div>
      <div id="closeWrapShopBtn" class="fill-amber-400 cursor-pointer">
        <svg class="w-7 h-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c9.4-9.4 24.6-9.4 33.9 0l47 47 47-47c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-47 47 47 47c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-47-47-47 47c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l47-47-47-47c-9.4-9.4-9.4-24.6 0-33.9z"
          /></svg
        >
      </div>
    </div>
    <div
      class="w-full flex flex-row justify-center items-center text-sm font-semibold z-20"
    >
      <div
        id="shopMenuHatBox"
        class="px-3 pt-1 pb-2 w-20 cursor-pointer text-center rounded-t-xl shadow-inner bg-gray-100"
      >
        Hat
      </div>
      <div
        id="shopMenuClothesBox"
        class="px-3 pt-1 pb-2 w-20 cursor-pointer text-center"
      >
        Clothes
      </div>
      <div id="shopMenuShoesBox" class="px-3 pt-1 pb-2 w-20 cursor-pointer text-center">
        Shoes
      </div>
    </div>
    <div
      id="itemShopHatBox"
      class="flex w-full shadow-inner bg-gray-100 rounded-xl py-4 pl-4 text-xs font-semibold -mt-1 z-10 flex-row justify-start items-center flex-nowrap overflow-x-auto"
    ></div>
    <div
      id="itemShopClothesBox"
      class="hidden w-full shadow-inner bg-gray-100 rounded-xl py-4 pl-4 text-xs font-semibold -mt-1 z-10 flex-row justify-start items-center flex-nowrap overflow-x-auto"
    ></div>
    <div
      id="itemShopShoesBox"
      class="hidden w-full shadow-inner bg-gray-100 rounded-xl py-4 pl-4 text-xs font-semibold -mt-1 z-10 flex-row justify-start items-center flex-nowrap overflow-x-auto"
    ></div>
  </div>
</div>

<!-- Confirm Buy -->
<div
  id="wrapConfirmBuyBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="font-semibold text-md w-full text-center" id="confirmNameBox"></div>
    <div class="relative">
      <img id="confirmThumbnailBox" src="" alt="Thumbnail" />
      <div
        id="confirmPercentValueBox"
        class="absolute bottom-1 right-0 text-red-500"
        style="font-size:8pt"
      ></div>
    </div>
    <div class="mb-1.5" id="confirmPriceBox">
      <!-- 🪙 2000 <span class="line-through text-gray-300" style="font-size:8pt">2500</span> -->
    </div>
    <div class="mb-3">Do you want to buy?</div>
    <div class="flex flex-row justify-center items-center">
      <div
        id="confirmBuyBtn"
        class="mr-2 px-2 py-1 rounded-xl bg-amber-400 cursor-pointer hover:bg-amber-500 font-semibold"
      >
        Confirm
      </div>
      <div
        id="cancelBuyBtn"
        class="px-2 py-1 rounded-xl bg-gray-300 cursor-pointer hover:bg-gray-400 font-semibold"
      >
        Cancel
      </div>
    </div>
  </div>
</div>

<!-- Not enough gold or already owned -->
<div
  id="wrapNotifNotEnoughGoldBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="font-semibold mb-2">Failed to Buy</div>
    <div class="text-center mb-2">Gold not enough or the item is already owned</div>
    <div
      id="okNotifNotEnoughBtn"
      class="px-4 py-1 rounded-xl bg-amber-400 cursor-pointer hover:bg-amber-500 font-semibold"
    >
      Ok
    </div>
  </div>
</div>

<!-- Notif Success Buy -->
<div
  id="wrapNotifSuccessBuyBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    style="max-width:196px;"
    class="relative bg-white p-4 w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700 text-sm"
  >
    <div class="font-semibold mb-2">Success!</div>
    <div class="text-center mb-2">
      Thank you for purchasing, please check the item in your bag.
    </div>
    <div
      id="okNotifSuccessBtn"
      class="px-4 py-1 rounded-xl bg-amber-400 cursor-pointer hover:bg-amber-500 font-semibold"
    >
      Ok
    </div>
  </div>
</div>

<!-- Bag Items -->
<div
  id="wrapBagBox"
  class="hidden absolute top-0 w-full flex-col justify-center items-center h-full bg-gray-900/80 z-20 pb-16"
>
  <div
    class="relative bg-white p-4 max-w-xs w-full h-full xxs:h-auto xxs:rounded-xl flex flex-col items-center text-gray-700"
  >
    <div class="absolute top-0 w-full h-auto flex flex-row justify-center">
      <div class="bg-white p-1 -mt-8 rounded-t-xl w-20 text-center font-bold">Bag</div>
    </div>
    <div class="w-full flex flex-row justify-between items-center mb-1">
      <div
        id="triggerShopFromBagBtn"
        class="fill-amber-400 hover:fill-amber-500 cursor-pointer"
      >
        <svg class="w-7 h-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512"
          ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M547.6 103.8L490.3 13.1C485.2 5 476.1 0 466.4 0H109.6C99.9 0 90.8 5 85.7 13.1L28.3 103.8c-29.6 46.8-3.4 111.9 51.9 119.4c4 .5 8.1 .8 12.1 .8c26.1 0 49.3-11.4 65.2-29c15.9 17.6 39.1 29 65.2 29c26.1 0 49.3-11.4 65.2-29c15.9 17.6 39.1 29 65.2 29c26.2 0 49.3-11.4 65.2-29c16 17.6 39.1 29 65.2 29c4.1 0 8.1-.3 12.1-.8c55.5-7.4 81.8-72.5 52.1-119.4zM499.7 254.9l-.1 0c-5.3 .7-10.7 1.1-16.2 1.1c-12.4 0-24.3-1.9-35.4-5.3V384H128V250.6c-11.2 3.5-23.2 5.4-35.6 5.4c-5.5 0-11-.4-16.3-1.1l-.1 0c-4.1-.6-8.1-1.3-12-2.3V384v64c0 35.3 28.7 64 64 64H448c35.3 0 64-28.7 64-64V384 252.6c-4 1-8 1.8-12.3 2.3z"
          /></svg
        >
      </div>
      <div id="closeBagBtn" class="fill-amber-400 hover:fill-amber-500 cursor-pointer">
        <svg class="w-7 h-7" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"
          ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
            d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM175 175c9.4-9.4 24.6-9.4 33.9 0l47 47 47-47c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-47 47 47 47c9.4 9.4 9.4 24.6 0 33.9s-24.6 9.4-33.9 0l-47-47-47 47c-9.4 9.4-24.6 9.4-33.9 0s-9.4-24.6 0-33.9l47-47-47-47c-9.4-9.4-9.4-24.6 0-33.9z"
          /></svg
        >
      </div>
    </div>
    <div
      class="w-full flex flex-row justify-center items-center text-sm font-semibold z-20"
    >
      <div
        id="bagMenuHatBox"
        class="px-3 pt-1 pb-2 w-20 cursor-pointer text-center rounded-t-xl shadow-inner bg-gray-100"
      >
        Hat
      </div>
      <div
        id="bagMenuClothesBox"
        class="px-3 pt-1 pb-2 w-20 cursor-pointer text-center"
      >
        Clothes
      </div>
      <div id="bagMenuShoesBox" class="px-3 pt-1 pb-2 w-20 cursor-pointer text-center">
        Shoes
      </div>
    </div>
    <div
      id="itemBagHatBox"
      class="flex w-full shadow-inner bg-gray-100 rounded-xl py-4 pl-4 text-xs font-semibold -mt-1 z-10 flex-row justify-start items-center flex-nowrap overflow-x-auto"
    ></div>
    <div
      id="itemBagClothesBox"
      class="hidden w-full shadow-inner bg-gray-100 rounded-xl py-4 pl-4 text-xs font-semibold -mt-1 z-10 flex-row justify-start items-center flex-nowrap overflow-x-auto"
    ></div>
    <div
      id="itemBagShoesBox"
      class="hidden w-full shadow-inner bg-gray-100 rounded-xl py-4 pl-4 text-xs font-semibold -mt-1 z-10 flex-row justify-start items-center flex-nowrap overflow-x-auto"
    ></div>
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
