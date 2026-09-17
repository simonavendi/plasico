#!/usr/bin/env node
// Zero-dependency local dev server that mirrors Vercel's static hosting for this
// project. It reads `vercel.json` and applies the same `outputDirectory`,
// `rewrites`, and response `headers` so local behavior matches production
// (clean URLs, `/` -> hot-summer-sale-2026.html, campaign subpages, etc.).
//
// Usage: node scripts/dev-server.mjs [--port 3000] [--host 0.0.0.0]

import http from "node:http";
import { readFile, stat } from "node:fs/promises";
import { createReadStream } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");

function parseArgs(argv) {
  const args = { port: 3000, host: "0.0.0.0" };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--port" || a === "-p") args.port = Number(argv[++i]);
    else if (a === "--host" || a === "-h") args.host = argv[++i];
  }
  if (process.env.PORT) args.port = Number(process.env.PORT);
  return args;
}

const CONTENT_TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".txt": "text/plain; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".pdf": "application/pdf",
  ".mp4": "video/mp4",
  ".webm": "video/webm",
};

function contentType(filePath) {
  return CONTENT_TYPES[path.extname(filePath).toLowerCase()] || "application/octet-stream";
}

// Convert a Vercel rewrite `source` pattern into a RegExp and capture the
// `:param` names so the `destination` can be filled back in.
function compileRoute(source, destination) {
  const paramNames = [];
  const pattern = source.replace(/:[A-Za-z0-9_]+/g, (m) => {
    paramNames.push(m.slice(1));
    return "([^/]+)";
  });
  const regex = new RegExp("^" + pattern + "/?$");
  return { regex, paramNames, destination };
}

function applyRewrite(pathname, routes) {
  for (const route of routes) {
    const match = route.regex.exec(pathname);
    if (!match) continue;
    let dest = route.destination;
    route.paramNames.forEach((name, i) => {
      dest = dest.replace(new RegExp(":" + name + "\\b"), match[i + 1]);
    });
    return dest;
  }
  return null;
}

// Turn a Vercel header `source` (path or simple glob) into a matcher.
function compileHeaderMatcher(source) {
  const pattern = source
    .replace(/[.+?^${}()|[\]\\]/g, "\\$&")
    .replace(/\\\*/g, ".*")
    .replace(/:[A-Za-z0-9_]+/g, "[^/]+");
  return new RegExp("^" + pattern + "$");
}

async function resolveFile(pathname, outputDir) {
  // Try the path as-is, then as a directory index, then with a `.html` suffix
  // (Vercel "clean URLs" behavior).
  const candidates = [];
  const clean = pathname.replace(/\/+$/, "");
  candidates.push(pathname);
  if (clean !== pathname) candidates.push(clean);
  candidates.push(path.posix.join(pathname, "index.html"));
  if (!path.extname(clean)) candidates.push(clean + ".html");

  for (const candidate of candidates) {
    const rel = candidate.replace(/^\/+/, "");
    const filePath = path.join(outputDir, rel);
    // Guard against path traversal outside the output directory.
    if (!filePath.startsWith(outputDir)) continue;
    try {
      const info = await stat(filePath);
      if (info.isFile()) return { filePath, size: info.size };
      if (info.isDirectory()) {
        const idx = path.join(filePath, "index.html");
        const idxInfo = await stat(idx).catch(() => null);
        if (idxInfo?.isFile()) return { filePath: idx, size: idxInfo.size };
      }
    } catch {
      // keep trying candidates
    }
  }
  return null;
}

async function main() {
  const { port, host } = parseArgs(process.argv.slice(2));
  const vercelConfig = JSON.parse(await readFile(path.join(rootDir, "vercel.json"), "utf-8"));

  const outputDir = path.resolve(rootDir, vercelConfig.outputDirectory || ".");
  const routes = (vercelConfig.rewrites || []).map((r) => compileRoute(r.source, r.destination));
  const headerRules = (vercelConfig.headers || []).map((h) => ({
    matcher: compileHeaderMatcher(h.source),
    headers: h.headers || [],
  }));

  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url, `http://${req.headers.host || "localhost"}`);
    let pathname = decodeURIComponent(url.pathname);

    let resolved = await resolveFile(pathname, outputDir);

    if (!resolved) {
      const rewritten = applyRewrite(pathname, routes);
      if (rewritten) {
        pathname = rewritten;
        resolved = await resolveFile(pathname, outputDir);
      }
    }

    if (!resolved) {
      res.statusCode = 404;
      res.setHeader("Content-Type", "text/html; charset=utf-8");
      res.end(`<h1>404 Not Found</h1><p>${pathname}</p>`);
      console.log(`404 ${req.method} ${url.pathname}`);
      return;
    }

    for (const rule of headerRules) {
      if (rule.matcher.test(pathname)) {
        for (const { key, value } of rule.headers) res.setHeader(key, value);
      }
    }

    res.statusCode = 200;
    res.setHeader("Content-Type", contentType(resolved.filePath));
    res.setHeader("Content-Length", resolved.size);
    console.log(`200 ${req.method} ${url.pathname} -> ${path.relative(outputDir, resolved.filePath)}`);

    if (req.method === "HEAD") {
      res.end();
      return;
    }
    createReadStream(resolved.filePath).pipe(res);
  });

  server.listen(port, host, () => {
    console.log(`Plasico dev server running at http://${host}:${port}`);
    console.log(`Serving ${path.relative(rootDir, outputDir)} with vercel.json rewrites`);
  });
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
