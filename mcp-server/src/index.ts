import { spawn } from "child_process";

function runCli(args: string[]): Promise<{ code: number }> {
  return new Promise((resolve) => {
    const p = spawn("python", ["-m", "engine.cli.auto_rebase", ...args], { stdio: "inherit" });
    p.on("close", (code) => resolve({ code: code ?? 1 }));
  });
}

async function main() {
  console.log("auto-rebase MCP server stub. Expose CLI via tools.");
  const code = (await runCli(["--help"]))?.code;
  process.exit(0);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});

