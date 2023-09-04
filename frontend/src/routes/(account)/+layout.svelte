<svelte:head>
  <style>
    .input-group {
      position: relative;
    }
    .input-group label {
      position: absolute;
      bottom: 50%;
      transform-origin: 0 0;
      transform: translateY(100%);
      transition: transform 0.2s linear;
    }
    .input-group label.animate-label {
      top: -20px;
      height: fit-content;
      transform: scale(0.8) translateY(0%);
      transition: transform 0.2s linear;
    }
    .input-group input {
      /* padding-top: 20px; */
      width: 100%;
      box-sizing: border-box;
    }

    /* Disclaimer, source: https://codepen.io/matchboxhero/pen/RLebOY */
    .bird {
      background-image: url(https://s3-us-west-2.amazonaws.com/s.cdpn.io/174479/bird-cells-new.svg);
      background-size: auto 100%;
      width: 88px;
      height: 125px;
      will-change: background-position;
      -webkit-animation-name: fly-cycle;
      animation-name: fly-cycle;
      -webkit-animation-timing-function: steps(10);
      animation-timing-function: steps(10);
      -webkit-animation-iteration-count: infinite;
      animation-iteration-count: infinite;
    }
    .bird--one {
      -webkit-animation-duration: 1s;
      animation-duration: 1s;
      -webkit-animation-delay: -0.5s;
      animation-delay: -0.5s;
    }
    .bird--two {
      -webkit-animation-duration: 0.9s;
      animation-duration: 0.9s;
      -webkit-animation-delay: -0.75s;
      animation-delay: -0.75s;
    }
    .bird--three {
      -webkit-animation-duration: 1.25s;
      animation-duration: 1.25s;
      -webkit-animation-delay: -0.25s;
      animation-delay: -0.25s;
    }
    .bird--four {
      -webkit-animation-duration: 1.1s;
      animation-duration: 1.1s;
      -webkit-animation-delay: -0.5s;
      animation-delay: -0.5s;
    }

    .bird-container {
      position: absolute;
      top: 20%;
      left: -10%;
      transform: scale(0) translateX(-10vw);
      will-change: transform;
      -webkit-animation-name: fly-right-one;
      animation-name: fly-right-one;
      -webkit-animation-timing-function: linear;
      animation-timing-function: linear;
      -webkit-animation-iteration-count: infinite;
      animation-iteration-count: infinite;
    }
    .bird-container--one {
      -webkit-animation-duration: 15s;
      animation-duration: 15s;
      -webkit-animation-delay: 0;
      animation-delay: 0;
    }
    .bird-container--two {
      -webkit-animation-duration: 16s;
      animation-duration: 16s;
      -webkit-animation-delay: 1s;
      animation-delay: 1s;
    }
    .bird-container--three {
      -webkit-animation-duration: 14.6s;
      animation-duration: 14.6s;
      -webkit-animation-delay: 9.5s;
      animation-delay: 9.5s;
    }
    .bird-container--four {
      -webkit-animation-duration: 16s;
      animation-duration: 16s;
      -webkit-animation-delay: 10.25s;
      animation-delay: 10.25s;
    }

    @-webkit-keyframes fly-cycle {
      100% {
        background-position: -900px 0;
      }
    }

    @keyframes fly-cycle {
      100% {
        background-position: -900px 0;
      }
    }
    @-webkit-keyframes fly-right-one {
      0% {
        transform: scale(0.3) translateX(-10vw);
      }
      10% {
        transform: translateY(2vh) translateX(10vw) scale(0.4);
      }
      20% {
        transform: translateY(0vh) translateX(30vw) scale(0.5);
      }
      30% {
        transform: translateY(4vh) translateX(50vw) scale(0.6);
      }
      40% {
        transform: translateY(2vh) translateX(70vw) scale(0.6);
      }
      50% {
        transform: translateY(0vh) translateX(90vw) scale(0.6);
      }
      60% {
        transform: translateY(0vh) translateX(110vw) scale(0.6);
      }
      100% {
        transform: translateY(0vh) translateX(110vw) scale(0.6);
      }
    }
    @keyframes fly-right-one {
      0% {
        transform: scale(0.3) translateX(-10vw);
      }
      10% {
        transform: translateY(2vh) translateX(10vw) scale(0.4);
      }
      20% {
        transform: translateY(0vh) translateX(30vw) scale(0.5);
      }
      30% {
        transform: translateY(4vh) translateX(50vw) scale(0.6);
      }
      40% {
        transform: translateY(2vh) translateX(70vw) scale(0.6);
      }
      50% {
        transform: translateY(0vh) translateX(90vw) scale(0.6);
      }
      60% {
        transform: translateY(0vh) translateX(110vw) scale(0.6);
      }
      100% {
        transform: translateY(0vh) translateX(110vw) scale(0.6);
      }
    }
    @-webkit-keyframes fly-right-two {
      0% {
        transform: translateY(-2vh) translateX(-10vw) scale(0.5);
      }
      10% {
        transform: translateY(0vh) translateX(10vw) scale(0.4);
      }
      20% {
        transform: translateY(-4vh) translateX(30vw) scale(0.6);
      }
      30% {
        transform: translateY(1vh) translateX(50vw) scale(0.45);
      }
      40% {
        transform: translateY(-2.5vh) translateX(70vw) scale(0.5);
      }
      50% {
        transform: translateY(0vh) translateX(90vw) scale(0.45);
      }
      51% {
        transform: translateY(0vh) translateX(110vw) scale(0.45);
      }
      100% {
        transform: translateY(0vh) translateX(110vw) scale(0.45);
      }
    }
    @keyframes fly-right-two {
      0% {
        transform: translateY(-2vh) translateX(-10vw) scale(0.5);
      }
      10% {
        transform: translateY(0vh) translateX(10vw) scale(0.4);
      }
      20% {
        transform: translateY(-4vh) translateX(30vw) scale(0.6);
      }
      30% {
        transform: translateY(1vh) translateX(50vw) scale(0.45);
      }
      40% {
        transform: translateY(-2.5vh) translateX(70vw) scale(0.5);
      }
      50% {
        transform: translateY(0vh) translateX(90vw) scale(0.45);
      }
      51% {
        transform: translateY(0vh) translateX(110vw) scale(0.45);
      }
      100% {
        transform: translateY(0vh) translateX(110vw) scale(0.45);
      }
    }
  </style>
</svelte:head>

<!-- <div class="bg-red-900">[Begin] account layout</div>
<slot />
<div class="bg-red-900">[End] account layout</div> -->

<div class="h-screen w-screen">
  <div
    class="absolute min-h-screen h-full w-full bg-[url('/sprite-default/background/0_Background.png')] bg-cover blur-sm"
  />
  <div
    class="relative overflow-x-hidden flex flex-row justify-center items-center bg-gradient-radial from-sky-950/10 via-sky-950/70 to-sky-950 min-h-screen h-full w-full"
  >
    <div class="bird-container bird-container--one z-10 invisible sm:visible">
      <div class="bird bird--one" />
    </div>
    <div class="bird-container bird-container--two z-30 invisible sm:visible">
      <div class="bird bird--two" />
    </div>
    <div class="bird-container bird-container--three z-10 invisible sm:visible">
      <div class="bird bird--three" />
    </div>
    <div class="bird-container bird-container--four z-30 invisible sm:visible">
      <div class="bird bird--four" />
    </div>
    <slot />
  </div>
</div>
