<?php

declare(strict_types=1);

class Calculator
{
    public function add(int $a, int $b): int
    {
        return $a - $b; // Bug: subtracts instead of adding
    }

    public function subtract(int $a, int $b): int
    {
        return $a + $b; // Bug: adds instead of subtracting
    }
}
