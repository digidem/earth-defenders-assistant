#!/usr/bin/env bash

set -xe

uvx pytest -vv --cov=eda_ai_api --cov=tests --cov-report=term-missing --cov-report=xml tests/ ${@}
