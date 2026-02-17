#!/usr/bin/env node

/**
 * Vitest wrapper using native JSON output (--reporter=json).
 *
 * Vitest provides JSON output natively, so we use it directly
 * rather than reconstructing JSON from a programmatic API.
 */

import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";

const targets = process.argv.slice(2);

if (targets.length === 0) {
  process.stderr.write("❌ Vitest: No targets specified\n");
  process.stderr.write("   Usage: llm-vitest.js <path> [...paths]\n");
  process.exit(2);
}

const wrapperDir = dirname(fileURLToPath(import.meta.url));
const vitestBin = join(wrapperDir, "node_modules", ".bin", "vitest");

try {
  let rawOutput;
  let exitCode = 0;

  try {
    rawOutput = execFileSync(
      vitestBin,
      ["run", "--reporter=json", ...targets],
      {
        encoding: "utf-8",
        maxBuffer: 50 * 1024 * 1024,
      }
    );
  } catch (err) {
    if (err.stdout) {
      rawOutput = err.stdout;
      exitCode = err.status;
    } else {
      throw err;
    }
  }

  // Vitest may prepend non-JSON output before the JSON block
  const jsonStart = rawOutput.indexOf("{");
  if (jsonStart === -1) {
    throw new Error("No JSON output found from Vitest");
  }
  const jsonOutput = rawOutput.slice(jsonStart);

  const results = JSON.parse(jsonOutput);

  const tmpFile = join(
    tmpdir(),
    `vitest-${randomBytes(4).toString("hex")}.json`
  );
  writeFileSync(tmpFile, JSON.stringify(results, null, 2));

  const { numPassedTests, numFailedTests, numTotalTests, success } = results;

  if (success) {
    process.stdout.write(
      `✅ Vitest: ${numPassedTests}/${numTotalTests} tests passed (details: ${tmpFile})\n`
    );
    process.exit(0);
  } else {
    process.stdout.write(
      `❌ Vitest: ${numFailedTests} failed, ${numPassedTests} passed of ${numTotalTests} tests\n`
    );
    const failedSuites = results.testResults.filter(
      (r) => r.status === "failed"
    );
    for (const suite of failedSuites.slice(0, 3)) {
      const failedTest = suite.assertionResults?.find(
        (a) => a.status === "failed"
      );
      if (failedTest) {
        process.stdout.write(
          `   - ${failedTest.fullName}: ${failedTest.failureMessages[0]?.split("\n")[0] || "failed"}\n`
        );
      }
    }
    process.stdout.write(`   (details: ${tmpFile})\n`);
    process.exit(1);
  }
} catch (err) {
  process.stderr.write(`❌ Vitest: Execution error - ${err.message}\n`);
  process.exit(2);
}
