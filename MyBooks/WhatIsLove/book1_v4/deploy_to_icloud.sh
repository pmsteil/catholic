#!/bin/bash

# fail if any error
set -e

bin/build audiomd --no-open

# Generate timestamp in format YY-MM-DD_HHMM
TIMESTAMP=$(date +"%y-%m-%d_%H%M")
NEW_FILENAME="WIL_${TIMESTAMP}.txt"

cp WhatIsLove_book.audiomd.md /Users/patiman/Library/Mobile\ Documents/com~apple~CloudDocs/GodIsLove/"${NEW_FILENAME}"
echo "Copied to iCloud: ${NEW_FILENAME}"
