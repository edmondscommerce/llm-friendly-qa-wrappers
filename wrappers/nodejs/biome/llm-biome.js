#!/usr/bin/env node

/**
 * Biome wrapper using native JSON output (--reporter=json).
 *
 * Biome provides JSON output natively via --reporter=json, so we use it
 * directly rather than reconstructing JSON from a programmatic API.
 */

import { spawnSync } from "node:child_process";
import { writeFileSync, openSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";

const targets = process.argv.slice(2);

if (targets.length === 0) {
  process.stderr.write("❌ Biome: No targets specified\n");
  process.stderr.write("   Usage: llm-biome.js <path> [...paths]\n");
  process.exit(2);
}

const wrapperDir = dirname(fileURLToPath(import.meta.url));
const biomeBin = join(wrapperDir, "node_modules", ".bin", "biome");

try {
  // Suppress biome's stderr (unstable warnings, summary lines) to keep output terse
  const devNull = openSync("/dev/null", "w");
  const proc = spawnSync(
    biomeBin,
    ["lint", "--reporter=json", ...targets],
    {
      encoding: "utf-8",
      maxBuffer: 50 * 1024 * 1024,
      stdio: ["pipe", "pipe", devNull],
    }
  );
  const stdout = proc.stdout || "";
  const exitCode = proc.status;

  // Biome outputs JSON on stdout; find the JSON object
  const jsonStart = stdout.indexOf("{");
  if (jsonStart === -1) {
    throw new Error("No JSON output found from Biome");
  }
  // Find the last closing brace to handle potential trailing output
  const jsonEnd = stdout.lastIndexOf("}");
  const jsonStr = stdout.slice(jsonStart, jsonEnd + 1);

  const results = JSON.parse(jsonStr);

  const tmpFile = join(
    tmpdir(),
    `biome-${randomBytes(4).toString("hex")}.json`
  );
  writeFileSync(tmpFile, JSON.stringify(results, null, 2));

  const errorCount = results.summary?.errors || 0;
  const warningCount = results.summary?.warnings || 0;

  if (errorCount === 0) {
    const warnMsg = warningCount > 0 ? `, ${warningCount} warnings` : "";
    process.stdout.write(
      `✅ Biome: 0 errors${warnMsg} (details: ${tmpFile})\n`
    );
    process.exit(0);
  } else {
    process.stdout.write(
      `❌ Biome: ${errorCount} errors, ${warningCount} warnings\n`
    );
    const topDiags = (results.diagnostics || []).slice(0, 3);
    for (const d of topDiags) {
      const file = d.location?.path?.file || "unknown";
      process.stdout.write(
        `   - ${file}: ${d.description || d.category}\n`
      );
    }
    process.stdout.write(`   (details: ${tmpFile})\n`);
    process.exit(1);
  }
} catch (err) {
  process.stderr.write(`❌ Biome: Execution error - ${err.message}\n`);
  process.exit(2);
}
