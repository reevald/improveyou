export const ssr = true;
export function load({ cookies }) {
  cookies.delete('__Secure-refresh-jwt');
  return {
    status: 'success'
  };
}
