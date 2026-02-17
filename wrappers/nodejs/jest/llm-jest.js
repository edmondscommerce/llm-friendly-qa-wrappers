#!/usr/bin/env node

/**
 * Jest wrapper using native JSON output (--json).
 *
 * Jest provides rich JSON output natively, so we use it directly
 * rather than reconstructing JSON from a programmatic API.
 */

import { spawnSync } from "node:child_process";
import { writeFileSync, openSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { randomBytes } from "node:crypto";
import { fileURLToPath } from "node:url";

const targets = process.argv.slice(2);

if (targets.length === 0) {
  process.stderr.write("❌ Jest: No targets specified\n");
  process.stderr.write("   Usage: llm-jest.js <path> [...paths]\n");
  process.exit(2);
}

const wrapperDir = dirname(fileURLToPath(import.meta.url));
const jestBin = join(wrapperDir, "node_modules", ".bin", "jest");

try {
  // Suppress Jest's visual stderr output to keep terminal terse
  const devNull = openSync("/dev/null", "w");
  const proc = spawnSync(
    jestBin,
    ["--json", "--no-coverage", ...targets],
    {
      encoding: "utf-8",
      maxBuffer: 50 * 1024 * 1024,
      stdio: ["pipe", "pipe", devNull],
    }
  );

  const rawOutput = proc.stdout || "";

  // Jest may prepend non-JSON visual output before the JSON block
  const jsonStart = rawOutput.indexOf("{");
  if (jsonStart === -1) {
    throw new Error("No JSON output found from Jest");
  }
  const results = JSON.parse(rawOutput.slice(jsonStart));

  const tmpFile = join(
    tmpdir(),
    `jest-${randomBytes(4).toString("hex")}.json`
  );
  writeFileSync(tmpFile, JSON.stringify(results, null, 2));

  const { numPassedTests, numFailedTests, numTotalTests } = results;

  if (results.success) {
    process.stdout.write(
      `✅ Jest: ${numPassedTests}/${numTotalTests} tests passed (details: ${tmpFile})\n`
    );
    process.exit(0);
  } else {
    process.stdout.write(
      `❌ Jest: ${numFailedTests} failed, ${numPassedTests} passed of ${numTotalTests} tests\n`
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
  process.stderr.write(`❌ Jest: Execution error - ${err.message}\n`);
  process.exit(2);
}
