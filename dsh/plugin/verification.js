import { randomUUID } from 'node:crypto';
import { existsSync } from 'node:fs';
import { resolve } from 'node:path';

const EVIDENCE_KIND = 'wxh-dsh-trellis/run-checks';

const DEFAULT_MUTATION_TOOLS = [
  'bash',
  'pwsh',
  'write',
  'edit',
  'str_replace_editor',
  'mcp__serena__replace_content',
  'mcp__serena__replace_in_files',
  'mcp__serena__replace_symbol_body',
  'mcp__serena__insert_after_symbol',
  'mcp__serena__insert_before_symbol',
  'mcp__serena__rename_symbol',
  'mcp__serena__safe_delete_symbol',
  'mcp__serena__write_memory',
  'mcp__serena__edit_memory',
  'mcp__serena__delete_memory',
  'mcp__serena__rename_memory',
];

export function currentVerification(session, mutationToolNames = DEFAULT_MUTATION_TOOLS) {
  const calls = new Map();
  const mutations = new Set(mutationToolNames);
  let evidence;
  let stale = false;

  for (let seq = 0; seq < session.seq; seq += 1) {
    const event = session.eventAt(seq);
    if (event === undefined) continue;
    if (event.type === 'turn/start') {
      evidence = undefined;
      stale = false;
      continue;
    }
    if (event.type === 'tool/call') {
      calls.set(event.data.callId, event.data.name);
      if (evidence !== undefined && mutations.has(event.data.name)) stale = true;
      continue;
    }
    if (event.type !== 'tool/result') continue;
    const callName = calls.get(event.data.message.toolCallId);
    if (callName !== 'run_checks') continue;
    const meta = event.data.meta;
    evidence = {
      seq,
      passed: event.data.message.isError !== true
        && meta?.kind === EVIDENCE_KIND
        && meta.passed === true,
    };
    stale = false;
  }

  return { evidence, stale };
}

const READ_ONLY_COMMANDS = new Set([
  'ls', 'pwd', 'cat', 'head', 'tail', 'grep', 'rg', 'egrep', 'fgrep', 'find',
  'wc', 'stat', 'file', 'du', 'df', 'date', 'uname', 'whoami', 'id', 'env',
  'printenv', 'which', 'type', 'command', 'true', 'false', 'sleep', 'echo',
  'printf', 'jq', 'awk', 'sort', 'uniq', 'cut', 'tr', 'basename', 'dirname',
  'realpath', 'readlink', 'test', '[', 'pytest', 'vitest', 'jest', 'mocha',
  'tsc', 'eslint', 'ruff', 'golangci-lint', 'gofmt', 'sed', 'perl',
  'cd', 'pushd', 'popd', 'export', 'unset',
  'git', 'npm', 'pnpm', 'yarn', 'bun', 'pip', 'pip3', 'uv', 'poetry',
  'cargo', 'go', 'composer', 'gem',
]);

const MUTATING_COMMANDS = new Set([
  'rm', 'rmdir', 'mv', 'cp', 'mkdir', 'touch', 'chmod', 'chown', 'chgrp',
  'ln', 'truncate', 'tee', 'dd', 'install', 'patch', 'make', 'cmake', 'ninja',
]);

const MUTATING_GIT_SUBCOMMANDS = new Set([
  'add', 'commit', 'apply', 'checkout', 'restore', 'reset', 'clean', 'merge',
  'rebase', 'cherry-pick', 'stash', 'switch', 'rm', 'mv',
]);

const MUTATING_PACKAGE_SUBCOMMANDS = new Set([
  'install', 'add', 'remove', 'uninstall', 'update', 'upgrade', 'get', 'link',
  'unlink',
]);

function parseArguments(value) {
  if (typeof value === 'string') {
    try {
      return JSON.parse(value);
    } catch {
      return undefined;
    }
  }
  return value ?? {};
}

function stripQuoted(command) {
  return command.replace(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'/g, '""');
}

function firstNonOption(tokens) {
  for (let index = 0; index < tokens.length; index += 1) {
    const token = tokens[index];
    if (token.startsWith('-')) {
      if (['-C', '-c', '--prefix', '--cwd', '--dir'].includes(token)) index += 1;
      continue;
    }
    return token;
  }
  return undefined;
}

/**
 * Conservative heuristic for a shell call that may change files.
 * Unknown commands count as mutating; clearly read-only commands do not.
 */
export function isMutatingShell(command) {
  if (typeof command !== 'string' || command.trim() === '') return false;
  const stripped = stripQuoted(command);
  if (/(^|[^0-9])>{1,2}(?!&)/.test(stripped)) return true;

  for (const raw of stripped.split(/\n|;|&&|\|\||\|/)) {
    const tokens = raw.trim().split(/\s+/).filter(Boolean);
    let index = 0;
    while (index < tokens.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[index])) index += 1;
    let base = (tokens[index] ?? '').split('/').pop();
    if (['sudo', 'doas', 'env', 'time', 'command', 'nohup'].includes(base)) {
      index += 1;
      while (index < tokens.length && tokens[index].startsWith('-')) index += 1;
      while (index < tokens.length && /^[A-Za-z_][A-Za-z0-9_]*=/.test(tokens[index])) index += 1;
      base = (tokens[index] ?? '').split('/').pop();
    }
    if (!base) continue;
    const args = tokens.slice(index + 1);

    if (base === 'git') {
      const sub = firstNonOption(args);
      if (sub !== undefined && MUTATING_GIT_SUBCOMMANDS.has(sub)) return true;
      continue;
    }
    if (['npm', 'pnpm', 'yarn', 'bun'].includes(base)) {
      const sub = firstNonOption(args);
      if (sub !== undefined && MUTATING_PACKAGE_SUBCOMMANDS.has(sub)) return true;
      continue;
    }
    if (['pip', 'pip3', 'uv', 'poetry', 'cargo', 'go', 'composer', 'gem'].includes(base)) {
      const sub = firstNonOption(args);
      if (sub !== undefined && MUTATING_PACKAGE_SUBCOMMANDS.has(sub)) return true;
      if (base === 'go' && sub === 'build') return true;
      continue;
    }
    if (base === 'sed' || base === 'perl') {
      if (args.some((arg) => /^-[a-zA-Z]*i/.test(arg))) return true;
      continue;
    }
    if (base === 'find' && args.includes('-delete')) return true;
    if (base === 'prettier' && args.includes('--write')) return true;
    if (base === 'black' && !args.includes('--check')) return true;
    if (base === 'gofmt' && args.includes('-w')) return true;
    if (MUTATING_COMMANDS.has(base)) return true;
    if (READ_ONLY_COMMANDS.has(base)) continue;
    return true;
  }
  return false;
}

/**
 * Mutation state for one turn. A bash call counts only when its command looks
 * mutating; malformed bash arguments count conservatively as mutations.
 */
export function turnMutationState(session, turn, mutationToolNames = DEFAULT_MUTATION_TOOLS) {
  const mutations = new Set(mutationToolNames);
  let mutated = false;
  let lastMutationSeq = -1;
  let start = 0;

  for (let seq = session.seq - 1; seq >= 0; seq -= 1) {
    const event = session.eventAt(seq);
    if (event?.type === 'turn/start' && event.data.turn === turn) {
      start = seq;
      break;
    }
  }

  for (let seq = start; seq < session.seq; seq += 1) {
    const event = session.eventAt(seq);
    if (event?.type !== 'tool/call' || !mutations.has(event.data.name)) continue;
    if (event.data.name === 'pwsh') {
      mutated = true;
      lastMutationSeq = seq;
      continue;
    }
    if (event.data.name === 'bash') {
      const args = parseArguments(event.data.arguments);
      if (args !== undefined && !isMutatingShell(args.command)) continue;
    }
    mutated = true;
    lastMutationSeq = seq;
  }

  return { mutated, lastMutationSeq };
}

function createAgentMessage(text, summary) {
  return {
    id: randomUUID(),
    role: 'user',
    content: [{ type: 'text', text }],
    source: { kind: 'wxh-dsh-trellis', form: 'notice', summary },
  };
}

function createStopMessage(text) {
  return createAgentMessage(
    `<wxh-stop-verification>\n${text.trim()}\n</wxh-stop-verification>`,
    'automatic verification failed',
  );
}

function truncateOutput(text, max) {
  return text.length > max ? `${text.slice(0, max)}\n[output truncated]` : text;
}

export function registerStopVerification(ctx, config, { resolveCwd, run }) {
  if (!config.stopVerification) return;
  if (!config.verification) {
    throw new Error('wxh-dsh-trellis: stopVerification needs verification: true');
  }
  if (!Number.isInteger(config.stopVerificationMaxAttempts) || config.stopVerificationMaxAttempts < 1) {
    throw new Error('wxh-dsh-trellis: stopVerificationMaxAttempts must be a positive integer');
  }
  if (!Number.isInteger(config.stopVerificationMaxOutputChars) || config.stopVerificationMaxOutputChars < 1) {
    throw new Error('wxh-dsh-trellis: stopVerificationMaxOutputChars must be a positive integer');
  }

  const states = new WeakMap();
  ctx.on('agent/turn-stopping', async ({ agent, turn, signal }) => {
    if (agent?.session === undefined) return;
    const header = agent.session.header;
    if (header?.origin === 'subagent' || (header?.delegationDepth ?? 0) > 0) return;

    const state = states.get(agent.session) ?? {
      turn,
      attempts: 0,
      verifiedThroughSeq: -1,
      attemptedThroughSeq: -1,
      missingWarned: false,
    };
    states.set(agent.session, state);
    if (state.turn !== turn) {
      state.turn = turn;
      state.attempts = 0;
      state.verifiedThroughSeq = -1;
      state.attemptedThroughSeq = -1;
    }

    const { mutated, lastMutationSeq } = turnMutationState(agent.session, turn, config.mutationToolNames);
    if (!mutated) return;
    if (lastMutationSeq <= state.verifiedThroughSeq) return;
    if (lastMutationSeq <= state.attemptedThroughSeq) return;

    const cwd = await resolveCwd(ctx, { agent, arguments: {}, signal });
    const scriptPath = resolve(cwd, config.verificationScript);
    if (!existsSync(scriptPath)) {
      if (!state.missingWarned) {
        state.missingWarned = true;
        ctx.logger.warn(`wxh-dsh-trellis: stop verification skipped; ${scriptPath} not found`);
        if (typeof agent.inject === 'function') {
          try {
            agent.inject(createAgentMessage(
              `自动验证已跳过：当前工作目录没有 ${config.verificationScript}。请确认项目验证入口；本次不阻止回合结束。`,
              'stop verification skipped',
            ));
          } catch (error) {
            ctx.logger.warn(`wxh-dsh-trellis: cannot inject stop-verification notice: ${error instanceof Error ? error.message : String(error)}`);
          }
        }
      }
      return;
    }

    const evidence = currentVerification(agent.session, config.mutationToolNames);
    if (evidence.evidence?.passed && !evidence.stale) {
      state.verifiedThroughSeq = lastMutationSeq;
      return;
    }
    if (state.attempts >= config.stopVerificationMaxAttempts) return;

    state.attempts += 1;
    state.attemptedThroughSeq = lastMutationSeq;
    const finalAttempt = state.attempts >= config.stopVerificationMaxAttempts;

    let result;
    try {
      result = await run(config.verificationShell, [config.verificationScript], {
        env: { ...process.env },
        cwd,
        timeoutMs: config.verificationTimeoutMs,
        signal,
        maxOutputChars: config.stopVerificationMaxOutputChars,
      });
    } catch (error) {
      if (signal?.aborted) return;
      const message = error instanceof Error ? error.message : String(error);
      const text = [
        `自动验证无法运行（${config.verificationScript}）。`,
        `工作目录：${cwd}`,
        `第 ${state.attempts}/${config.stopVerificationMaxAttempts} 次。`,
        `错误：${message}`,
        finalAttempt ? '这是最后一次自动验证；请报告未通过项和已完成的修复。' : '',
      ].filter(Boolean).join('\n\n');
      agent.steer(createStopMessage(text));
      return;
    }

    if (result.code === 0) {
      state.verifiedThroughSeq = lastMutationSeq;
      return;
    }

    const output = [result.stdout, result.stderr].filter(Boolean).join('\n').trim();
    const text = [
      `自动验证失败（${config.verificationScript}，exit ${String(result.code)}）。`,
      `工作目录：${cwd}`,
      `第 ${state.attempts}/${config.stopVerificationMaxAttempts} 次。修复失败原因后继续；不要只报告完成。`,
      output ? `输出：\n${truncateOutput(output, config.stopVerificationMaxOutputChars)}` : '',
      finalAttempt ? '这是最后一次自动验证；请报告未通过项和已完成的修复。' : '',
    ].filter(Boolean).join('\n\n');
    agent.steer(createStopMessage(text));
  });
}

function outputSchema() {
  return {
    type: 'object',
    additionalProperties: false,
    required: ['kind', 'script', 'cwd', 'passed', 'exitCode', 'durationMs', 'output', 'error'],
    properties: {
      kind: { type: 'string', const: 'checks' },
      script: { type: 'string' },
      cwd: { type: 'string' },
      passed: { type: 'boolean' },
      exitCode: { oneOf: [{ type: 'integer' }, { type: 'null' }] },
      durationMs: { type: 'integer' },
      output: { type: 'string' },
      error: { type: 'string' },
    },
  };
}

function presentationMeta(_args, value) {
  return {
    kind: EVIDENCE_KIND,
    passed: value.passed,
    script: value.script,
    cwd: value.cwd,
    exitCode: value.exitCode,
    durationMs: value.durationMs,
  };
}

function renderResult(_args, value) {
  return [{ type: 'text', text: JSON.stringify(value, null, 2) }];
}

export function registerVerification(ctx, config, { resolveCwd, run }) {
  if (config.requireVerification && !config.verification) {
    throw new Error('wxh-dsh-trellis: requireVerification needs verification: true');
  }
  if (!config.verification) return;

  ctx.tools.register({
    name: 'run_checks',
    description: 'Run the project-owned verification entrypoint configured by the deployment. The model cannot choose the command. Use this after implementation and before marking a goal complete; a later write, edit, or shell call makes the evidence stale.',
    parameters: {},
    timeoutMs: config.verificationTimeoutMs + 1000,
    output: {
      schema: outputSchema(),
      render: renderResult,
      presentationMeta,
    },
    async execute(_args, exec) {
      const startedAt = Date.now();
      const cwd = await resolveCwd(ctx, exec);
      const script = config.verificationScript;
      const base = {
        kind: 'checks',
        script,
        cwd,
        durationMs: 0,
      };
      try {
        const result = await run(config.verificationShell, [script], {
          env: { ...process.env },
          cwd,
          timeoutMs: config.verificationTimeoutMs,
          signal: exec.signal,
          maxOutputChars: config.verificationMaxOutputChars,
        });
        const output = [result.stdout, result.stderr].filter(Boolean).join('\n')
          + (result.truncated ? '\n[output truncated]' : '');
        return {
          ...base,
          passed: result.code === 0,
          exitCode: result.code,
          durationMs: Date.now() - startedAt,
          output,
          error: result.code === 0 ? '' : `Verification exited ${String(result.code)}`,
        };
      } catch (error) {
        return {
          ...base,
          passed: false,
          exitCode: null,
          durationMs: Date.now() - startedAt,
          output: '',
          error: error instanceof Error ? error.message : String(error),
        };
      }
    },
  });

  if (!config.requireVerification) return;
  ctx.tools.guard((exec) => {
    if (exec.name !== 'update_goal' || exec.arguments?.action !== 'complete' || exec.agent === undefined) {
      return undefined;
    }
    const { evidence, stale } = currentVerification(exec.agent.session, config.mutationToolNames);
    if (evidence === undefined) return '完成 goal 前，先调用 run_checks 运行项目固定的验证入口。';
    if (!evidence.passed) return '最近一次 run_checks 未通过；修复失败后重新运行，再完成 goal。';
    if (stale) return '最近一次 run_checks 之后又有写入、编辑或 shell 调用；请重新运行 run_checks。';
    return undefined;
  });
}

export { DEFAULT_MUTATION_TOOLS };
