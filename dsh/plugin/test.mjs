import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, chmod, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { apply } from './index.js';

async function makeTrellisRoot(currentTask) {
  const root = await mkdtemp(join(tmpdir(), 'wxh-gate-fixture-'));
  const scripts = join(root, '.trellis', 'scripts');
  await mkdir(scripts, { recursive: true });
  const taskPy = join(scripts, 'task.py');
  await writeFile(taskPy, `#!/usr/bin/env python3\nimport json\nprint(json.dumps({"current_task": ${JSON.stringify(currentTask)}}))\n`);
  await chmod(taskPy, 0o755);
  return root;
}

const activeRoot = await makeTrellisRoot({ dir: '.trellis/tasks/demo', id: 'demo', status: 'in_progress' });
const noTaskRoot = await makeTrellisRoot(null);
let workingDirectory = activeRoot;
const handlers = new Map();
const ctx = {
  on(event, handler) {
    handlers.set(event, handler);
    return () => {};
  },
  get(name) {
    if (name === 'workingDirectory') return { ensure: async () => workingDirectory };
    return undefined;
  },
  logger: { warn: (...args) => console.error('[warn]', ...args) },
};

apply(ctx, { gate: true, steer: true });

const pre = handlers.get('tools/pre-execute');
assert.ok(pre, 'tools/pre-execute handler registered');
const post = handlers.get('agent/pre-step');
assert.ok(post, 'agent/pre-step handler registered');

const execution = (sessionId, command = 'git commit -m test') => ({
  name: 'bash',
  arguments: { command },
  agent: { session: { header: { id: sessionId } } },
  signal: new AbortController().signal,
});

let allowed = false;
const allowDecision = await pre(execution('active-session'), async () => {
  allowed = true;
  return { kind: 'allow' };
});
assert.equal(allowed, true, 'active task should be allowed');
assert.equal(allowDecision.kind, 'allow');

let deniedNext = false;
workingDirectory = noTaskRoot;
const denied = await pre(execution('no-task-session'), async () => {
  deniedNext = true;
  return { kind: 'allow' };
});
assert.equal(deniedNext, false, 'denied commit must not call next');
assert.equal(denied.kind, 'deny');
assert.match(denied.reason, /Trellis/);

let nonCommitNext = false;
await pre(execution('no-task-session', 'echo hello'), async () => {
  nonCommitNext = true;
  return { kind: 'allow' };
});
assert.equal(nonCommitNext, true, 'non-commit command should pass through');

const original = { id: 'user-message', role: 'user', content: [{ type: 'text', text: 'hi' }], source: { kind: 'user' } };
const steered = await post({ agent: {}, messages: [original], signal: new AbortController().signal }, async () => ({
  kind: 'enter',
  messages: [original],
}));
assert.equal(steered.messages.length, 2, 'steer message appended');
assert.match(steered.messages[1].content[0].text, /<wxh-steer>/);
assert.match(steered.messages[1].content[0].text, /验证针对后果/);

await rm(activeRoot, { recursive: true, force: true });
await rm(noTaskRoot, { recursive: true, force: true });
console.log('plugin tests passed');
