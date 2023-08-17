<script>
  /** @type {import('./$types').PageData} */
  export let data;
</script>

<h1>{data.post.title}</h1>
<div>Content: {@html data.post.content}</div>

<h1>Confirm-email page w/ magic link</h1>
