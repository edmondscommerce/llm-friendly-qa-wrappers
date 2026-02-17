#!/bin/bash
set -euo pipefail

greeting="hello world"
  echo   "$greeting"

  count=0
for file in *.txt; do
count=$((count + 1))
    echo "Processing: $file"
done

echo "Processed $count files"
