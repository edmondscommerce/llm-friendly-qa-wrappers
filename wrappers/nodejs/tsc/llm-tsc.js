#!/usr/bin/env node

/**
 * TypeScript compiler (tsc) wrapper with custom JSON output.
 *
 * tsc does not have a native JSON output mode, so we parse its
 * diagnostic output to produce structured JSON.
 */

import { execFileSync } from "node:child_process";
import { writeFileSync, readdirSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname, resolve } from "node:path";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";

const targets = process.argv.slice(2);

if (targets.length === 0) {
  process.stderr.write("❌ tsc: No targets specified\n");
  process.stderr.write("   Usage: llm-tsc.js <path> [...paths]\n");
  process.exit(2);
}

const wrapperDir = dirname(fileURLToPath(import.meta.url));
const tscBin = join(wrapperDir, "node_modules", ".bin", "tsc");

// Resolve directories into .ts files since tsc doesn't accept directories
function collectTsFiles(dir, files) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      collectTsFiles(fullPath, files);
    } else if (/\.(ts|tsx)$/.test(entry.name) && !entry.name.endsWith(".d.ts")) {
      files.push(resolve(fullPath));
    }
  }
}

function resolveTargets(targets) {
  const files = [];
  for (const target of targets) {
    const stat = statSync(target, { throwIfNoEntry: false });
    if (!stat) continue;
    if (stat.isFile()) {
      files.push(resolve(target));
    } else if (stat.isDirectory()) {
      collectTsFiles(target, files);
    }
  }
  return files;
}

try {
  const tsFiles = resolveTargets(targets);

  if (tsFiles.length === 0) {
    process.stderr.write("❌ tsc: No TypeScript files found\n");
    process.exit(2);
  }

  let rawOutput = "";
  let exitCode = 0;

  try {
    rawOutput = execFileSync(
      tscBin,
      ["--noEmit", "--pretty", "false", ...tsFiles],
      {
        encoding: "utf-8",
        maxBuffer: 50 * 1024 * 1024,
      }
    );
  } catch (err) {
    if (err.stdout !== undefined) {
      rawOutput = err.stdout;
      exitCode = err.status;
    } else {
      throw err;
    }
  }

  // Parse tsc output: file(line,col): category TScode: message
  const diagnostics = [];
  const diagRegex = /^(.+?)\((\d+),(\d+)\):\s+(error|warning)\s+(TS\d+):\s+(.+)$/gm;
  let match;

  while ((match = diagRegex.exec(rawOutput)) !== null) {
    diagnostics.push({
      file_path: match[1],
      line: parseInt(match[2], 10),
      column: parseInt(match[3], 10),
      severity: match[4],
      code: match[5],
      message: match[6],
    });
  }

  const errorCount = diagnostics.filter((d) => d.severity === "error").length;
  const warningCount = diagnostics.filter(
    (d) => d.severity === "warning"
  ).length;
  const filesWithErrors = new Set(
    diagnostics.filter((d) => d.severity === "error").map((d) => d.file_path)
  ).size;

  // Get tsc version
  let tscVersion = "unknown";
  try {
    tscVersion = execFileSync(tscBin, ["--version"], {
      encoding: "utf-8",
    }).trim().replace(/^Version\s+/, "");
  } catch {}

  const output = {
    tool: "tsc",
    version: tscVersion,
    timestamp: new Date().toISOString(),
    exit_code: errorCount > 0 ? 1 : 0,
    command: `llm-tsc.js ${targets.join(" ")}`,
    summary: {
      total_errors: errorCount,
      total_warnings: warningCount,
      files_with_errors: filesWithErrors,
    },
    diagnostics,
  };

  const tmpFile = join(
    tmpdir(),
    `tsc-${randomBytes(4).toString("hex")}.json`
  );
  writeFileSync(tmpFile, JSON.stringify(output, null, 2));

  if (errorCount === 0) {
    process.stdout.write(
      `✅ tsc: 0 errors (details: ${tmpFile})\n`
    );
    process.exit(0);
  } else {
    process.stdout.write(
      `❌ tsc: ${errorCount} errors in ${filesWithErrors} files\n`
    );
    for (const d of diagnostics.slice(0, 3)) {
      process.stdout.write(
        `   - ${d.file_path}:${d.line}:${d.column} ${d.code}: ${d.message}\n`
      );
    }
    process.stdout.write(`   (details: ${tmpFile})\n`);
    process.exit(1);
  }
} catch (err) {
  process.stderr.write(`❌ tsc: Execution error - ${err.message}\n`);
  process.exit(2);
}
