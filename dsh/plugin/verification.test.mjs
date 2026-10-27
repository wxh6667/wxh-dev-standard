import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdtemp, mkdir, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { apply } from './index.js';

const require = createRequire(process.env.DSH_CLI_PACKAGE ?? join(process.env.HOME, 'dsh', 'package.json'));
const { assertSupportedJsonSchema, validateJsonSchemaValue } = require('@deepseek-ai/dsh-tools');

const root = await mkdtemp(join(tmpdir(), 'wxh-verification-fixture-'));
const emptyRoot = await mkdtemp(join(tmpdir(), 'wxh-verification-empty-'));
await mkdir(join(root, 'scripts'));
const script = join(root, 'scripts', 'verify.sh');
await writeFile(script, '#!/bin/sh\nprintf "verification ok\\n"\nexit 0\n');

const tools = new Map();
const guards = [];
let workingDirectory = root;
const ctx = {
  on() { return () => {}; },
  get(name) {
    if (name === 'workingDirectory') return { ensure: async () => workingDirectory };
    return undefined;
  },
  tools: {
    register(definition) {
      tools.set(definition.name, definition);
      return () => {};
    },
    guard(handler) {
      guards.push(handler);
      return () => {};
    },
  },
  logger: { warn: (...args) => console.error('[warn]', ...args) },
};

apply(ctx, {
  gate: false,
  steer: false,
  verification: true,
  requireVerification: true,
  verificationTimeoutMs: 5000,
});

const runChecks = tools.get('run_checks');
assert.ok(runChecks, 'run_checks registered');
assert.deepEqual(runChecks.parameters, {}, 'model cannot supply a command');
assertSupportedJsonSchema(runChecks.output.schema, 'run_checks.output');
assert.deepEqual(
  validateJsonSchemaValue(runChecks.output.schema, {
    kind: 'checks',
    script: 'scripts/verify.sh',
    cwd: root,
    passed: true,
    exitCode: 0,
    durationMs: 1,
    output: '',
    error: '',
  }),
  [],
  'run_checks output satisfies the DSH runtime schema',
);
assert.deepEqual(
  runChecks.output.schema.required,
  ['kind', 'script', 'cwd', 'passed', 'exitCode', 'durationMs', 'output', 'error'],
  'required fields use the object-level JSON Schema contract',
);
assert.ok(
  Object.values(runChecks.output.schema.properties).every((property) => !('required' in property)),
  'DSH rejects required on individual property schemas',
);
assert.equal(guards.length, 1, 'completion guard registered');
const guard = guards[0];

function session(events) {
  return {
    header: { id: 'verification-session' },
    seq: events.length,
    eventAt(seq) { return events[seq]; },
  };
}

function toolCall(callId, name) {
  return { type: 'tool/call', data: { callId, name, arguments: '{}' } };
}

function toolResult(callId, value, isError = false) {
  return {
    type: 'tool/result',
    data: {
      message: { toolCallId: callId, isError },
      meta: runChecks.output.presentationMeta({}, value),
    },
  };
}

function goalExecution(currentSession, action = 'complete') {
  return {
    name: 'update_goal',
    arguments: { action },
    agent: { session: currentSession },
  };
}

const execution = {
  agent: { session: session([]) },
  signal: new AbortController().signal,
};
const passed = await runChecks.execute({}, execution);
assert.equal(passed.passed, true, 'real verification script passes');
assert.equal(passed.exitCode, 0);
assert.match(passed.output, /verification ok/);

const passEvents = [
  { type: 'turn/start', data: { turn: 1 } },
  toolCall('check-1', 'run_checks'),
  toolResult('check-1', passed),
];
assert.equal(guard(goalExecution(session(passEvents))), undefined, 'current passing evidence allows completion');
assert.equal(guard(goalExecution(session(passEvents), 'pause')), undefined, 'other goal actions are unaffected');

const staleEvents = [...passEvents, toolCall('write-1', 'write')];
assert.match(guard(goalExecution(session(staleEvents))), /重新运行/, 'write after checks makes evidence stale');
const shellStaleEvents = [...passEvents, toolCall('bash-1', 'bash')];
assert.match(guard(goalExecution(session(shellStaleEvents))), /重新运行/, 'shell after checks makes evidence stale');
const newTurnEvents = [...passEvents, { type: 'turn/start', data: { turn: 2 } }];
assert.match(guard(goalExecution(session(newTurnEvents))), /先调用 run_checks/, 'previous turn evidence is insufficient');

await writeFile(script, '#!/bin/sh\nprintf "intentional failure\\n"\nexit 23\n');
const failed = await runChecks.execute({}, execution);
assert.equal(failed.passed, false, 'nonzero verification is a failed result');
assert.equal(failed.exitCode, 23);
const failedEvents = [
  { type: 'turn/start', data: { turn: 1 } },
  toolCall('check-2', 'run_checks'),
  toolResult('check-2', failed),
];
assert.match(guard(goalExecution(session(failedEvents))), /未通过/, 'failed checks deny completion');

workingDirectory = emptyRoot;
const missing = await runChecks.execute({}, execution);
assert.equal(missing.passed, false, 'missing verification entrypoint cannot pass');
assert.equal(missing.exitCode, 127);
assert.match(missing.error, /exited 127/);

await rm(root, { recursive: true, force: true });
await rm(emptyRoot, { recursive: true, force: true });
console.log('verification tests passed');
