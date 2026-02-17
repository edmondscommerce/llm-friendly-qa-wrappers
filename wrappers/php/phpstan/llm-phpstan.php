<?php
/**
 * PHPStan wrapper using native JSON output (--error-format=json).
 *
 * PHPStan provides rich JSON output natively, so we use it directly
 * rather than reconstructing JSON from the programmatic API.
 */

$targets = array_slice($argv, 1);

if (empty($targets)) {
    fwrite(STDERR, "❌ PHPStan: No targets specified\n");
    fwrite(STDERR, "   Usage: llm-phpstan.php <path> [...paths]\n");
    exit(2);
}

$wrapperDir = __DIR__;
$phpstanBin = $wrapperDir . '/vendor/bin/phpstan';

if (!file_exists($phpstanBin)) {
    fwrite(STDERR, "❌ PHPStan: Binary not found. Run composer install first.\n");
    exit(2);
}

$cmd = [
    $phpstanBin,
    'analyse',
    '--error-format=json',
    '--no-progress',
    '--no-ansi',
    '--no-interaction',
    ...$targets,
];

$process = proc_open(
    $cmd,
    [
        0 => ['pipe', 'r'],
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ],
    $pipes
);

if (!is_resource($process)) {
    fwrite(STDERR, "❌ PHPStan: Failed to start process\n");
    exit(2);
}

fclose($pipes[0]);
$stdout = stream_get_contents($pipes[1]);
fclose($pipes[1]);
$stderr = stream_get_contents($pipes[2]);
fclose($pipes[2]);
$exitCode = proc_close($process);

// PHPStan outputs JSON to stdout even on failure
$data = json_decode($stdout, true);

if ($data === null) {
    fwrite(STDERR, "❌ PHPStan: Failed to parse JSON output\n");
    if (!empty($stderr)) {
        fwrite(STDERR, "   " . trim($stderr) . "\n");
    }
    exit(2);
}

// Normalize: PHPStan outputs files as [] when empty, {} when populated.
// Force it to always be an object for consistent schema validation.
if (empty($data['files'])) {
    $data['files'] = new \stdClass();
}

// Write JSON to temp file
$tmpFile = tempnam(sys_get_temp_dir(), 'phpstan-') . '.json';
file_put_contents($tmpFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

$totalErrors = $data['totals']['errors'] ?? 0;
$fileErrors = $data['totals']['file_errors'] ?? 0;
$totalIssues = $totalErrors + $fileErrors;

if ($totalIssues === 0) {
    fwrite(STDOUT, "✅ PHPStan: 0 errors (details: {$tmpFile})\n");
    exit(0);
} else {
    fwrite(STDOUT, "❌ PHPStan: {$fileErrors} errors found\n");

    // Show up to 3 top errors from native output
    $shown = 0;
    if (!empty($data['files'])) {
        foreach ($data['files'] as $filePath => $fileData) {
            foreach ($fileData['messages'] as $msg) {
                if ($shown >= 3) break 2;
                fwrite(STDOUT, "   - {$filePath}:{$msg['line']} {$msg['message']}\n");
                $shown++;
            }
        }
    }

    fwrite(STDOUT, "   (details: {$tmpFile})\n");
    exit(1);
}
