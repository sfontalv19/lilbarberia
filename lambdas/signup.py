import json, os, base64, re, boto3
from botocore.exceptions import ClientError

REGION = os.getenv("AWS_REGION", "us-east-1")
COGNITO_CLIENT_ID = os.getenv("COGNITO_CLIENT_ID")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")

# Headers CORS actualizados
default_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token",
}

def resp(status, body):
    """Genera una respuesta HTTP con headers CORS"""
    return {
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps(body),
    }

def handler(event, context):
    try:
        # Manejo de preflight (CORS)
        method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
        if method == "OPTIONS":
            return resp(200, {"ok": True})

        # Leer body
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode("utf-8")
        body = json.loads(raw if isinstance(raw, str) else json.dumps(raw))

        # Validar campos requeridos
        for f in ["email", "password", "phone"]:
            if f not in body:
                return resp(400, {"error": f"missing required field: {f}"})

        email = str(body["email"]).strip()
        password = str(body["password"]).strip()
        phone = str(body.get("phone", "")).strip()
        client = body.get("client", True)

        # Validaciones
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return resp(400, {"error": "invalid email format"})
        if len(password) < 8:
            return resp(400, {"error": "password must be at least 8 characters long"})
        if not phone.startswith("+"):
            phone = "+57" + phone.lstrip("0").strip()  # prefijo Colombia

        # Validar configuración
        if not COGNITO_CLIENT_ID or not COGNITO_USER_POOL_ID:
            return resp(500, {"error": "missing cognito configuration"})

        # Cliente Cognito
        cognito = boto3.client("cognito-idp", region_name=REGION)

        # Verificar si ya existe
        try:
            cognito.admin_get_user(UserPoolId=COGNITO_USER_POOL_ID, Username=email)
            return resp(400, {"error": "user already exists"})
        except cognito.exceptions.UserNotFoundException:
            pass

        # Crear usuario
        try:
            cognito.sign_up(
                ClientId=COGNITO_CLIENT_ID,
                Username=email,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "phone_number", "Value": phone},
                ],
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            print("SignUp ERROR:", e.response)
            if code == "UsernameExistsException":
                return resp(400, {"error": "user already exists"})
            return resp(500, {"error": f"cognito sign_up failed: {code}"})

        return resp(201, {
            "message": "user registered and confirmed successfully",
            "email": email,
            "is_client": client
        })

    except Exception as e:
        print("UNHANDLED ERROR:", repr(e))
        return resp(500, {"error": "internal server error"})
