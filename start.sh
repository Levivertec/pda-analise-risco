#!/usr/bin/env bash
# Script de inicialização do app no Railway.
# - Recria .streamlit/secrets.toml a partir da variável de ambiente (Railway não
#   tem o arquivo de secrets; ele é injetado via env var STREAMLIT_SECRETS_TOML).
# - Sobe o Streamlit na porta fornecida pelo Railway ($PORT).
set -e

mkdir -p .streamlit

if [ -n "$STREAMLIT_SECRETS_TOML" ]; then
  printf '%s' "$STREAMLIT_SECRETS_TOML" > .streamlit/secrets.toml
  echo "[start.sh] secrets.toml gerado a partir de STREAMLIT_SECRETS_TOML"
else
  echo "[start.sh] AVISO: STREAMLIT_SECRETS_TOML nao definido — login nao vai funcionar"
fi

exec streamlit run app.py \
  --server.port "${PORT:-8501}" \
  --server.address 0.0.0.0 \
  --server.headless true
