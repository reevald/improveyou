module.exports = {
  root: true,
  extends: ['eslint:recommended', 'plugin:svelte/recommended', 'prettier'],
  parserOptions: {
    sourceType: 'module',
    ecmaVersion: 'latest',
    extraFileExtensions: ['.svelte']
  },
  env: {
    browser: true,
    es2021: true,
    node: true
  }
};
