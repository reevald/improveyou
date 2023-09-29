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

  onMount(async () => {
    const wrapTrackerElem = document.getElementById('wrapTrackerBox');
    resizeWrap(wrapTrackerElem);
    window.addEventListener('resize', () => {
      resizeWrap(wrapTrackerElem);
    });

    const prevMonthBtnElem = document.getElementById('prevMonthBtn');
    const nextMonthBtnElem = document.getElementById('nextMonthBtn');
    const currMonthYearElem = document.getElementById('currMonthYearBox');
    const mainDaysElem = document.getElementById('mainDaysBox');
    const wrapLoaderElem = document.getElementById('wrapLoaderBox');

    const totalStreakElem = document.getElementById('totalStreakBox');
    const currStreakElem = document.getElementById('currStreakBox');
    const bestStreakElem = document.getElementById('bestStreakBox');
    const totalTaskDoneElem = document.getElementById('totalTaskDoneBox');

    const barTaskExeElem = document.getElementById('barTaskExeBox');
    const barTaskMedElem = document.getElementById('barTaskMedBox');
    const barTaskReadElem = document.getElementById('barTaskReadBox');
    const percentTaskExeElem = document.getElementById('percentTaskExeBox');
    const percentTaskMedElem = document.getElementById('percentTaskMedBox');
    const percentTaskReadElem = document.getElementById('percentTaskReadBox');

    const currMonthYearGraphElem = document.getElementById('currMonthYearGraphBox');
    const prevMonthGraphBtnElem = document.getElementById('prevMonthGraphBtn');
    const nextMonthGraphBtnElem = document.getElementById('nextMonthGraphBtn');

    // Reference: https://www.geeksforgeeks.org/how-to-design-a-simple-calendar-using-javascript/
    // Init dates
    let date = new Date();
    date.setHours(0, 0, 0, 0);

    let year = date.getFullYear();
    let month = date.getMonth();
    let dataEvent = {};

    const msInADay = 24 * 60 * 60 * 1000;
    const short_months = [
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

    const renderCalendar = () => {
      if (Object.keys(dataEvent).length === 0) return;

      const dayOne = new Date(year, month, 1).getDay();
      const lastDate = new Date(year, month + 1, 0).getDate();
      const monthLastDate = new Date(year, month, 0).getDate();

      const dateJoined = new Date(dataEvent?.date_joined).setHours(0, 0, 0, 0);
      const listStreakDate = dataEvent?.streak_track.map((data) => {
        if (data?.streak_status == 'continue') {
          return new Date(data?.date_target).toDateString();
        }
      });

      let htmlDays = '';
      let lastStreak = 0;

      for (let i = dayOne; i > 0; i--) {
        htmlDays += '<div></div>';
      }

      for (let i = 1; i <= lastDate; i++) {
        // Check if the current date is today
        const isToday =
          i === date.getDate() &&
          month === new Date().getMonth() &&
          year === new Date().getFullYear();

        const iDate = new Date(year, month, i);
        iDate.setHours(0, 0, 0, 0);
        const strIDate = iDate.toDateString();

        const basicDay = (i) => `
          <div class="w-full flex flex-row items-center justify-center">
            <div
              class="w-7 h-7 xxs:w-8 xxs:h-8 xs:w-9 xs:h-9 rounded-full flex flex-row items-center justify-center text-sm font-semibold hover:bg-lime-100 cursor-default"
            >
              ${i}
            </div>
          </div>
        `;

        if (dateJoined - msInADay * 2 <= iDate && iDate <= date) {
          if (listStreakDate.includes(strIDate)) {
            const isWired =
              strIDate.split(' ')[0] != 'Sun' && lastStreak != 0 && lastStreak == i - 1;

            htmlDays += `
              <div class="${
                isWired ? 'relative' : ''
              } w-full flex flex-row items-center justify-center">
                <div
                  class="border-lime-400 border-2 bg-lime-300 hover:bg-lime-200 ring-lime-500 ring-2 w-7 h-7 xxs:w-8 xxs:h-8 xs:w-9 xs:h-9 rounded-full flex flex-row items-center justify-center text-sm font-semibold z-20 cursor-default"
                >
                  ${i}
                </div>
                ${
                  isWired
                    ? `
                  <div
                    class="absolute w-6 xxs:w-10 h-0.5 -ml-10 xxs:-ml-14 xs:-ml-16 bg-lime-500 z-10"
                  ></div>
                  `
                    : ''
                }
              </div>
            `;
            lastStreak = i;
          } else if (dateJoined <= iDate) {
            htmlDays += `
              <div class="w-full flex flex-row items-center justify-center">
                <div
                  class="border-lime-400 border-2 ring-lime-500 ring-2 w-7 h-7 xxs:w-8 xxs:h-8 xs:w-9 xs:h-9 rounded-full flex flex-row items-center justify-center text-sm font-semibold ${
                    isToday ? 'bg-lime-100' : 'bg-white hover:bg-lime-100'
                  } cursor-default"
                >
                  ${i}
                </div>
              </div>
            `;
          } else {
            htmlDays += basicDay(i);
          }
        } else {
          htmlDays += basicDay(i);
        }
      }

      currMonthYearElem.innerText = `${short_months[month]} ${year}`;
      mainDaysElem.innerHTML = htmlDays;
    };

    const setDataAndRender = () => {
      if (Object.keys(dataEvent).length === 0) return;

      let listUTCStreakDate = [];
      let totalStreak = 0;
      listUTCStreakDate = dataEvent?.streak_track
        .map((data) => {
          if (data?.streak_status == 'continue') {
            totalStreak += 1;
            return new Date(new Date(data?.date_target).toDateString()).getTime();
          }
        })
        .sort((a, b) => b - a);

      let finalCurrStreak = 0;
      let finalBestStreak = 0;

      const now = new Date();
      const miliEpochUTCToday = new Date(
        now.getFullYear(),
        now.getMonth(),
        now.getDate(),
        0,
        0,
        0
      ).getTime();
      const miliEpochUTCYesterday = miliEpochUTCToday - msInADay;

      let currStreak = 0;
      let lastCurrStreak;
      for (let i = 0; i < listUTCStreakDate.length; i++) {
        if (miliEpochUTCYesterday - msInADay * i == listUTCStreakDate[i]) {
          finalCurrStreak += 1;
        }

        if (lastCurrStreak) {
          if (lastCurrStreak - msInADay == listUTCStreakDate[i]) {
            currStreak += 1;
          } else {
            currStreak = 0;
          }
          finalBestStreak = currStreak > finalBestStreak ? currStreak : finalBestStreak;
        }

        lastCurrStreak = listUTCStreakDate[i];
        if (currStreak == 0) {
          currStreak += 1;
        }
      }

      totalStreakElem.innerText = totalStreak;
      currStreakElem.innerText = finalCurrStreak;
      bestStreakElem.innerText = finalBestStreak;
      totalTaskDoneElem.innerText = dataEvent?.task_track
        ? dataEvent.task_track.length
        : 0;
    };

    let yearGraph = year;
    let monthGraph = month;
    const renderGraph = () => {
      if (Object.keys(dataEvent).length === 0) return;

      let now = new Date();
      now.setHours(0, 0, 0, 0);
      now = now.getTime();
      let firstDate = new Date(yearGraph, monthGraph, 1).getTime();
      let lastDate = new Date(yearGraph, monthGraph + 1, 0).getTime();
      const dateJoined = new Date(dataEvent?.date_joined).setHours(0, 0, 0, 0);

      if (firstDate <= dateJoined && dateJoined <= lastDate) {
        firstDate = dateJoined;
      }

      if (firstDate <= now && now <= lastDate) {
        lastDate = now;
      }

      const finalResultGraph = {
        exercise: 0,
        meditation: 0,
        reading: 0
      };
      const diffDays = Math.round(Math.abs((firstDate - lastDate) / msInADay)) + 1;

      dataEvent?.task_track?.forEach((task) => {
        const taskDate = new Date(task?.completed_at).getTime();
        if (firstDate <= taskDate && taskDate <= lastDate) {
          finalResultGraph[task?.category] += 1;
        }
      });

      // https://stackoverflow.com/a/18358056
      const roundToTwo = (num) => {
        return +(Math.round(num + 'e+2') + 'e-2');
      };

      // To simplify one category = one task = one day
      finalResultGraph.exercise = roundToTwo(
        (finalResultGraph.exercise / diffDays) * 100
      );
      finalResultGraph.meditation = roundToTwo(
        (finalResultGraph.meditation / diffDays) * 100
      );
      finalResultGraph.reading = roundToTwo(
        (finalResultGraph.reading / diffDays) * 100
      );

      percentTaskExeElem.innerText = `${finalResultGraph.exercise}%`;
      percentTaskMedElem.innerText = `${finalResultGraph.meditation}%`;
      percentTaskReadElem.innerText = `${finalResultGraph.reading}%`;

      barTaskExeElem.style.height = `${finalResultGraph.exercise}%`;
      barTaskMedElem.style.height = `${finalResultGraph.meditation}%`;
      barTaskReadElem.style.height = `${finalResultGraph.reading}%`;

      const dateFormat =
        firstDate == lastDate
          ? `${new Date(firstDate).getDate()}`
          : `${new Date(firstDate).getDate()} - ${new Date(lastDate).getDate()}`;
      currMonthYearGraphElem.innerHTML = `${
        firstDate == dateJoined ? '(Joined) ' : ''
      }${dateFormat} ${short_months[new Date(lastDate).getMonth()]} ${new Date(
        lastDate
      ).getFullYear()}`;
    };

    const trackerHandler = (data) => {
      dataEvent = data;
      renderCalendar();
      setDataAndRender();
      renderGraph();
      wrapLoaderElem.classList.add('hidden');
      wrapLoaderElem.classList.remove('flex');
    };
    wrapLoaderElem.classList.remove('hidden');
    wrapLoaderElem.classList.add('flex');
    await getWithAuth('user/me/tracker', trackerHandler);

    const ctrlMonthBtnHandler = (type) => {
      month = type == 'NEXT' ? month + 1 : month - 1;

      if (month < 0 || month > 11) {
        date = new Date(year, month, new Date().getDate());
        year = date.getFullYear();
        month = date.getMonth();
      } else {
        date = new Date();
      }

      renderCalendar();
    };

    const ctrlMonthGraphBtnHandler = (type) => {
      monthGraph = type == 'NEXT' ? monthGraph + 1 : monthGraph - 1;

      if (monthGraph < 0 || monthGraph > 11) {
        const updateDate = new Date(yearGraph, monthGraph, new Date().getDate());

        yearGraph = updateDate.getFullYear();
        monthGraph = updateDate.getMonth();
      }

      renderGraph();
    };

    prevMonthBtnElem.addEventListener('click', () => {
      ctrlMonthBtnHandler('PREV');
    });
    nextMonthBtnElem.addEventListener('click', () => {
      ctrlMonthBtnHandler('NEXT');
    });

    prevMonthGraphBtnElem.addEventListener('click', () => {
      ctrlMonthGraphBtnHandler('PREV');
    });
    nextMonthGraphBtnElem.addEventListener('click', () => {
      ctrlMonthGraphBtnHandler('NEXT');
    });
  });
</script>

<div id="wrapTrackerBox" class="max-h-screen w-[480] pb-16 bg-gray-100 text-gray-600">
  <div class="h-full overflow-y-auto w-full py-6 flex flex-col">
    <div
      class="mb-6 px-1.5 xxs:px-2.5 xs:px-4 text-2xl font-oswald font-semibold flex flex-row justify-between"
    >
      <div>Tracker</div>
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

    <!-- Main -->
    <div class="px-1.5 xxs:px-2.5 xs:px-4">
      <!-- Total streak days section -->
      <div
        class="mb-6 p-4 rounded-lg flex flex-row items-center w-full bg-white shadow"
      >
        <div class="flex-1 text-gray-500">
          <div class="text-md mb-1 font-semibold">Total streak days</div>
          <div class="text-sm mb-1">Total number of days you didn't masturbate</div>
          <div class="font-semibold">
            <span
              class="text-3xl mr-1.5 text-gray-500 tracking-tighter"
              id="totalStreakBox"
            ></span><span class="text-lg text-gray-400">days</span>
          </div>
        </div>
        <div class="fill-lime-400 ml-4">
          <svg
            class="w-10 h-10"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 448 512"
            ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
              d="M128 0c13.3 0 24 10.7 24 24V64H296V24c0-13.3 10.7-24 24-24s24 10.7 24 24V64h40c35.3 0 64 28.7 64 64v16 48V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V192 144 128C0 92.7 28.7 64 64 64h40V24c0-13.3 10.7-24 24-24zM400 192H48V448c0 8.8 7.2 16 16 16H384c8.8 0 16-7.2 16-16V192zM329 297L217 409c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47 95-95c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"
            /></svg
          >
        </div>
      </div>

      <!-- Calendar section -->
      <div class="mb-6 pb-1 flex flex-col w-full bg-white rounded-lg shadow">
        <div class="py-3.5 px-4 border-b flex flex-row items-center w-full">
          <div
            id="prevMonthBtn"
            class="fill-gray-500 p-2 rounded-full hover:bg-gray-100 cursor-pointer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              viewBox="0 0 320 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256 246.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"
              /></svg
            >
          </div>
          <div
            id="currMonthYearBox"
            class="flex-1 text-center text-md font-semibold text-gray-500 cursor-default"
          ></div>
          <div
            id="nextMonthBtn"
            class="fill-gray-500 p-2 rounded-full hover:bg-gray-100 cursor-pointer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              viewBox="0 0 320 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M310.6 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L242.7 256 73.4 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"
              /></svg
            >
          </div>
        </div>
        <div
          class="px-2 py-2.5 grid grid-cols-7 gap-2 items-center justify-between w-full text-xs cursor-default font-semibold"
        >
          <div class="text-center">Sun</div>
          <div class="text-center">Mon</div>
          <div class="text-center">Tue</div>
          <div class="text-center">Wed</div>
          <div class="text-center">Thu</div>
          <div class="text-center">Fri</div>
          <div class="text-center">Sat</div>
        </div>
        <div
          id="mainDaysBox"
          class="p-2 mb-3 grid grid-cols-7 gap-3 text-gray-500"
        ></div>
      </div>

      <!-- Your current streak -->
      <div
        class="mb-6 p-4 rounded-lg flex flex-row items-center w-full bg-white shadow"
      >
        <div class="flex-1 text-gray-500">
          <div class="text-md mb-1 font-semibold">Your current streak</div>
          <div class="text-sm mb-1">
            Consecutive number of days you didn't masturbate in which includes yesterday
          </div>
          <div class="font-semibold">
            <span
              class="text-3xl mr-1.5 text-gray-500 tracking-tighter"
              id="currStreakBox"
            ></span><span class="text-lg text-gray-400">days</span>
          </div>
        </div>
        <div class="fill-amber-400 ml-4">
          <svg
            class="w-10 h-10"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 448 512"
            ><!--! Font Awesome Pro 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
              d="M159.3 5.4c7.8-7.3 19.9-7.2 27.7 .1c27.6 25.9 53.5 53.8 77.7 84c11-14.4 23.5-30.1 37-42.9c7.9-7.4 20.1-7.4 28 .1c34.6 33 63.9 76.6 84.5 118c20.3 40.8 33.8 82.5 33.8 111.9C448 404.2 348.2 512 224 512C98.4 512 0 404.1 0 276.5c0-38.4 17.8-85.3 45.4-131.7C73.3 97.7 112.7 48.6 159.3 5.4zM225.7 416c25.3 0 47.7-7 68.8-21c42.1-29.4 53.4-88.2 28.1-134.4c-4.5-9-16-9.6-22.5-2l-25.2 29.3c-6.6 7.6-18.5 7.4-24.7-.5c-16.5-21-46-58.5-62.8-79.8c-6.3-8-18.3-8.1-24.7-.1c-33.8 42.5-50.8 69.3-50.8 99.4C112 375.4 162.6 416 225.7 416z"
            /></svg
          >
        </div>
      </div>

      <!-- Stats best streak and total task done -->
      <div class="mb-6 grid grid-cols-2 gap-4 w-full">
        <div class="p-2 rounded-lg bg-white shadow flex flex-col items-center">
          <div class="fill-rose-400 py-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-10 h-10"
              viewBox="0 0 512 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M64 64c0-17.7-14.3-32-32-32S0 46.3 0 64V400c0 44.2 35.8 80 80 80H480c17.7 0 32-14.3 32-32s-14.3-32-32-32H80c-8.8 0-16-7.2-16-16V64zm406.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L320 210.7l-57.4-57.4c-12.5-12.5-32.8-12.5-45.3 0l-112 112c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L240 221.3l57.4 57.4c12.5 12.5 32.8 12.5 45.3 0l128-128z"
              /></svg
            >
          </div>
          <div class="font-semibold mb-1">
            <span
              class="text-3xl mr-1.5 text-gray-500 tracking-tighter"
              id="bestStreakBox"
            ></span><span class="text-lg text-gray-400">days</span>
          </div>
          <div class="text-sm mb-2">Best streak</div>
        </div>
        <div class="p-2 rounded-lg bg-white shadow flex flex-col items-center">
          <div class="fill-purple-400 py-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-10 h-10"
              viewBox="0 0 512 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M152.1 38.2c9.9 8.9 10.7 24 1.8 33.9l-72 80c-4.4 4.9-10.6 7.8-17.2 7.9s-12.9-2.4-17.6-7L7 113C-2.3 103.6-2.3 88.4 7 79s24.6-9.4 33.9 0l22.1 22.1 55.1-61.2c8.9-9.9 24-10.7 33.9-1.8zm0 160c9.9 8.9 10.7 24 1.8 33.9l-72 80c-4.4 4.9-10.6 7.8-17.2 7.9s-12.9-2.4-17.6-7L7 273c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l22.1 22.1 55.1-61.2c8.9-9.9 24-10.7 33.9-1.8zM224 96c0-17.7 14.3-32 32-32H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H256c-17.7 0-32-14.3-32-32zm0 160c0-17.7 14.3-32 32-32H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H256c-17.7 0-32-14.3-32-32zM160 416c0-17.7 14.3-32 32-32H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H192c-17.7 0-32-14.3-32-32zM48 368a48 48 0 1 1 0 96 48 48 0 1 1 0-96z"
              /></svg
            >
          </div>
          <div
            class="font-semibold mb-1 text-3xl mr-1.5 text-gray-500 tracking-tight"
            id="totalTaskDoneBox"
          ></div>
          <div class="text-sm mb-2">Total task done</div>
        </div>
      </div>

      <!-- Task completion graph -->
      <div class="p-4 bg-white rounded-lg shadow flex flex-col text-gray-500">
        <div class="pb-4 flex flex-row items-center w-full">
          <div
            id="prevMonthGraphBtn"
            class="fill-gray-500 p-2 rounded-full hover:bg-gray-100 cursor-pointer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              viewBox="0 0 320 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M9.4 233.4c-12.5 12.5-12.5 32.8 0 45.3l192 192c12.5 12.5 32.8 12.5 45.3 0s12.5-32.8 0-45.3L77.3 256 246.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0l-192 192z"
              /></svg
            >
          </div>
          <div
            class="flex-1 flex flex-col items-center text-center text-md font-semibold text-gray-500 cursor-default"
          >
            <div class="text-center font-semibold mb-1">Task completion graph</div>
            <div id="currMonthYearGraphBox" class="text-sm"></div>
          </div>
          <div
            id="nextMonthGraphBtn"
            class="fill-gray-500 p-2 rounded-full hover:bg-gray-100 cursor-pointer"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="w-4 h-4"
              viewBox="0 0 320 512"
              ><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><path
                d="M310.6 233.4c12.5 12.5 12.5 32.8 0 45.3l-192 192c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L242.7 256 73.4 86.6c-12.5-12.5-12.5-32.8 0-45.3s32.8-12.5 45.3 0l192 192z"
              /></svg
            >
          </div>
        </div>
        <div class="relative mb-12 flex flex-col">
          <div class="flex flex-row items-center">
            <div class="text-xs mr-2 w-8 text-center">100%</div>
            <div class="h-0.5 bg-gray-200 w-full"></div>
          </div>
          <div class="h-5 w-full"></div>
          <div class="flex flex-row items-center">
            <div class="text-xs mr-2 w-8 text-center">75%</div>
            <div class="h-0.5 bg-gray-200 w-full"></div>
          </div>
          <div class="h-5 w-full"></div>
          <div class="flex flex-row items-center">
            <div class="text-xs mr-2 w-8 text-center">50%</div>
            <div class="h-0.5 bg-gray-200 w-full"></div>
          </div>
          <div class="h-5 w-full"></div>
          <div class="flex flex-row items-center">
            <div class="text-xs mr-2 w-8 text-center">25%</div>
            <div class="h-0.5 bg-gray-200 w-full"></div>
          </div>
          <div class="h-5 w-full"></div>
          <div class="flex flex-row items-center">
            <div class="text-xs mr-2 w-8 text-center">0%</div>
            <div class="h-0.5 bg-gray-200 w-full"></div>
          </div>
          <div class="h-full bottom-0 left-0 absolute w-full pl-8 xs:pr-8">
            <div class="flex flex-row items-end justify-center h-full w-full py-2">
              <div
                id="barTaskExeBox"
                class="relative bg-amber-400 w-12 xxs:w-14 xs:w-16 mr-5 flex flex-col"
                style=""
              >
                <div
                  class="text-xs absolute -top-4 w-full text-center text-gray-500"
                  id="percentTaskExeBox"
                ></div>
                <div
                  class="absolute -bottom-14 left-0 flex flex-col items-center justify-center w-full text-xs"
                >
                  <div class="text-2xl">💪</div>
                  <div>Exercise</div>
                </div>
              </div>
              <div
                id="barTaskMedBox"
                class="relative bg-rose-400 w-12 xxs:w-14 xs:w-16 mr-5 flex flex-col"
                style=""
              >
                <div
                  class="text-xs absolute -top-4 w-full text-center text-gray-500"
                  id="percentTaskMedBox"
                ></div>
                <div
                  class="absolute -bottom-14 left-0 flex flex-col items-center justify-center w-full text-xs"
                >
                  <div class="text-2xl">🧘</div>
                  <div>Meditation</div>
                </div>
              </div>
              <div
                id="barTaskReadBox"
                class="relative bg-purple-400 w-12 xxs:w-14 xs:w-16 flex flex-col"
                style=""
              >
                <div
                  class="text-xs absolute -top-4 w-full text-center text-gray-500"
                  id="percentTaskReadBox"
                ></div>
                <div
                  class="absolute -bottom-14 left-0 flex flex-col items-center justify-center w-full text-xs"
                >
                  <div class="text-2xl">🧠</div>
                  <div>Reading</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
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
  <div class="mt-3 font-semibold text-xl font-oswald text-white"></div>
</div>
