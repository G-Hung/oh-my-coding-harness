const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
function local(relative, inspectSymlinks = true) {
  if (typeof relative !== 'string' || !relative || path.isAbsolute(relative)) throw new Error(`Expected relative path: ${relative}`);
  const absolute = path.resolve(root, relative);
  if (absolute !== root && !absolute.startsWith(root + path.sep)) throw new Error(`Path escapes root: ${relative}`);
  let current = root;
  for (const part of path.relative(root, absolute).split(path.sep).filter(Boolean)) {
    current = path.join(current, part);
    if (inspectSymlinks && fs.existsSync(current) && fs.lstatSync(current).isSymbolicLink()) throw new Error(`Symlink is outside scan policy: ${relative}`);
  }
  return absolute;
}
function config() {
  const value = require(local('harness.config.cjs'));
  for (const key of ['sourceRoots', 'markdownRoots', 'extensions', 'exclude', 'checks']) {
    if (!Array.isArray(value[key]) || value[key].some(x => typeof x !== 'string' || !x) || (key !== 'exclude' && !value[key].length)) throw new Error(`Invalid config: ${key}`);
  }
  for (const relative of [...value.sourceRoots, ...value.markdownRoots]) local(relative);
  for (const relative of value.exclude) local(relative, false);
  if (value.extensions.some(x => !/^\.[a-z]+$/.test(x))) throw new Error('Invalid extensions: use final lowercase suffixes such as .ts, .vue, or .svelte; .d.ts is matched as .ts');
  if (!Number.isInteger(value.maxLines) || value.maxLines < 1) throw new Error('maxLines must be a positive integer');
  return value;
}
function excluded(file, cfg) { return cfg.exclude.some(x => file === x || file.startsWith(x + '/')); }
function walk(roots, cfg) {
  const found = new Set();
  function visit(relative) {
    const normalized = relative.split(path.sep).join('/');
    if (excluded(normalized, cfg)) return;
    const absolute = local(relative);
    const stat = fs.lstatSync(absolute);
    if (stat.isDirectory()) {
      for (const name of fs.readdirSync(absolute).sort()) visit(path.join(relative, name));
    } else if (stat.isFile()) found.add(normalized);
  }
  roots.forEach(visit);
  return [...found].sort();
}
function source(file, cfg) {
  return !excluded(file, cfg) && cfg.sourceRoots.some(x => x === '.' || file === x || file.startsWith(x + '/')) && cfg.extensions.includes(path.extname(file));
}
function sourceFiles(cfg) {
  const files = walk(cfg.sourceRoots, cfg).filter(file => source(file, cfg));
  if (!files.length) throw new Error('No source files found; check sourceRoots and exclusions');
  return files;
}
function cli(main) {
  Promise.resolve().then(main).then(code => { process.exitCode = code || 0; }).catch(error => { console.error(error.message); process.exitCode = 1; });
}
module.exports = { root, local, config, walk, source, sourceFiles, cli };
