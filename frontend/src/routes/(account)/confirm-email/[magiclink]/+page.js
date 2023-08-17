/** @type {import('./$types').PageLoad} */

export function load({ params }) {
  return {
    post: {
      title: `Title for ${params.magiclink} goes here`,
      content: `Content for ${params.magiclink} goes here`
    }
  };
}
