# 1. Definición del Alcance
El servicio de MFA permitirá a los usuarios proteger sus cuentas con una segunda capa de autenticación, además de la contraseña. Los factores comunes serían:

- **OTP (One-Time Password)** generado por una aplicación como Google Authenticator o Authy.
- **Autenticación vía SMS o correo electrónico** con un código temporal.
- **Push notifications** (opcional si decides integrarlo más adelante).

# Diseño de la Arquitectura
La arquitectura para un servicio de MFA podría ser la siguiente:

- **FastAPI como servidor principal:** Proporcionará las rutas necesarias para gestionar la autenticación, verificación de códigos y configuración del segundo factor.
- **Base de Datos:** Para almacenar usuarios y detalles relacionados con la autenticación multifactor, como el secreto compartido para generar TOTP (para Google Authenticator) o tokens de recuperación.
- **Redis o Cache (opcional):** Para almacenar temporalmente los códigos de verificación de SMS o correo, y las sesiones de MFA para una experiencia más rápida.
- **Integraciones externas:**
  - **Twilio** o un servicio similar para enviar SMS.
  - **SendGrid** o un servicio de correo electrónico para enviar códigos por correo.
  - **PyOTP** para generar y verificar códigos TOTP.

# 3. Flujo de Usuario
El flujo para un usuario sería algo así:

1. Registro de MFA:
   - El usuario se registra normalmente en el sistema (si no está registrado).
   - En la página de configuración de seguridad, el usuario puede optar por activar MFA.
   - Se genera un código QR que contiene un secreto TOTP, que el usuario escaneará con una aplicación de autenticación como Google Authenticator.
   - Se guarda el secreto en la base de datos asociado al usuario.
2. Inicio de Sesión con MFA:
   - El usuario ingresa su usuario y contraseña como siempre.
   - El servidor verifica la contraseña. Si es correcta, solicita el segundo factor.
   - Dependiendo del método activado (TOTP, SMS o correo), se le solicita al usuario ingresar el código recibido/generado.
   - El código se verifica, y si es correcto, el usuario es autenticado.
3. Recuperación de cuenta:
   - Si el usuario pierde acceso a su dispositivo de MFA, puede tener configurados métodos alternativos como enviar el código a su correo o recuperar la cuenta con preguntas de seguridad u otro mecanismo.
# 4. Tecnologías y Librerías Clave
- FastAPI: Para la creación de la API y manejo de las rutas de autenticación.
- PyOTP: Esta librería permite generar y verificar códigos TOTP, lo cual es ideal para integrar con Google Authenticator o Authy.
  - Ejemplo: otp = pyotp.TOTP(secret_key).now()
- Twilio o SendGrid: Para enviar mensajes SMS o correos electrónicos con los códigos.
- Passlib: Para manejar el hashing seguro de contraseñas (si aún no tienes un sistema de autenticación robusto).
- SQLAlchemy o Tortoise ORM: Para el manejo de la base de datos.

# 5. Endpoints Propuestos

## Autenticación del Cliente (API Keys / OAuth)

POST /auth

Este endpoint permitirá que las aplicaciones de terceros se autentiquen con tu servicio para obtener un token de acceso.

Request:
```json
{
  "client_id": "app123",
  "client_secret": "secret123"
}
```
Response:
```json
{
  "access_token": "abcd1234",
  "expires_in": 3600
}
```
## Registro de Usuario y Generación de Secreto TOTP

POST /mfa/register

Este endpoint permite que la aplicación de terceros registre a un usuario en tu servicio MFA y genere un secreto TOTP único para ese usuario.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123"
}
```
Response:
```json
{
  "qr_code_url": "https://mfa.example.com/qrcode/user123",
  "secret": "JBSWY3DPEHPK3PXP"
}
```

## Generación de Código MFA

POST /mfa/generate

Este endpoint permite a una aplicación de terceros generar un código MFA para un usuario en caso de que el usuario solicite o si pierde acceso al dispositivo.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123"
}
```

Response:
```json
{
    "code": "123456"
}
```

## Solicitud de Código MFA por SMS

POST /mfa/sms

Este endpoint permite a una aplicación de terceros enviar un código MFA por SMS para un usuario en caso de que el usuario solicite o si pierde acceso al dispositivo.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123"
}
```
## Solicitud de Código MFA por Mail

POST /mfa/email

Este endpoint permite a una aplicación de terceros enviar un código MFA por correo para un usuario en caso de que el usuario solicite o si pierde acceso al dispositivo.

Request:
```json
{
    "user_id": "user123",
    "client_id": "app123"
}
```
s
## Verificación del Código MFA

POST /mfa/verify

Este endpoint es utilizado por la aplicación de terceros para verificar el código TOTP ingresado por el usuario durante el proceso de autenticación.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123",
  "code": "123456"
}
```
Response:

```json
{
  "status": "success",
  "message": "Code verified successfully"
}
```
O en caso de error:
```json
{
  "status": "failure",
  "message": "Invalid code"
}
```

## Desactivar MFA para un Usuario

POST /mfa/disable

Este endpoint permite a una aplicación de terceros desactivar MFA para un usuario en caso de que el usuario lo solicite o si pierde acceso al dispositivo.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123"
}
```

Response:
```json
{
  "status": "success",
  "message": "MFA disabled for user"
}
```

## Restablecimiento de MFA (Recuperación de Cuenta)

POST /mfa/recovery

Este endpoint permite a la aplicación de terceros solicitar un método alternativo de autenticación (por ejemplo, un código temporal enviado por SMS o correo electrónico) en caso de que el usuario pierda acceso a su aplicación MFA.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123",
  "recovery_method": "email"  // Puede ser "email", "sms", etc.
}
```

Response:
```json
{
  "status": "success",
  "message": "Recovery code sent to user"
}
```

## Consulta del Estado de MFA

GET /mfa/status

Permite a una aplicación de terceros consultar si un usuario tiene MFA activado.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123"
}
```

Response:
```json
{
  "mfa_enabled": true
}
```

## Renovación del Secreto TOTP

POST /mfa/renew

Permite generar un nuevo secreto TOTP para un usuario en caso de que necesite cambiar su dispositivo o restablecer la aplicación MFA.

Request:
```json
{
  "user_id": "user123",
  "client_id": "app123"
}
```

Response:
```json
{
  "qr_code_url": "https://mfa.example.com/qrcode/user123",
  "secret": "NEWSECRET123"
}
```

##Revocación de Token de Acceso (para el Cliente)

POST /auth/revoke

Permite que una aplicación de terceros revoque su token de acceso para finalizar la sesión con tu microservicio.

Request:
```json
{
  "access_token": "abcd1234"
}
```
Response:
```json
{
  "status": "success",
  "message": "Token revoked"
}
```


# 6. Consideraciones de Seguridad
- Almacenamiento del secreto TOTP: Los secretos compartidos para TOTP deben almacenarse de forma segura (encriptados en la base de datos).
- Protección contra ataques de fuerza bruta: Implementar bloqueo temporal de cuentas después de varios intentos fallidos en el ingreso de códigos MFA.
- HTTPS obligatorio: Para garantizar que todas las comunicaciones (incluidos los códigos MFA) estén cifradas.
# 7. Extensiones y Mejoras Futuras
- Push Notifications: Para una experiencia más fluida en lugar de enviar códigos, podrías integrar push notifications (con servicios como Firebase) que envíen solicitudes de autenticación al teléfono.
- Recuperación sin MFA: Un sistema robusto de recuperación que permita a los usuarios recuperar sus cuentas sin MFA (ej. preguntas de seguridad o enlaces de recuperación de cuenta).
# 8. Ejemplo de Código

Aquí un pequeño ejemplo de cómo generar un código TOTP:

```python
import pyotp
import qrcode
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Guardar el secreto de cada usuario en la base de datos (esto es solo un ejemplo)
user_secrets = {"user1": "JBSWY3DPEHPK3PXP"}

@app.get("/generate-mfa/{username}")
def generate_mfa(username: str):
    secret = user_secrets.get(username)
    if not secret:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    otp = pyotp.TOTP(secret)
    uri = otp.provisioning_uri(username, issuer_name="MiApp")

    # Genera un código QR que el usuario puede escanear
    img = qrcode.make(uri)
    img.save(f"{username}_qrcode.png")
    return {"message": "QR generado", "qr_code": f"{username}_qrcode.png"}

@app.post("/verify-mfa/{username}")
def verify_mfa(username: str, mfa_code: str):
    secret = user_secrets.get(username)
    if not secret:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    otp = pyotp.TOTP(secret)
    if otp.verify(mfa_code):
        return {"message": "Código MFA verificado"}
    else:
        raise HTTPException(status_code=400, detail="Código incorrecto")
        
```
Este código demuestra cómo generar un código QR para TOTP y verificarlo.

# 9. Conclusiones y Despliegue

Finalmente, podrías desplegar este servicio en una infraestructura con contenedores (Docker) y usar Kubernetes o un servicio como AWS para garantizar la escalabilidad. También sería buena idea usar un API Gateway para administrar las rutas de autenticación entre microservicios.


___

## Referencias

Tools and libraries used in this project:
- [FastAPI](https://fastapi.tiangolo.com/)
- [PyOTP](https://pyotp.readthedocs.io/en/latest/)
- [Twilio](https://www.twilio.com/)
- [SendGrid](https://sendgrid.com/)
- [Passlib](https://passlib.readthedocs.io/en/stable/)
- [SQLAlchemy](https://docs.sqlalchemy.org/en/14/)
- [Redis](https://redis.io/)
- [Redis-py](https://redis-py.readthedocs.io/en/latest/)
- [pydantic](https://docs.pydantic.dev/latest/api/)
- [sqlmodel](https://sqlmodel.tiangolo.com/)

Articles and tutorials used in this project:

- [Securing Digital Assets with MFA and Python](https://medium.com/@diego_maia/securing-digital-assets-with-mfa-and-python-generating-time-based-one-time-passwords-totps-143f4ea06955)
- [How Time-base One-Time Passwords work and why you should use them in your app.](https://www.freecodecamp.org/news/how-time-based-one-time-passwords-work-and-why-you-should-use-them-in-your-app-fdd2b9ed43c3/)
- [Fastapi, a deep dive into clean code](https://medium.com/@dhruvahuja2330/fastapi-application-a-deep-dive-into-clean-code-folder-structure-and-database-integration-7a172417cae2)
- [why fastapi is not production ready yet](https://python.plainenglish.io/this-is-why-fastapi-is-not-production-ready-yet-6c707823bd7c)
- [how to structure your fastapi projects](https://medium.com/@amirm.lavasani/how-to-structure-your-fastapi-projects-0219a6600a8f)