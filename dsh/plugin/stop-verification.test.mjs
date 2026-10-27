import assert from 'node:assert/strict';
import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { apply } from './index.js';
import { isMutatingShell, turnMutationState } from './verification.js';

const root = await mkdtemp(join(tmpdir(), 'wxh-stop-verification-fixture-'));
const emptyRoot = await mkdtemp(join(tmpdir(), 'wxh-stop-verification-empty-'));
await mkdir(join(root, 'scripts'));
await writeFile(join(root, 'scripts', 'verify.sh'), `#!/bin/sh
mode=$(cat verify-mode)
echo "verify output: mode=$mode"
echo run >> runs.log
exit "$mode"
`);

const handlers = new Map();
const tools = new Map();
const warnings = [];
let workingDirectory = root;
const ctx = {
  on(event, handler) {
    handlers.set(event, handler);
    return () => {};
  },
  get(name) {
    if (name === 'workingDirectory') return { ensure: async () => workingDirectory };
    return undefined;
  },
  tools: {
    register(definition) {
      tools.set(definition.name, definition);
      return () => {};
    },
    guard() {
      return () => {};
    },
  },
  logger: { warn: (...args) => warnings.push(args.join(' ')) },
};

apply(ctx, {
  gate: false,
  steer: false,
  verification: true,
  requireVerification: false,
  stopVerification: true,
  verificationTimeoutMs: 5000,
  stopVerificationMaxAttempts: 3,
  stopVerificationMaxOutputChars: 12000,
});

const stopping = handlers.get('agent/turn-stopping');
assert.ok(stopping, 'agent/turn-stopping handler registered');
const runChecks = tools.get('run_checks');
assert.ok(runChecks, 'run_checks still registered');

function turnStart(turn = 1) {
  return { type: 'turn/start', data: { turn } };
}

function toolCall(name, args, callId = 'callback', turn = 1) {
  return {
    type: 'tool/call',
    data: { turn, step: 1, callId, name, arguments: JSON.stringify(args) },
  };
}

function toolResult(callId, meta) {
  return {
    type: 'tool/result',
    data: { message: { toolCallId: callId, isError: false }, meta },
  };
}

function makeAgent(events, header = { id: 'stop-session', delegationDepth: 0 }) {
  const steers = [];
  const injects = [];
  const session = {
    header,
    events,
    get seq() {
      return events.length;
    },
    eventAt(seq) {
      return events[seq];
    },
  };
  return {
    session,
    steers,
    injects,
    agent: {
      session,
      steer(message) {
        steers.push(message);
      },
      inject(message) {
        injects.push(message);
      },
    },
  };
}

async function reset(mode = 0) {
  await writeFile(join(root, 'verify-mode'), String(mode));
  await writeFile(join(root, 'runs.log'), '');
}

async function runCount() {
  const text = await readFile(join(root, 'runs.log'), 'utf8');
  return text.split('\n').filter(Boolean).length;
}

for (const command of [
  'git status',
  'git diff --stat',
  'ls -la',
  'npm test',
  'cat file | grep needle',
  'find . -name "*.js"',
]) {
  assert.equal(isMutatingShell(command), false, `read-only: ${command}`);
}
for (const command of [
  'rm -rf build',
  'git commit -m test',
  'git -C repo commit -m test',
  'npm install',
  'echo hello > file.txt',
  'sed -i s/a/b/ file.txt',
  'find . -delete',
  'prettier --write src',
]) {
  assert.equal(isMutatingShell(command), true, `mutating: ${command}`);
}

const mutationEvents = [
  turnStart(1),
  toolCall('bash', { command: 'git status' }, 'call-read'),
  toolCall('bash', { command: 'echo x > y' }, 'call-write'),
  toolCall('edit', { file_path: 'a.txt' }, 'call-edit'),
];
assert.deepEqual(
  turnMutationState({ seq: mutationEvents.length, eventAt: (seq) => mutationEvents[seq] }, 1),
  { mutated: true, lastMutationSeq: 3 },
  'turn mutation state finds the last mutating call',
);
const readOnlyEvents = [turnStart(1), toolCall('bash', { command: 'git status' }, 'call-read')];
assert.deepEqual(
  turnMutationState({ seq: readOnlyEvents.length, eventAt: (seq) => readOnlyEvents[seq] }, 1),
  { mutated: false, lastMutationSeq: -1 },
  'read-only shell calls do not count as mutations',
);

await reset(0);
let fixture = makeAgent([turnStart(1), toolCall('bash', { command: 'git status' }, 'call-read')]);
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 0, 'read-only turn does not run verification');
assert.equal(fixture.steers.length, 0, 'read-only turn does not steer');

await reset(0);
fixture = makeAgent([turnStart(1), toolCall('edit', { file_path: 'a.txt' }, 'call-edit')]);
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 1, 'mutating turn runs verification once');
assert.equal(fixture.steers.length, 0, 'passing verification does not steer');
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 1, 'unchanged mutation state does not rerun verification');

await reset(1);
fixture = makeAgent([turnStart(1), toolCall('edit', { file_path: 'a.txt' }, 'call-edit')]);
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 1, 'failing verification runs once');
assert.equal(fixture.steers.length, 1, 'failing verification steers the model');
assert.match(fixture.steers[0].content[0].text, /自动验证失败/);
assert.match(fixture.steers[0].content[0].text, /verify output: mode=1/);
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 1, 'same mutation state is not retried without a new edit');

fixture.session.events.push(toolCall('edit', { file_path: 'b.txt' }, 'call-edit-2'));
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 2, 'a new edit retries verification');
assert.equal(fixture.steers.length, 2, 'second failure steers again');

fixture.session.events.push(toolCall('edit', { file_path: 'c.txt' }, 'call-edit-3'));
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 3, 'third mutation reaches the retry cap');
assert.match(fixture.steers[2].content[0].text, /最后一次自动验证/);

fixture.session.events.push(toolCall('edit', { file_path: 'd.txt' }, 'call-edit-4'));
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 3, 'cap prevents a fourth verification run');
assert.equal(fixture.steers.length, 3, 'cap prevents a fourth steer');

await reset(0);
const passing = {
  kind: 'checks',
  script: 'scripts/verify.sh',
  cwd: root,
  passed: true,
  exitCode: 0,
  durationMs: 1,
  output: 'ok',
  error: '',
};
const passingMeta = runChecks.output.presentationMeta({}, passing);
fixture = makeAgent([
  turnStart(1),
  toolCall('edit', { file_path: 'a.txt' }, 'call-edit'),
  toolCall('run_checks', {}, 'call-checks'),
  toolResult('call-checks', passingMeta),
]);
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 0, 'fresh run_checks evidence skips stop verification');
assert.equal(fixture.steers.length, 0);

workingDirectory = emptyRoot;
fixture = makeAgent([turnStart(1), toolCall('edit', { file_path: 'a.txt' }, 'call-edit')]);
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(fixture.steers.length, 0, 'missing script does not steer');
assert.equal(fixture.injects.length, 1, 'missing script injects one notice');
assert.match(fixture.injects[0].content[0].text, /自动验证已跳过/);
assert.ok(warnings.some((warning) => /not found/.test(warning)), 'missing script is logged');
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(fixture.injects.length, 1, 'missing-script notice is emitted once');
workingDirectory = root;

await reset(0);
fixture = makeAgent(
  [turnStart(1), toolCall('edit', { file_path: 'a.txt' }, 'call-edit')],
  { id: 'child-session', origin: 'subagent', delegationDepth: 1 },
);
await stopping({ agent: fixture.agent, turn: 1, signal: new AbortController().signal });
assert.equal(await runCount(), 0, 'subagent turns are skipped');
assert.equal(fixture.steers.length, 0);
assert.equal(fixture.injects.length, 0);

await rm(root, { recursive: true, force: true });
await rm(emptyRoot, { recursive: true, force: true });
console.log('stop verification tests passed');
