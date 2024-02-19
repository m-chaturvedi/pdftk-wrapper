#!/usr/bin/env bash
set -euo pipefail

twine upload --verbose --repository testpypi dist/*

