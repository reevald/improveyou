<script>
  import { page } from '$app/stores';
  import { onMount } from 'svelte';

  const duration = $page.url.searchParams.get('sec') || null;
  const formatDuration = (dur) => {
    // Reference: https://stackoverflow.com/a/37096512
    const d = Number(dur);
    const h = Math.floor(d / 3600);
    const m = Math.floor((d % 3600) / 60);
    const s = Math.floor((d % 3600) % 60);
    const hDisplay =
      h > 0 ? h + (h == 1 ? ' hr' : ' hrs') + (m > 0 || s > 0 ? ', ' : '') : '';
    const mDisplay = m > 0 ? m + (m == 1 ? ' min' : ' mins') + (s > 0 ? ', ' : '') : '';
    const sDisplay = s > 0 ? s + (s == 1 ? ' sec' : ' secs') : '';
    return hDisplay + mDisplay + sDisplay;
  };
  onMount(() => {
    document.getElementById('secBox').innerText = duration
      ? ` expected available in ${formatDuration(duration)},`
      : '';
  });
</script>

<div class="flex flex-row justify-center items-center max-h-screen h-screen p-3">
  <div class="flex flex-col items-center max-w-sm w-full">
    <div class="mb-6 text-2xl font-oswald text-center">
      [Error 429]<br />Too Many Requests
    </div>
    <div class="mb-6 flex flex-row w-full justify-center">
      <img src="./icon/undraw_warning_re_eoyh.svg" alt="Warning" />
    </div>
    <div class="text-lg font-oswald mb-4 text-center">
      Request was throttled,<span id="secBox"></span> please try again later.
    </div>
  </div>
</div>
