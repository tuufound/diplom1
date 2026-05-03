#!/usr/bin/env bash
# Создаёт .env.lan в корне репозитория (Linux / macOS / WSL).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/.env.lan"

pick_ip() {
  if command -v hostname >/dev/null 2>&1 && hostname -I >/dev/null 2>&1; then
    # Linux / WSL
    for ip in $(hostname -I); do
      case "$ip" in
        192.168.*|10.*|172.1[6-9].*|172.2[0-9].*|172.3[0-1].*) echo "$ip"; return 0 ;;
      esac
    done
    echo "$(hostname -I | awk '{print $1}')"
    return 0
  fi
  if command -v ip >/dev/null 2>&1; then
    ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") {print $(i+1); exit}}'
    return 0
  fi
  return 1
}

IP="$(pick_ip || true)"
if [[ -z "${IP:-}" ]]; then
  echo "Не удалось определить IPv4. Скопируйте lan-access.env.example в .env и подставьте IP." >&2
  exit 1
fi

ALLOWED="localhost,127.0.0.1,backend,$IP"
CSRF="http://$IP:3000"
cat >"$OUT" <<EOF
# Автоматически сгенерировано scripts/write-lan-env.sh
DJANGO_ALLOWED_HOSTS=$ALLOWED
DJANGO_CSRF_TRUSTED_ORIGINS=$CSRF
VITE_API_BASE_URL=http://localhost:8000/api
VITE_PROXY_TARGET=http://backend:8000
EOF
echo "Записан $OUT (LAN IP: $IP). На телефоне: http://$IP:3000"
