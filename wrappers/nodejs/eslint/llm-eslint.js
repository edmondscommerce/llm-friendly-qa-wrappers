#!/usr/bin/env node

/**
 * ESLint wrapper using native JSON output (--format json).
 *
 * ESLint provides rich JSON output natively, so we use it directly
 * rather than reconstructing JSON from the programmatic API.
 */

import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";

const targets = process.argv.slice(2);

if (targets.length === 0) {
  process.stderr.write("❌ ESLint: No targets specified\n");
  process.stderr.write("   Usage: llm-eslint.js <path> [...paths]\n");
  process.exit(2);
}

const wrapperDir = dirname(fileURLToPath(import.meta.url));
const eslintBin = join(wrapperDir, "node_modules", ".bin", "eslint");

try {
  let jsonOutput;
  let exitCode = 0;

  try {
    jsonOutput = execFileSync(eslintBin, ["--format", "json", ...targets], {
      encoding: "utf-8",
      maxBuffer: 50 * 1024 * 1024,
    });
  } catch (err) {
    if (err.stdout) {
      // ESLint exits non-zero when it finds errors, but still outputs JSON
      jsonOutput = err.stdout;
      exitCode = err.status;
    } else {
      throw err;
    }
  }

  const results = JSON.parse(jsonOutput);

  // Calculate summary from native output
  let totalErrors = 0;
  let totalWarnings = 0;
  let filesWithErrors = 0;

  for (const file of results) {
    totalErrors += file.errorCount;
    totalWarnings += file.warningCount;
    if (file.errorCount > 0) filesWithErrors++;
  }

  const tmpFile = join(
    tmpdir(),
    `eslint-${randomBytes(4).toString("hex")}.json`
  );
  writeFileSync(tmpFile, JSON.stringify(results, null, 2));

  if (totalErrors === 0) {
    const warnMsg = totalWarnings > 0 ? `, ${totalWarnings} warnings` : "";
    process.stdout.write(
      `✅ ESLint: 0 errors${warnMsg} (details: ${tmpFile})\n`
    );
    process.exit(0);
  } else {
    process.stdout.write(
      `❌ ESLint: ${totalErrors} errors, ${totalWarnings} warnings in ${filesWithErrors} files\n`
    );
    // Show up to 3 top errors from native output
    const topErrors = results
      .flatMap((f) =>
        f.messages
          .filter((m) => m.severity === 2)
          .map((m) => ({ file: f.filePath, ...m }))
      )
      .slice(0, 3);
    for (const e of topErrors) {
      process.stdout.write(
        `   - ${e.file}:${e.line}:${e.column} ${e.ruleId}: ${e.message}\n`
      );
    }
    process.stdout.write(`   (details: ${tmpFile})\n`);
    process.exit(1);
  }
} catch (err) {
  process.stderr.write(`❌ ESLint: Execution error - ${err.message}\n`);
  process.exit(2);
}
