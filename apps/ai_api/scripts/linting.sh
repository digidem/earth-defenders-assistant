#! /usr/bin/env bash

set -xe

uvx isort .

uvx mypy --install-types --non-interactive eda_ai_api/

uvx mypy eda_ai_api

uvx black eda_ai_api --line-length 88

uvx flake8 eda_ai_api

uvx bandit -r eda_ai_api/
