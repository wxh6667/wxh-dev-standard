/**
 * Minimal stdio MCP probe for the DSH baseline.
 *
 * Starts each server, performs initialize + tools/list, and prints a JSON line.
 * It does not call tools or a model. Usage:
 *
 *   node dsh/mcp-probe.mjs [project-dir]
 *
 * `project-dir` is used as cwd for --project-from-cwd servers (default: cwd).
 */
import { spawn } from 'node:child_process';

const HOME = process.env.HOME;
const project = process.argv[2] ?? process.cwd();
const baseEnv = {
  ...process.env,
  PATH: `${HOME}/.local/bin:${process.env.PATH ?? ''}`,
  HOME,
};

const servers = [
  {
    name: 'context7',
    command: 'npx',
    args: ['-y', '@upstash/context7-mcp'],
    env: { CONTEXT7_API_KEY: process.env.CONTEXT7_API_KEY ?? '' },
  },
  {
    name: 'sequential-thinking',
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-sequential-thinking'],
  },
  {
    name: 'serena',
    command: 'uvx',
    args: ['-p', '3.13', 'serena-agent', 'start-mcp-server', '--project-from-cwd', '--context', 'claude-code'],
  },
  {
    name: 'playwright',
    command: 'npx',
    args: ['@playwright/mcp@latest', '--isolated', '--no-sandbox'],
  },
  {
    name: 'mcp-server-time',
    command: 'uvx',
    args: ['--with', 'mcp<2', 'mcp-server-time==2026.7.10', '--local-timezone=Asia/Shanghai'],
  },
  {
    name: 'awslabs-doc-loader',
    command: 'uvx',
    args: ['awslabs.document-loader-mcp-server@latest'],
    env: { FASTMCP_LOG_LEVEL: 'ERROR' },
  },
];

function probe(server) {
  return new Promise((resolve) => {
    const child = spawn(server.command, server.args, {
      cwd: project,
      env: { ...baseEnv, ...(server.env ?? {}) },
      stdio: ['pipe', 'pipe', 'pipe'],
      windowsHide: true,
    });
    let stdout = '';
    let stderr = '';
    let settled = false;
    const timer = setTimeout(() => finish({ ok: false, reason: 'timeout after 180s' }), 180_000);

    const finish = (result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      try { child.kill(); } catch {}
      resolve({ name: server.name, ...result, stderr: stderr.slice(-1200) });
    };

    const send = (message) => {
      child.stdin.write(`${JSON.stringify(message)}\n`);
    };

    const onLine = (line) => {
      if (line.trim().length === 0) return;
      let message;
      try {
        message = JSON.parse(line);
      } catch {
        return;
      }
      if (message.id === 1) {
        if (message.error) {
          finish({ ok: false, reason: `initialize error: ${JSON.stringify(message.error)}` });
          return;
        }
        send({ jsonrpc: '2.0', method: 'notifications/initialized' });
        send({ jsonrpc: '2.0', id: 2, method: 'tools/list', params: {} });
        return;
      }
      if (message.id === 2) {
        if (message.error) {
          finish({ ok: false, reason: `tools/list error: ${JSON.stringify(message.error)}` });
          return;
        }
        const tools = message.result?.tools;
        if (!Array.isArray(tools)) {
          finish({ ok: false, reason: 'tools/list returned no tools array' });
          return;
        }
        finish({ ok: true, toolCount: tools.length, tools: tools.slice(0, 8).map((tool) => tool.name) });
      }
    };

    child.stdout.setEncoding('utf8');
    child.stderr.setEncoding('utf8');
    child.stdout.on('data', (chunk) => {
      stdout += chunk;
      const lines = stdout.split('\n');
      stdout = lines.pop() ?? '';
      for (const line of lines) onLine(line);
    });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', (error) => finish({ ok: false, reason: error.message }));
    child.on('exit', (code) => {
      if (!settled) finish({ ok: false, reason: `exited before tools/list (code ${String(code)})` });
    });

    send({
      jsonrpc: '2.0',
      id: 1,
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: { name: 'wxh-mcp-probe', version: '0.1.0' },
      },
    });
  });
}

for (const server of servers) {
  console.log(`\n## ${server.name}`);
  console.log(JSON.stringify(await probe(server)));
}
