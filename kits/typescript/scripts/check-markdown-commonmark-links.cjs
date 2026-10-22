const fs = require('node:fs');
const path = require('node:path');
const { local, config, walk, cli } = require('./lib/project.cjs');
// Check local CommonMark inline and reference links with unified and remark-parse.
async function main() {
  if (process.argv.length > 2) throw new Error('No arguments expected');
  const { unified } = await import('unified');
  const { default: remarkParse } = await import('remark-parse');
  const cfg = config(), files = walk(cfg.markdownRoots, cfg).filter(x => /\.md$/i.test(x));
  if (!files.length) throw new Error('No Markdown files found');
  let failures = 0, checked = 0;
  for (const file of files) {
    const tree = unified().use(remarkParse).parse(fs.readFileSync(local(file), 'utf8'));
    const definitions = new Map();
    function gather(node) {
      if (node.type === 'definition') definitions.set(node.identifier, node.url);
      for (const child of node.children || []) gather(child);
    }
    gather(tree);
    function visit(node) {
      let url = ['link', 'image'].includes(node.type) ? node.url : undefined;
      if (['linkReference', 'imageReference'].includes(node.type)) url = definitions.get(node.identifier);
      if (url && !/^[a-z][a-z\d+.-]*:|^\/\/|^#/i.test(url)) {
        try {
          const target = decodeURIComponent(url.split(/[?#]/)[0]);
          if (target) {
            const relative = target.startsWith('/') ? target.slice(1) : path.join(path.dirname(file), target);
            if (!fs.existsSync(local(relative))) throw new Error('target missing');
            checked++;
          }
        } catch (error) { failures++; console.error(`${JSON.stringify(file)}:${node.position.start.line}: ${JSON.stringify(url)}: ${error.message}`); }
      }
      for (const child of node.children || []) visit(child);
    }
    visit(tree);
  }
  console.log(`Checked ${checked} local link targets across ${files.length} Markdown files; ${failures} broken. Anchors, HTML and remote URLs are not checked.`);
  return failures ? 1 : 0;
}
if (require.main === module) cli(main);
