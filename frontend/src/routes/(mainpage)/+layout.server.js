export const ssr = false;
export function load({ url }) {
  return {
    isPageHome: url.pathname.startsWith('/home'),
    isPageActivity:
      url.pathname.startsWith('/activities') || url.pathname.startsWith('/activity'),
    isPageLeaderboard: url.pathname.startsWith('/leaderboard'),
    isPageTracker: url.pathname.startsWith('/tracker')
  };
}
// console.log('[page server signup] Its run server?');
