# Despliegue de BibliotecaUN en AWS

Resultado: **https://biblioteca.jan-productions.com**

```
Navegador
   │ HTTPS (un solo dominio: sin CORS)
   ▼
CloudFront ── /*      → S3 privado (React compilado, solo CloudFront puede leerlo)
   └───────── /api/*  → API Gateway HTTP API → Lambda (Django + apig-wsgi)
                                                  │ dentro de la VPC del RDS
                                                  ▼
                                            RDS MySQL portafolio-db (SSL)
```

Todo lo de AWS está descrito en `backend/serverless.yml` (Infraestructura como Código):
un `serverless deploy` crea o actualiza la Lambda, el API, el bucket, CloudFront, el
certificado HTTPS, el registro DNS y la regla de red hacia el RDS. `serverless remove` lo borra.

> Todos los comandos son para **Git Bash**, desde la raíz del repo, con el perfil de AWS activo:
> `export AWS_PROFILE=todo`

---

## 1. Verificar permisos del usuario de AWS (2 min)

El usuario `todo-deployer` se creó para ToDoBackend. Este proyecto además crea Security Groups,
certificados, CloudFront y registros DNS. Revisa qué políticas tiene:

```bash
aws iam list-attached-user-policies --user-name todo-deployer
aws iam list-user-policies --user-name todo-deployer
```

Si en el paso 4 aparece `AccessDenied` / `is not authorized to perform`, el mensaje dice exactamente
qué acción falta (por ejemplo `ec2:CreateSecurityGroup`): agrégala a la política del usuario desde la
consola de IAM y vuelve a correr el deploy. (Lo correcto a futuro es un rol con permisos mínimos y
OIDC en GitHub Actions, como recomendó la revisión de ToDoBackend.)

## 2. Usuario de MySQL para la aplicación (5 min, en Workbench con el admin del RDS)

La app no debe usar el usuario de ningún integrante: tiene el suyo, con lo mínimo que necesita
(leer y escribir datos; no puede crear ni borrar tablas). Genera una contraseña larga:

```bash
python -c "import secrets; print(secrets.token_urlsafe(24))"
```

Y en Workbench:

```sql
CREATE USER 'app_biblioteca'@'%' IDENTIFIED BY '<LA CONTRASEÑA GENERADA>'
  REQUIRE SSL WITH MAX_USER_CONNECTIONS 10;
GRANT SELECT, INSERT, UPDATE, DELETE ON biblioteca.* TO 'app_biblioteca'@'%';
```

`MAX_USER_CONNECTIONS 10` limita cuántas conexiones puede abrir la Lambda aunque escale.

## 3. Guardar los secretos en SSM Parameter Store (3 min)

Los secretos no van en el repo ni en archivos: van cifrados (`SecureString`) en AWS y el deploy los
lee. `MSYS_NO_PATHCONV=1` es obligatorio en Git Bash: sin eso convierte `/bibliotecaun/...` en una
ruta de Windows (`C:/Program Files/Git/bibliotecaun/...`).

```bash
export MSYS_NO_PATHCONV=1
aws ssm put-parameter --region us-east-1 --type SecureString --name /bibliotecaun/prod/db_user     --value 'app_biblioteca'
aws ssm put-parameter --region us-east-1 --type SecureString --name /bibliotecaun/prod/db_password --value '<LA CONTRASEÑA DEL PASO 2>'
aws ssm put-parameter --region us-east-1 --type SecureString --name /bibliotecaun/prod/secret_key  --value "$(python -c 'import secrets; print(secrets.token_urlsafe(50))')"
```

Para cambiar un valor después: el mismo comando con `--overwrite`.

## 4. Desplegar el backend y la infraestructura (20–40 min la primera vez)

```bash
cd backend
source .venv/Scripts/activate      # Python 3.13: el plugin lo usa para armar el paquete
npm install                        # instala Serverless Framework v3 y el plugin de Python
npx serverless deploy
```

La primera vez tarda porque **CloudFront** se distribuye a todos sus puntos de presencia y el
**certificado** espera su validación por DNS (CloudFormation crea el registro solo en Route 53).
Las siguientes veces son 1–3 minutos.

Al terminar, comprueba la API a través del dominio:

```bash
curl -i https://biblioteca.jan-productions.com/api/auth/me/
```

Debe responder **401** con `{"detail": "Las credenciales de autenticación no se proveyeron."}`:
eso prueba DNS → HTTPS → CloudFront → API Gateway → Lambda → Django.

## 5. Desplegar el frontend (2 min)

```bash
cd ../frontend
bash desplegar.sh
```

Compila con `.env.production` (API en el mismo dominio), sube a S3 y limpia el caché de CloudFront.
Abre **https://biblioteca.jan-productions.com** e inicia sesión con
`admin.biblioteca@uninorte.edu.co` / `Admin123!`.

## Actualizar después de un cambio

| Cambió… | Comando |
|---|---|
| Código del backend (Python) | `cd backend && npx serverless deploy` |
| Código del frontend (React) | `cd frontend && bash desplegar.sh` |
| Datos o estructura de la BD | Scripts SQL en Workbench, como siempre |

## Diagnóstico

- **Ver errores de la Lambda en vivo:** `cd backend && npx serverless logs -f api --tail`
- **502/503 desde CloudFront:** la Lambda falló al arrancar. Los logs dicen por qué (casi siempre una
  variable de SSM mal escrita).
- **Timeout de ~28 s en cualquier petición:** la Lambda no llega al RDS. Revisa que exista la regla
  "MySQL desde la Lambda de BibliotecaUN" en el Security Group `sg-0706c4fb379e6c19b`.
- **`DisallowedHost` en los logs:** falta un dominio en `ALLOWED_HOSTS` (`serverless.yml`).
- **El certificado se queda "Pending validation" más de 30 min:** revisa que la zona
  `Z03822205GB25RP0AKE2` sea la que usa realmente el dominio (los NS del registrador).

## Costos (demo con poco tráfico; verifica en la AWS Pricing Calculator)

Lambda, API Gateway, CloudFront, S3 y SSM estándar quedan dentro de la capa gratuita o en centavos.
No se usa NAT Gateway ni RDS Proxy (los que suelen disparar la factura). El RDS ya existía.

## Plan B para la sustentación

Si algo falla en AWS, el proyecto corre igual en local (`python manage.py runserver` y
`npm run dev`) contra el mismo RDS.

## Borrar todo

```bash
cd backend
aws s3 rm "s3://$(aws cloudformation describe-stacks --stack-name bibliotecaun-prod --region us-east-1 --query "Stacks[0].Outputs[?OutputKey=='FrontBucketName'].OutputValue" --output text)" --recursive
npx serverless remove
```

Elimina la Lambda, el API, CloudFront, el bucket, el certificado, el registro DNS y la regla del
Security Group. El RDS y sus datos no se tocan.
