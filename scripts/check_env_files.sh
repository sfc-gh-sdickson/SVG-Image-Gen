#!/bin/bash
# Check for .env files in project directory
# This script prevents .env files from being committed to version control

if find . -name ".env" -not -path "./.venv/*" -not -path "./.git/*" | grep -q .; then
    echo "ERROR: .env files found in project directory. Use config.example.env as template and never commit .env files."
    exit 1
fi
