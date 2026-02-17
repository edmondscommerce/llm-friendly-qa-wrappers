<?php
/**
 * PHP-CS-Fixer wrapper using native JSON output (--format=json).
 *
 * PHP-CS-Fixer provides JSON output natively, so we use it directly.
 * Uses --dry-run to check without modifying files.
 * Uses --verbose to include appliedFixers in output.
 */

$targets = array_slice($argv, 1);

if (empty($targets)) {
    fwrite(STDERR, "❌ PHP-CS-Fixer: No targets specified\n");
    fwrite(STDERR, "   Usage: llm-php-cs-fixer.php <path> [...paths]\n");
    exit(2);
}

$wrapperDir = __DIR__;
$fixerBin = $wrapperDir . '/vendor/bin/php-cs-fixer';

if (!file_exists($fixerBin)) {
    fwrite(STDERR, "❌ PHP-CS-Fixer: Binary not found. Run composer install first.\n");
    exit(2);
}

$cmd = [
    $fixerBin,
    'fix',
    '--dry-run',
    '--format=json',
    '--diff',
    '--verbose',
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
    fwrite(STDERR, "❌ PHP-CS-Fixer: Failed to start process\n");
    exit(2);
}

fclose($pipes[0]);
$stdout = stream_get_contents($pipes[1]);
fclose($pipes[1]);
$stderr = stream_get_contents($pipes[2]);
fclose($pipes[2]);
$exitCode = proc_close($process);

$data = json_decode($stdout, true);

if ($data === null) {
    fwrite(STDERR, "❌ PHP-CS-Fixer: Failed to parse JSON output\n");
    if (!empty($stderr)) {
        fwrite(STDERR, "   " . trim(preg_replace('/\x1b\[[0-9;]*m/', '', $stderr)) . "\n");
    }
    exit(2);
}

// Write JSON to temp file
$tmpFile = tempnam(sys_get_temp_dir(), 'php-cs-fixer-') . '.json';
file_put_contents($tmpFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

$fileCount = count($data['files'] ?? []);

if ($fileCount === 0) {
    fwrite(STDOUT, "✅ PHP-CS-Fixer: 0 files need fixing (details: {$tmpFile})\n");
    exit(0);
} else {
    fwrite(STDOUT, "❌ PHP-CS-Fixer: {$fileCount} files need fixing\n");

    // Show up to 3 files
    $shown = 0;
    foreach ($data['files'] as $file) {
        if ($shown >= 3) break;
        $fixerCount = count($file['appliedFixers'] ?? []);
        fwrite(STDOUT, "   - {$file['name']} ({$fixerCount} fixers)\n");
        $shown++;
    }

    fwrite(STDOUT, "   (details: {$tmpFile})\n");
    exit(1);
}
