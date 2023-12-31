// import adapter from '@sveltejs/adapter-static';

// /** @type {import('@sveltejs/kit').Config} */
// const config = {
//   kit: {
//     // adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
//     // If your environment is not supported or you settled on a specific environment, switch out the adapter.
//     // See https://kit.svelte.dev/docs/adapters for more information about adapters.
//     adapter: adapter({
//       pages: 'build',
//       assets: 'build',
//       precompress: false,
//       strict: true,
//       fallback: '200.html'
//     })
//   }
// };

// export default config;
import adapter from '@sveltejs/adapter-vercel';

export default {
  kit: {
    adapter: adapter({
      runtime: 'nodejs18.x'
    })
  }
};
