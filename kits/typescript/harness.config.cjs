// TODO: adapt these roots, exclusions and limit to your project. Paths are root-relative.
module.exports = {
  sourceRoots: ['src', 'scripts'],
  markdownRoots: ['.'],
  extensions: ['.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs', '.mts', '.cts'],
  // TODO: document why each additional exclusion is appropriate; no glob syntax.
  exclude: ['node_modules', '.git', 'coverage', '.cache', 'dist'],
  maxLines: 500,
  // TODO: add required integration checks here once they exist. Commands must be npm script names.
  checks: ['lint', 'typecheck', 'test', 'test:harness', 'check:loc', 'check:links'],
};
