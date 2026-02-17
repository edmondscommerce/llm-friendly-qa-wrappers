#!/usr/bin/env node

import * as prettier from "prettier";
import { readFileSync, writeFileSync, readdirSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { randomBytes } from "node:crypto";

const targets = process.argv.slice(2);

if (targets.length === 0) {
  process.stderr.write("❌ Prettier: No targets specified\n");
  process.stderr.write("   Usage: llm-prettier.js <path> [...paths]\n");
  process.exit(2);
}

const extensions = [".js", ".jsx", ".ts", ".tsx", ".json", ".css", ".md", ".html", ".yaml", ".yml"];

function walk(dir, files) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    if (entry.name.startsWith(".") || entry.name === "node_modules") continue;
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath, files);
    } else if (extensions.some((ext) => entry.name.endsWith(ext))) {
      files.push(resolve(fullPath));
    }
  }
}

try {
  const allFiles = [];

  for (const target of targets) {
    const stat = statSync(target, { throwIfNoEntry: false });
    if (!stat) continue;
    if (stat.isFile()) {
      allFiles.push(resolve(target));
    } else if (stat.isDirectory()) {
      walk(target, allFiles);
    }
  }

  if (allFiles.length === 0) {
    process.stderr.write("❌ Prettier: No supported files found\n");
    process.exit(2);
  }

  const fileResults = [];
  let unformattedCount = 0;

  for (const filePath of allFiles) {
    const source = readFileSync(filePath, "utf-8");
    const options = (await prettier.resolveConfig(filePath)) || {};
    options.filepath = filePath;

    const isFormatted = await prettier.check(source, options);

    if (!isFormatted) {
      unformattedCount++;
      fileResults.push({
        file_path: filePath,
        formatted: false,
      });
    } else {
      fileResults.push({
        file_path: filePath,
        formatted: true,
      });
    }
  }

  const prettierVersion = (
    await import("prettier/package.json", { with: { type: "json" } })
  ).default.version;

  const output = {
    tool: "prettier",
    version: prettierVersion,
    timestamp: new Date().toISOString(),
    exit_code: unformattedCount > 0 ? 1 : 0,
    command: `llm-prettier.js ${targets.join(" ")}`,
    summary: {
      total_files: allFiles.length,
      files_with_errors: unformattedCount,
      error_count: unformattedCount,
      warning_count: 0,
    },
    results: fileResults,
  };

  const tmpFile = join(
    tmpdir(),
    `prettier-${randomBytes(4).toString("hex")}.json`
  );
  writeFileSync(tmpFile, JSON.stringify(output, null, 2));

  if (unformattedCount === 0) {
    process.stdout.write(
      `✅ Prettier: All ${allFiles.length} files formatted (details: ${tmpFile})\n`
    );
    process.exit(0);
  } else {
    process.stdout.write(
      `❌ Prettier: ${unformattedCount} of ${allFiles.length} files need formatting\n`
    );
    const topFiles = fileResults.filter((f) => !f.formatted).slice(0, 3);
    for (const f of topFiles) {
      process.stdout.write(`   - ${f.file_path}\n`);
    }
    process.stdout.write(`   (details: ${tmpFile})\n`);
    process.exit(1);
  }
} catch (err) {
  process.stderr.write(`❌ Prettier: Execution error - ${err.message}\n`);
  process.exit(2);
}
