import { cpSync, existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const packageManager = process.env.npm_execpath?.includes("pnpm") ? "pnpm" : "npm";

rmSync("dist", { force: true, recursive: true });

if (!existsSync("frontend/node_modules")) {
  execFileSync(packageManager, ["install"], {
    cwd: "frontend",
    stdio: "inherit",
    shell: process.platform === "win32",
  });
}
execFileSync(packageManager, ["run", "build"], {
  cwd: "frontend",
  stdio: "inherit",
  shell: process.platform === "win32",
});

mkdirSync("dist/server", { recursive: true });
mkdirSync("dist/.openai", { recursive: true });
cpSync("frontend/out", "dist/assets", { force: true, recursive: true });
cpSync(".openai/hosting.json", "dist/.openai/hosting.json", { force: true });

writeFileSync(
  "dist/server/index.js",
  `export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const assetResponse = await env.ASSETS.fetch(request);

    if (assetResponse.status !== 404 || url.pathname.includes(".")) {
      return assetResponse;
    }

    const fallbackUrl = new URL("/index.html", url);
    return env.ASSETS.fetch(new Request(fallbackUrl, request));
  },
};
`,
);
