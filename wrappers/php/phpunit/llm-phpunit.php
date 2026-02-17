<?php
/**
 * PHPUnit wrapper with custom JSON output.
 *
 * PHPUnit has no native JSON output mode. This wrapper uses --log-junit
 * to capture JUnit XML results and converts them to JSON.
 */

$targets = array_slice($argv, 1);

if (empty($targets)) {
    fwrite(STDERR, "❌ PHPUnit: No targets specified\n");
    fwrite(STDERR, "   Usage: llm-phpunit.php <path> [...paths]\n");
    exit(2);
}

$wrapperDir = __DIR__;
$phpunitBin = $wrapperDir . '/vendor/bin/phpunit';

if (!file_exists($phpunitBin)) {
    fwrite(STDERR, "❌ PHPUnit: Binary not found. Run composer install first.\n");
    exit(2);
}

$junitFile = tempnam(sys_get_temp_dir(), 'phpunit-junit-') . '.xml';

$cmd = [
    $phpunitBin,
    '--log-junit',
    $junitFile,
    '--no-progress',
    '--colors=never',
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
    fwrite(STDERR, "❌ PHPUnit: Failed to start process\n");
    exit(2);
}

fclose($pipes[0]);
$stdout = stream_get_contents($pipes[1]);
fclose($pipes[1]);
$stderr = stream_get_contents($pipes[2]);
fclose($pipes[2]);
$exitCode = proc_close($process);

// Parse JUnit XML
if (!file_exists($junitFile)) {
    fwrite(STDERR, "❌ PHPUnit: JUnit log not generated\n");
    if (!empty($stdout)) {
        fwrite(STDERR, "   " . trim(explode("\n", $stdout)[0] ?? '') . "\n");
    }
    if (!empty($stderr)) {
        fwrite(STDERR, "   " . trim(explode("\n", $stderr)[0] ?? '') . "\n");
    }
    exit(2);
}

$xml = @simplexml_load_file($junitFile);
@unlink($junitFile);

if ($xml === false) {
    fwrite(STDERR, "❌ PHPUnit: Failed to parse JUnit XML\n");
    exit(2);
}

// Convert JUnit XML to JSON
$rootSuite = $xml->testsuite;
$data = [
    'tool' => 'phpunit',
    'summary' => [
        'tests' => (int)$rootSuite['tests'],
        'assertions' => (int)$rootSuite['assertions'],
        'errors' => (int)$rootSuite['errors'],
        'failures' => (int)$rootSuite['failures'],
        'skipped' => (int)$rootSuite['skipped'],
        'time' => (float)$rootSuite['time'],
    ],
    'test_suites' => [],
];

function parseSuite(SimpleXMLElement $suite): array {
    $result = [
        'name' => (string)$suite['name'],
        'tests' => (int)$suite['tests'],
        'assertions' => (int)$suite['assertions'],
        'errors' => (int)$suite['errors'],
        'failures' => (int)$suite['failures'],
        'skipped' => (int)$suite['skipped'],
        'time' => (float)$suite['time'],
        'test_cases' => [],
    ];

    if (isset($suite['file'])) {
        $result['file'] = (string)$suite['file'];
    }

    foreach ($suite->testcase as $tc) {
        $case = [
            'name' => (string)$tc['name'],
            'class' => (string)$tc['class'],
            'file' => (string)$tc['file'],
            'line' => (int)$tc['line'],
            'assertions' => (int)$tc['assertions'],
            'time' => (float)$tc['time'],
            'status' => 'passed',
        ];

        if (isset($tc->failure)) {
            $case['status'] = 'failed';
            $case['failure'] = [
                'type' => (string)$tc->failure['type'],
                'message' => trim((string)$tc->failure),
            ];
        }

        if (isset($tc->error)) {
            $case['status'] = 'error';
            $case['error'] = [
                'type' => (string)$tc->error['type'],
                'message' => trim((string)$tc->error),
            ];
        }

        if (isset($tc->skipped)) {
            $case['status'] = 'skipped';
        }

        $result['test_cases'][] = $case;
    }

    // Recurse into nested testsuites
    foreach ($suite->testsuite as $child) {
        $childResult = parseSuite($child);
        $result['test_cases'] = array_merge($result['test_cases'], $childResult['test_cases']);
    }

    return $result;
}

// Parse all top-level testsuites
foreach ($rootSuite->testsuite as $suite) {
    $data['test_suites'][] = parseSuite($suite);
}

// Write JSON to temp file
$tmpFile = tempnam(sys_get_temp_dir(), 'phpunit-') . '.json';
file_put_contents($tmpFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));

$totalTests = $data['summary']['tests'];
$totalFailures = $data['summary']['failures'];
$totalErrors = $data['summary']['errors'];
$totalIssues = $totalFailures + $totalErrors;

if ($totalIssues === 0) {
    fwrite(STDOUT, "✅ PHPUnit: {$totalTests} tests passed (details: {$tmpFile})\n");
    exit(0);
} else {
    fwrite(STDOUT, "❌ PHPUnit: {$totalFailures} failures, {$totalErrors} errors in {$totalTests} tests\n");

    // Show up to 3 failing tests
    $shown = 0;
    foreach ($data['test_suites'] as $suite) {
        foreach ($suite['test_cases'] as $tc) {
            if ($shown >= 3) break 2;
            if ($tc['status'] === 'failed') {
                $msg = explode("\n", $tc['failure']['message'])[1] ?? $tc['failure']['message'];
                fwrite(STDOUT, "   - {$tc['class']}::{$tc['name']}: " . trim($msg) . "\n");
                $shown++;
            } elseif ($tc['status'] === 'error') {
                $msg = explode("\n", $tc['error']['message'])[0] ?? $tc['error']['message'];
                fwrite(STDOUT, "   - {$tc['class']}::{$tc['name']}: " . trim($msg) . "\n");
                $shown++;
            }
        }
    }

    fwrite(STDOUT, "   (details: {$tmpFile})\n");
    exit(1);
}
