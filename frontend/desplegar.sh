#!/usr/bin/env bash
# Sube el front compilado a S3 y limpia el caché de CloudFront.
# Uso (desde frontend/, con el backend ya desplegado):   bash desplegar.sh
set -euo pipefail

STACK="bibliotecaun-prod"
REGION="us-east-1"
salida() {
  aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}

BUCKET="$(salida FrontBucketName)"
DISTRIBUCION="$(salida DistributionId)"
echo "Bucket: $BUCKET | CloudFront: $DISTRIBUCION"

cd "$(dirname "$0")"

# El build de producción debe llamar a la API en el MISMO dominio (/api/... relativo).
# Si .env.production no existe, Vite usaría .env (127.0.0.1:8000) y el sitio no funcionaría.
if ! grep -qx "VITE_API_URL=" .env.production 2>/dev/null; then
  echo "Falta frontend/.env.production con la línea exacta: VITE_API_URL=" >&2
  echo "Créalo con:  printf 'VITE_API_URL=\\n' > .env.production" >&2
  exit 1
fi

npm run build   # usa .env.production
if grep -rq "127.0.0.1:8000" dist; then
  echo "El build quedó apuntando a 127.0.0.1:8000; revisa .env.production" >&2
  exit 1
fi

# Archivos con hash en el nombre (assets/index-AbC123.js): se pueden cachear un año,
# porque cada build nuevo genera nombres nuevos.
aws s3 sync dist "s3://$BUCKET" --delete --exclude "index.html" \
  --cache-control "public,max-age=31536000,immutable"

# index.html nunca se cachea: así el navegador siempre ve la versión nueva.
aws s3 cp dist/index.html "s3://$BUCKET/index.html" --cache-control "no-cache"

aws cloudfront create-invalidation --distribution-id "$DISTRIBUCION" --paths "/index.html" "/" > /dev/null
echo "Listo: https://biblioteca.jan-productions.com"
