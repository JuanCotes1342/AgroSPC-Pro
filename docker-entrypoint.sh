#!/bin/sh
set -e

# Railway puede conservar variables configuradas manualmente. Streamlit falla si
# STREAMLIT_SERVER_PORT llega como el texto literal "$PORT".
unset STREAMLIT_SERVER_PORT

exec "$@"
