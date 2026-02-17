<?php

declare(strict_types=1);

use PHPUnit\Framework\TestCase;

class CalculatorTest extends TestCase
{
    public function testAdd(): void
    {
        $calc = new Calculator();
        $this->assertSame(4, $calc->add(2, 2));
    }

    public function testSubtract(): void
    {
        $calc = new Calculator();
        $this->assertSame(0, $calc->subtract(2, 2));
    }
}
