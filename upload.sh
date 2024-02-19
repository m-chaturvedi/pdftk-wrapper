#!/usr/bin/env bash
set -euo pipefail

python3 -m build
twine check dist/*
twine upload --verbose --repository testpypi dist/*
