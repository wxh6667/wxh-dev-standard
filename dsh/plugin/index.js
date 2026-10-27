/**
 * DSH adapter for wxh-dev-standard's custom hooks.
 *
 * - Trellis commit gate: reuse hooks/gate-commit-trellis.py as the single
 *   source of parsing/denial logic. This plugin only adapts a DSH bash/pwsh
 *   call into the hook payload and passes DSH_SESSION_ID so Trellis can resolve
 *   the active task.
 * - Stop verification: run the project verification entrypoint before a
 *   mutating turn closes, and steer with the failure output.
 * - Steer reminder: inject the shared text from dsh/steer.md on a direct user
 *   prompt, mirroring Claude's UserPromptSubmit reminder.
 *
 * Trellis's DSH platform is intentionally pull-based (skills, no workflow-state
 * hook); this plugin does not inject <workflow-state> unless a caller adds that
 * separately.
 */
import { spawn } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { dirname, isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { randomUUID } from 'node:crypto';
import { registerStopVerification, registerVerification } from './verification.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const DEFAULT_GATE_SCRIPT = join(HERE, '..', '..', 'hooks', 'gate-commit-trellis.py');
const DEFAULT_STEER_FILE = join(HERE, '..', 'steer.md');

export const name = 'wxh-dsh-trellis';
export const inject = ['tools'];

function resolveConfig(config = {}) {
  return {
    gate: config.gate ?? true,
    steer: config.steer ?? true,
    failClosed: config.failClosed ?? true,
    python: config.python ?? (process.platform === 'win32' ? 'python' : 'python3'),
    gateScript: config.gateScript ?? DEFAULT_GATE_SCRIPT,
    steerFile: config.steerFile ?? DEFAULT_STEER_FILE,
    gateTimeoutMs: config.gateTimeoutMs ?? 10_000,
    toolNames: config.toolNames ?? ['bash', 'pwsh'],
    verification: config.verification ?? false,
    requireVerification: config.requireVerification ?? false,
    verificationScript: config.verificationScript ?? 'scripts/verify.sh',
    verificationShell: config.verificationShell ?? (process.platform === 'win32' ? 'pwsh' : 'bash'),
    verificationTimeoutMs: config.verificationTimeoutMs ?? 120_000,
    verificationMaxOutputChars: config.verificationMaxOutputChars ?? 64_000,
    stopVerification: config.stopVerification ?? false,
    stopVerificationMaxAttempts: config.stopVerificationMaxAttempts ?? 3,
    stopVerificationMaxOutputChars: config.stopVerificationMaxOutputChars ?? 12_000,
    mutationToolNames: config.mutationToolNames,
  };
}

function isGitCommit(command) {
  return typeof command === 'string' && /\bgit\b[\s\S]*\bcommit\b/.test(command);
}

function run(file, args, { input, env, cwd, timeoutMs, signal, maxOutputChars = 64_000 }) {
  return new Promise((resolvePromise, reject) => {
    if (signal?.aborted) {
      reject(new Error('operation aborted'));
      return;
    }
    const child = spawn(file, args, {
      cwd,
      env,
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
    });
    let stdout = '';
    let stderr = '';
    let settled = false;
    let truncated = false;
    const append = (current, chunk) => {
      const next = current + chunk;
      if (next.length > maxOutputChars) truncated = true;
      return next.slice(0, maxOutputChars);
    };
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      signal?.removeEventListener('abort', onAbort);
      fn(value);
    };
    const onAbort = () => {
      child.kill();
      finish(reject, new Error('operation aborted'));
    };
    const timer = setTimeout(() => {
      child.kill();
      finish(reject, new Error(`timed out after ${timeoutMs}ms`));
    }, timeoutMs);
    signal?.addEventListener('abort', onAbort, { once: true });
    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk) => { stdout = append(stdout, chunk); });
    child.stderr.on('data', (chunk) => { stderr = append(stderr, chunk); });
    child.on('error', (error) => finish(reject, error));
    child.on('close', (code) => {
      finish(resolvePromise, { code, stdout, stderr, truncated });
    });
    child.stdin.end(input);
  });
}

async function resolveCwd(ctx, exec) {
  const explicit = exec.arguments?.workdir ?? exec.arguments?.cwd;
  if (typeof explicit === 'string' && explicit.length > 0) {
    return isAbsolute(explicit) ? explicit : resolve(process.cwd(), explicit);
  }
  const workingDirectory = ctx.get('workingDirectory');
  if (workingDirectory !== undefined && exec.agent !== undefined) {
    return await workingDirectory.ensure(exec.agent, exec.signal);
  }
  return process.cwd();
}

async function checkGate(ctx, exec, config) {
  const command = exec.arguments?.command;
  if (!isGitCommit(command)) return undefined;
  const cwd = await resolveCwd(ctx, exec);
  const sessionId = exec.agent?.session?.header?.id ?? exec.agent?.id;
  const env = { ...process.env };
  if (typeof sessionId === 'string' && sessionId.length > 0) env.DSH_SESSION_ID = sessionId;
  const payload = JSON.stringify({
    tool_name: 'Bash',
    tool_input: { command },
    cwd,
  });
  try {
    const result = await run(config.python, [config.gateScript], {
      input: payload,
      env,
      cwd,
      timeoutMs: config.gateTimeoutMs,
      signal: exec.signal,
    });
    if (result.code !== 0) {
      if (config.failClosed) {
        return `Trellis commit gate exited ${String(result.code)}: ${result.stderr.trim() || 'no diagnostics'}`;
      }
      return undefined;
    }
    // The source hook is silent on allow: no JSON means "no objection".
    if (result.stdout.trim().length === 0) return undefined;
    let parsed;
    try {
      parsed = JSON.parse(result.stdout);
    } catch {
      if (config.failClosed) {
        return `Trellis commit gate returned unreadable output: ${result.stdout.slice(0, 200)}`;
      }
      return undefined;
    }
    const output = parsed?.hookSpecificOutput;
    if (output?.permissionDecision === 'deny') {
      return typeof output.permissionDecisionReason === 'string' && output.permissionDecisionReason.length > 0
        ? output.permissionDecisionReason
        : 'Trellis commit gate denied this commit';
    }
    return undefined;
  } catch (error) {
    if (config.failClosed) {
      return `Trellis commit gate could not run: ${error instanceof Error ? error.message : String(error)}`;
    }
    return undefined;
  }
}

function createSteerMessage(text) {
  return {
    id: randomUUID(),
    role: 'user',
    content: [{ type: 'text', text: `<wxh-steer>\n${text.trim()}\n</wxh-steer>` }],
    source: {
      kind: 'wxh-steer',
      form: 'notice',
      summary: 'wxh steer reminder',
    },
  };
}

async function readSteer(config) {
  const raw = await readFile(config.steerFile, 'utf8');
  const text = raw.trim();
  return text.length > 0 ? text : undefined;
}

/**
 * Mount the adapter.
 * @param {import('@deepseek-ai/cordis').Context} ctx - host context.
 * @param {object} userConfig - plugin options.
 */
export function apply(ctx, userConfig = {}) {
  const config = resolveConfig(userConfig);
  registerVerification(ctx, config, { resolveCwd, run });
  registerStopVerification(ctx, config, { resolveCwd, run });

  if (config.gate) {
    ctx.on('tools/pre-execute', async (exec, next) => {
      if (!config.toolNames.includes(exec.name)) return next();
      const reason = await checkGate(ctx, exec, config);
      if (reason !== undefined) return { kind: 'deny', reason };
      return next();
    });
  }

  if (config.steer) {
    ctx.on('agent/pre-step', async ({ messages, signal }, next) => {
      const decision = await next();
      if (decision.kind === 'reject') return decision;
      if (!messages.some((message) => message.source?.kind === 'user')) return decision;
      signal.throwIfAborted();
      let text;
      try {
        text = await readSteer(config);
      } catch (error) {
        ctx.logger.warn(`wxh-dsh-trellis: cannot read steer file ${config.steerFile}: ${error instanceof Error ? error.message : String(error)}`);
        return decision;
      }
      if (text === undefined) return decision;
      return { ...decision, messages: [...decision.messages, createSteerMessage(text)] };
    });
  }
}
