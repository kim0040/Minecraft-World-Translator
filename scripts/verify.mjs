// Opt-in verification with conservative source fingerprints. Never imports old PASS claims.
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, mkdirSync, renameSync, writeFileSync, openSync, closeSync, unlinkSync } from 'node:fs';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn, spawnSync } from 'node:child_process';
import { release } from 'node:os';

const root = resolve(fileURLToPath(new URL('..', import.meta.url)));
const python = process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python';
const ci = readFileSync(resolve(root, '.github/workflows/ci.yml'), 'utf8');
const pythonTests = [...new Set([...ci.matchAll(/(?:run:\s*|^\s+)python ((?:tests\/)?[\w-]+\.py)/gm)].map(m => m[1]))];
const profiles = {
  check: [['pnpm', 'check']],
  frontend: [['pnpm', 'test:frontend']],
  'browser-smoke': [['pnpm', 'exec', 'playwright', 'test', '--grep', 'filter counts follow|Enter opens candidate|model preserves scan|result-partial explains|OpenRouter usage reads|settings save shows pending']],
  'browser-layout': [['pnpm', 'exec', 'playwright', 'test', 'tests/browser/layout.spec.ts']],
  'browser-final': [['pnpm', 'test:browser']],
  'python-final': pythonTests.map(file => [python, file]),
  'rust-final': [['cargo', 'test', '--locked', '--offline', '--manifest-path', 'src-tauri/Cargo.toml', '--lib']],
};
const args = process.argv.slice(2);
const names = args.filter(arg => !arg.startsWith('--'));
if (!names.length || names.some(name => !Object.hasOwn(profiles, name)) || args.some(arg => arg.startsWith('--') && !['--run', '--force'].includes(arg))) {
  process.stderr.write('Usage: node scripts/verify.mjs <profile...> [--run] [--force]\nProfiles: ' + Object.keys(profiles).join(', ') + '\nDefault is plan only; --run executes. No native build or paid API is included.\n');
  process.exit(2);
}
const cacheDir = resolve(root, 'output/verification');
const cacheFile = resolve(cacheDir, 'evidence.json');
let evidence = {};
try { evidence = JSON.parse(readFileSync(cacheFile, 'utf8')); } catch { /* No verified evidence yet. */ }
if (args.includes('--run')) {
  mkdirSync(cacheDir, { recursive: true });
  const lock = resolve(cacheDir, 'run.lock');
  try { const fd = openSync(lock, 'wx'); writeFileSync(fd, String(process.pid)); closeSync(fd); }
  catch { throw new Error('Another verification owns output/verification/run.lock. Inspect its PID before clearing a stale lock.'); }
  process.on('exit', () => { try { unlinkSync(lock); } catch { /* Already removed. */ } });
}
function saveEvidence() {
  mkdirSync(cacheDir, { recursive: true });
  writeFileSync(cacheFile + '.tmp', JSON.stringify(evidence, null, 2));
  renameSync(cacheFile + '.tmp', cacheFile);
}

function inputs(name) {
  const listed = spawnSync('git', ['ls-files', '-z', '--cached', '--others', '--exclude-standard'], { cwd: root, encoding: 'utf8' });
  if (listed.status !== 0) throw new Error('Cannot inventory verification inputs');
  const common = ['scripts/verify.mjs', 'package.json', 'pnpm-lock.yaml'];
  const paths = listed.stdout.split('\0').filter(file => {
    if (common.includes(file)) return true;
    if (name === 'python-final') return file.endsWith('.py') || ['requirements.txt', '.github/workflows/ci.yml'].includes(file);
    if (name === 'rust-final') return /^src-tauri\/(src\/|Cargo\.|tauri\.conf\.json|capabilities\/)/.test(file);
    if (/^(src\/|public\/)/.test(file) || /^(vite|playwright|tsconfig).*\.(ts|json)$/.test(file)) return true;
    if (name === 'frontend') return file.startsWith('tests/frontend/');
    if (name.startsWith('browser-')) return file.startsWith('tests/browser/') || ['tests/frontend/tauri-fixture-init.js', 'tests/frontend/preview.html'].includes(file);
    return false;
  });
  if (name === 'python-final') paths.push('.venv/pyvenv.cfg');
  const hash = createHash('sha256');
  for (const file of [...new Set(paths)].sort()) {
    hash.update(file + '\0');
    hash.update(existsSync(resolve(root, file)) ? readFileSync(resolve(root, file)) : '<missing>');
  }
  hash.update(JSON.stringify(profiles[name]));
  hash.update(JSON.stringify([process.platform, process.arch, process.version, release(), process.env.CI || '']));
  return hash.digest('hex');
}

function toolchain(name) {
  const commands = name === 'python-final' ? [[python, '-c', 'import sys,importlib.metadata as m,json;print(sys.version);print(json.dumps(sorted((d.metadata["Name"],d.version) for d in m.distributions())))']] : name === 'rust-final' ? [['rustc', '-vV'], ['cargo', '--version']] : [['pnpm', '--version']];
  return commands.map(([command, ...argv]) => {
    const result = spawnSync(command, argv, { cwd: root, encoding: 'utf8' });
    if (result.status !== 0) throw new Error('Verification tool unavailable: ' + command);
    return result.stdout.trim() + result.stderr.trim();
  }).join('\n');
}

let active;
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => {
  if (active?.pid) {
    try { process.platform === 'win32' ? active.kill(signal) : process.kill(-active.pid, signal); } catch { /* Already stopped. */ }
  }
  process.exit(signal === 'SIGINT' ? 130 : 143);
});

function run(command) {
  return new Promise((done, reject) => {
    const [executable, ...argv] = command;
    active = spawn(executable, argv, { cwd: root, stdio: 'inherit', shell: false, detached: process.platform !== 'win32' });
    active.on('error', reject);
    active.on('close', code => { active = undefined; done(code ?? 1); });
  });
}

for (const name of names) {
  const fingerprint = inputs(name);
  if (!args.includes('--run')) {
    process.stdout.write(`[PLAN] ${name}: ${profiles[name].map(command => command.join(' ')).join('\n  ')}\n`);
    process.stdout.write(`  inputs ${fingerprint.slice(0, 12)}; previous ${evidence[name]?.status || 'NOT RUN'} (toolchain checked only with --run)\n`);
    continue;
  }
  const tools = toolchain(name);
  const previous = evidence[name];
  const fresh = previous && Date.now() - Date.parse(previous.finishedAt) < 24 * 60 * 60 * 1000;
  if (!args.includes('--force') && previous?.status === 'PASS' && previous.fingerprint === fingerprint && previous.toolchain === tools && fresh) {
    process.stdout.write(`[REUSED PASS] ${name}, ${previous.finishedAt}, ${previous.seconds}s. No command rerun.\n`);
    continue;
  }
  const start = Date.now();
  evidence[name] = { status: 'RUNNING', fingerprint, toolchain: tools, finishedAt: null };
  saveEvidence();
  let code = 0;
  try { for (const command of profiles[name]) { code = await run(command); if (code) break; } } catch { code = 1; }
  const unchanged = inputs(name) === fingerprint;
  evidence[name] = { status: code === 0 && unchanged ? 'PASS' : 'FAIL', fingerprint, toolchain: tools, finishedAt: new Date().toISOString(), seconds: (Date.now() - start) / 1000, reason: unchanged ? '' : 'Inputs changed during execution' };
  saveEvidence();
  process.stdout.write(`[${evidence[name].status}] ${name}: ${evidence[name].seconds}s\n`);
  if (code || !unchanged) process.exit(code || 1);
}
