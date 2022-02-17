#!/bin/bash

set -eu -o pipefail

# Ignore this check when in CI since there seems to be some bugs
[[ "${CI:-}" == "true" ]] || circleci config validate
