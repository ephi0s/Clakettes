# Modelo de confianza entre nodos federados — Clakettes (Fase 2)

> Origen: `TASKS.md` Fase 2, ítem 2: "Diseñar modelo de confianza entre nodos aprovechando certificados TLS de dominio (CA pública o privada) como raíz de identidad".
> Estado: completado. Diseño técnico detallado; referencia `docs/es/FEDERATION_SECURITY.md`, `docs/es/FEDERATION_PROTOCOL.md`, `docs/es/AMENAZAS_NODOS_FEDERACION.md`.

## 1. Principio de identidad

La identidad de un nodo federado es la tupla **(nombre de dominio, certificado TLS X.509)**. No se confía en direcciones IP, ni en claves precompartidas, ni en firmas autogeneradas sin respaldo de una CA.

- **Dominio:** el `node_domain` declarado en el manifiesto del nodo y verificado contra el CN/SAN del certificado presentado durante el handshake mTLS.
- **Certificado TLS:** emitido por una CA de confianza (pública, p. ej. Let's Encrypt, o privada operada por la federación). El certificado vincula criptográficamente el dominio a una clave pública.
- **Raíz de confianza:** el certificado de la CA emisora (o su cadena completa) es el ancla de confianza. Un nodo solo acepta peering con otro si la cadena de certificados se valida contra su almacén de CA raíz.

## 2. Flujo de establecimiento de peering mutuo (mTLS)

```
Nodo A (cliente)                              Nodo B (servidor)
-----------                                   -----------
1. TLS handshake mTLS                         1. Presenta certificado de servidor
2. Presenta certificado de cliente              2. Solicita certificado de cliente
3. Valida cadena de B contra CA raíz            3. Valida cadena de A contra CA raíz
4. Extrae dominio del CN/SAN de B               4. Extrae dominio del CN/SAN de A
5. Verifica que dominio de B está en allowlist  5. Verifica que dominio de A está en allowlist
6. Descarga manifiesto de B                     6. Descarga manifiesto de A
7. Valida firma del manifiesto con la clave    7. Valida firma del manifiesto con la clave
    pública del cert de B                      pública del cert de A
8. Peering establecido                          8. Peering establecido
```

Ambos nodos actúan a la vez como cliente y servidor TLS (mTLS mutuo). Cada extremo valida al otro de forma independiente.

### 2.1 Validación de certificados (lado servidor y lado cliente)

1. **Cadena de confianza:** el certificado presentado debe encadenar hasta una CA raíz presente en el almacén de confianza del nodo receptor. Certificados self-signed son rechazados en producción (ver §6).
2. **Vigencia:** `notBefore` ≤ ahora ≤ `notAfter`.
3. **Revoked:** el número de serie del certificado no debe aparecer en la CRL de la CA ni fallar una consulta OCSP (si está configurada).
4. **Nombre de dominio:** el dominio del nodo debe coincidir con el CN o uno de los SANs (`dNSName`) del certificado.
5. **Uso de clave:** el certificado debe incluir `digitalSignature` y `keyEncipherment` (o `keyAgreement` para suites ECDHE) en `Key Usage`, y `TLS Web Server Authentication` / `TLS Web Client Authentication` en `Extended Key Usage`.

## 3. Identidad de nodo y manifiesto firmado

Cada nodo expone un manifiesto en `GET /api/federation/manifest`:

```json
{
  "schema_version": "1",
  "node": "festival-clakettes.example.com",
  "version": "1.0.0",
  "capabilities": ["festivals", "users", "chat", "voting"],
  "issued_at": "2026-11-16T10:00:00Z",
  "expires_at": "2026-11-16T10:00:00Z",
  "signature": "BASE64(Sign(priv_key_cert, payload))",
  "certificate_chain": ["BASE64(cert_nodo)", "BASE64(cert_intermedio)", "BASE64(cert_raiz)"]
}
```

### 3.1 Firma del manifiesto

- El manifiesto se firma con la **clave privada del certificado TLS del nodo** (la misma clave usada en el handshake mTLS).
- El payload firmado incluye `schema_version`, `node`, `version`, `capabilities`, `issued_at`, `expires_at`.
- La firma se codifica en Base64 URL-safe sin padding.
- `certificate_chain` incluye el certificado del nodo y, opcionalmente, la cadena hacia la raíz para permitir verificación offline.

### 3.2 Verificación del manifiesto por un nodo par

1. Descarga `manifest` del nodo remoto vía mTLS.
2. Extrae `certificate_chain[0]` (certificado del nodo) y valida su cadena contra la CA raíz.
3. Extrae el dominio del certificado y lo compara con `manifest.node`; deben coincidir exactamente.
4. Valida vigencia del manifiesto (`issued_at` ≤ ahora ≤ `expires_at`).
5. Verifica `signature` usando la clave pública del certificado del nodo sobre el payload canónico.
6. Si todo pasa, el nodo remoto se considera **identidad verificada**.

## 4. Almacén de nodos confiados (modelo de datos)

Tabla `trusted_nodes`:

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador interno |
| `node_domain` | String(255), unique, index | Dominio del nodo (ej. `festival.example.com`) |
| `cert_fingerprint_sha256` | String(64), unique, index | Huella SHA-256 del certificado TLS del nodo (identifica la clave pública) |
| `cert_subject_cn` | String(255) | CN del certificado |
| `cert_sans` | JSON | Lista de SANs del certificado |
| `issuer_ca` | String(255) | CA emisora del certificado |
| `not_before` | DateTime | Inicio de vigencia del certificado |
| `not_after` | DateTime | Fin de vigencia del certificado |
| `allowed` | Boolean, default true | Si el nodo está autorizado para peering |
| `consent_required` | Boolean, default true | Si se requiere consentimiento explícito para compartir datos |
| `minimize_data` | Boolean, default true | Si se aplica minimización de datos en peering |
| `capabilities` | JSON | Capacidades declaradas en el manifiesto |
| `last_seen_at` | DateTime, nullable | Último contacto exitoso |
| `created_at` | DateTime | Fecha de registro |
| `updated_at` | DateTime | Última actualización de política |

Tabla `node_peering_sessions` (auditoría de handshakes):

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | |
| `remote_domain` | String(255) | Dominio del nodo remoto |
| `remote_ip` | String(45) | IP desde la que se conectó |
| `cert_fingerprint` | String(64) | Huella del cert presentado |
| `validated` | Boolean | Si la validación de cadena+dominio pasó |
| `reason` | String(255), nullable | Motivo de rechazo si no validó |
| `created_at` | DateTime | Timestamp del intento |

## 5. Rotación y revocación

### 5.1 Rotación por renovación de certificado

Cuando un nodo renueva su certificado TLS (misma clave o nueva clave, misma CA):

1. El nodo presenta el nuevo certificado en el próximo handshake mTLS.
2. El par valida la cadena contra la CA raíz (el nuevo certificado encadena hasta la misma raíz).
3. Se actualiza `cert_fingerprint_sha256`, `not_before`, `not_after` en `trusted_nodes`.
4. El manifiesto se vuelve a firmar con la clave del nuevo certificado y se redistribuye.

No es necesario reconfigurar manualmente la allowlist: la raíz de confianza es la CA, no el certificado individual.

### 5.2 Revocación

Un nodo se revoca cuando:

- Su certificado expira y no se renueva (`not_after` pasado).
- La CA emite una CRL que incluye el número de serie del certificado.
- Un administrador marca `allowed = false` en `trusted_nodes` (revocación administrativa inmediata).
- El nodo es comprometido: se invalida su entrada en el directorio y se añade su dominio a la blocklist.

En todos los casos, el siguiente handshake mTLS falla en la validación de cadena o de dominio, y el peering se cae.

## 6. Requisitos de TLS entre nodos

| Entorno | Requisito |
|---|---|
| Producción | TLS 1.2 mínimo (recomendado 1.3), mTLS obligatorio, CA pública o privada de confianza, **prohibido self-signed**, `FORWARDED_ALLOW_IPS` definido, uvicorn con `--proxy-headers`. |
| Desarrollo | Se permite CA local autofirmada solo para pruebas; nunca en producción. |

### 6.1 Configuración del servidor (Nodo B)

```python
# uvicorn --ssl-certfile=/path/to/fullchain.pem --ssl-keyfile=/path/to/privkey.pem
# ssl_cert_reqs=CERT_REQUIRED (exige certificado de cliente)
# ssl_ca_certs=/path/to/ca-bundle.pem (CA raíz de confianza para validar clientes)
```

### 6.2 Configuración del cliente (Nodo A)

```python
# httpx.Client(verify=/path/to/ca-bundle.pem, cert=(/path/to/cert.pem, /path/to/key.pem))
```

## 7. Endpoints afectados y nuevos

### 7.1 Endpoints existentes a endurecer (`backend/app/routers/federation.py`)

| Endpoint | Cambio requerido |
|---|---|
| `GET /api/federation/manifest` | Incluir `signature`, `certificate_chain`, `issued_at`, `expires_at`. Firmar con clave privada del cert TLS del nodo. |
| `GET /api/federation/directory` | Devolver solo nodos de `trusted_nodes` con `allowed = true`, incluyendo `cert_fingerprint_sha256` y `capabilities`. |
| `GET /api/federation/nodes` | Leer/escribir políticas desde `trusted_nodes` (ya existe `NodePolicyService`; migrar a la nueva tabla). |
| `GET /api/federation/users/{ref}` | Requerir autenticación mTLS + nodo remoto en `trusted_nodes`. |
| `GET /.well-known/webfinger` | Requerir autenticación mTLS + nodo remoto en `trusted_nodes`. |

### 7.2 Nuevos endpoints

| Endpoint | Método | Descripción |
|---|---|---|
| `POST /api/federation/peers/verify` | POST | Recibe un manifiesto remoto, valida firma+y cert, devuelve si el nodo es de confianza. |
| `GET /api/federation/.well-known/jwks.json` | GET | Claves públicas del nodo (JWKS) para verificación de tokens de pares. |
| `POST /api/federation/peers/{domain}/revoke` | POST | Marca `allowed = false` en `trusted_nodes` (revocación administrativa). |

## 8. Integración con middleware de seguridad existente

- `RateLimitMiddleware` (`main.py:224-261`): los handshakes mTLS fallan antes de llegar a HTTP, por lo que el rate limiting por IP se aplica a los requests HTTP posteriores, no al handshake TLS. Considerar rate limiting a nivel de balanceador de proxy TLS.
- `SecurityHeadersMiddleware` (`main.py:124-152`): se aplica a las respuestas HTTP de los endpoints de federación.
- `_validate_secret_key` (`main.py:83-118`: sigue validando `SECRET_KEY` y `CORS_ORIGINS` en producción.

## 9. Riesgos residuales tras este diseño

| Riesgo | Mitigación |
|---|---|
| CA privada comprometida | Rotar la CA raíz, reemitir todos los certificados de nodo, actualizar almacenes de confianza. |
| Certificado válido pero nodo comprometido | Revocación administrativa (`allowed = false`) + CRL/OCSP. |
| Ataque de repetición de manifiesto | `expires_at` corto (máximo 24 h) + `issued_at` + nonce opcional en handshake. |
| Dominio cuyo certificado se reemite a otro atacante (CA comprometida) | Pinado opcional de `cert_fingerprint_sha256` además de validación de CA. |

## 10. Referencias

- `docs/es/FEDERATION_SECURITY.md` — modelo de confianza, mTLS, rotación/revocación por certificado.
- `docs/es/FEDERATION_PROTOCOL.md` — pasos de interoperabilidad (manifest, directory, JWKS, webfinger, Schema v1).
- `docs/es/FEDERATION_SCHEMA.md` — Clakettes Schema v1, entidades y endpoints de federación.
- `docs/es/AMENAZAS_NODOS_FEDERACION.md` — amenazas A1 (suplantación de nodo) y A2 (intercepción DAV) mitigadas por este modelo.
