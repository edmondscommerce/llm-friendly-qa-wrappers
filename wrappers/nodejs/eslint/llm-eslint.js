#!/usr/bin/env node

import { ESLint } from "eslint";
import { writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomBytes } from "node:crypto";

const targets = process.argv.slice(2);

if (targets.length === 0) {
  process.stderr.write("❌ ESLint: No targets specified\n");
  process.stderr.write("   Usage: llm-eslint.js <path> [...paths]\n");
  process.exit(2);
}

try {
  const eslint = new ESLint();
  const results = await eslint.lintFiles(targets);

  let totalErrors = 0;
  let totalWarnings = 0;
  let totalFiles = results.length;
  let filesWithErrors = 0;

  const fileResults = results.map((result) => {
    const errors = result.messages.filter((m) => m.severity === 2);
    const warnings = result.messages.filter((m) => m.severity === 1);
    totalErrors += errors.length;
    totalWarnings += warnings.length;
    if (errors.length > 0) filesWithErrors++;

    return {
      file_path: result.filePath,
      error_count: errors.length,
      warning_count: warnings.length,
      errors: errors.map((m) => ({
        line: m.line,
        column: m.column,
        severity: "error",
        rule: m.ruleId,
        message: m.message,
      })),
      warnings: warnings.map((m) => ({
        line: m.line,
        column: m.column,
        severity: "warning",
        rule: m.ruleId,
        message: m.message,
      })),
    };
  });

  const eslintVersion = (await import("eslint/package.json", { with: { type: "json" } })).default.version;

  const output = {
    tool: "eslint",
    version: eslintVersion,
    timestamp: new Date().toISOString(),
    exit_code: totalErrors > 0 ? 1 : 0,
    command: `llm-eslint.js ${targets.join(" ")}`,
    summary: {
      total_files: totalFiles,
      files_with_errors: filesWithErrors,
      error_count: totalErrors,
      warning_count: totalWarnings,
    },
    results: fileResults,
  };

  const tmpFile = join(
    tmpdir(),
    `eslint-${randomBytes(4).toString("hex")}.json`
  );
  writeFileSync(tmpFile, JSON.stringify(output, null, 2));

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
    // Show up to 3 top errors
    const topErrors = fileResults
      .flatMap((f) =>
        f.errors.map((e) => ({ file: f.file_path, ...e }))
      )
      .slice(0, 3);
    for (const e of topErrors) {
      process.stdout.write(
        `   - ${e.file}:${e.line}:${e.column} ${e.rule}: ${e.message}\n`
      );
    }
    process.stdout.write(`   (details: ${tmpFile})\n`);
    process.exit(1);
  }
} catch (err) {
  process.stderr.write(`❌ ESLint: Execution error - ${err.message}\n`);
  process.exit(2);
}
