const js = require('@eslint/js');
const ts = require('typescript-eslint');
const globals = require('globals');
module.exports = ts.config(
  { ignores: ['node_modules/**', '.cache/**', 'coverage/**', 'dist/**'] },
  js.configs.recommended,
  { files: ['**/*.cjs'], languageOptions: { globals: globals.node, sourceType: 'commonjs' } },
  ...ts.configs.recommended.map(item => ({ ...item, files: ['src/**/*.ts'] })),
  { files: ['src/**/*.test.ts'], languageOptions: { globals: globals.jest } },
);
