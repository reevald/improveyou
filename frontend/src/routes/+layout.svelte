<script lang="ts">
  import '../app.css';
</script>

<svelte:head>
  <link
    href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&family=Oswald&display=swap"
    rel="stylesheet"
  />
  <style>
    ::-webkit-scrollbar {
      height: 10px;
      width: 10px;
    }
    ::-webkit-scrollbar-track {
      background-color: #e5e7eb;
      border-radius: 20px;
    }
    ::-webkit-scrollbar-thumb {
      background-color: #d1d5db;
      border-radius: 20px;
    }
  </style>
</svelte:head>
<slot />
