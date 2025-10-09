import json, os, base64, re, boto3
from botocore.exceptions import ClientError

# Headers CORS
default_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json",
}

def resp(status, body):
    return {"statusCode": status, "headers": default_headers, "body": json.dumps(body)}

def handler(event, context):
    try:
        # Manejar preflight CORS
        method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
        if method == "OPTIONS":
            return resp(200, {"ok": True})

        # Leer body
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode("utf-8")
        body = json.loads(raw if isinstance(raw, str) else json.dumps(raw))

        # Campos requeridos
        for f in ["email", "password", "phone", "client"]:
            if f not in body:
                return resp(400, {"error": f"missing required field: {f}"})

        email = str(body["email"]).strip()
        password = str(body["password"]).strip()
        phone = str(body["phone"]).strip()
        client = body["client"]

        # Validaciones
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return resp(400, {"error": "invalid email format"})
        if len(password) < 8:
            return resp(400, {"error": "password must be at least 8 characters long"})
        if not phone.startswith("+"):
            phone = "+57" + phone  # prefijo Colombia

        region = os.getenv("AWS_REGION", "us-east-1")
        client_id = os.getenv("COGNITO_CLIENT_ID")
        user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        if not client_id or not user_pool_id:
            return resp(500, {"error": "missing cognito configuration"})

        cognito = boto3.client("cognito-idp", region_name=region)

        # Validar si ya existe
        try:
            cognito.admin_get_user(UserPoolId=user_pool_id, Username=email)
            return resp(400, {"error": "user already exists"})
        except cognito.exceptions.UserNotFoundException:
            pass

        # Crear usuario en Cognito
        try:
            cognito.sign_up(
                ClientId=client_id,
                Username=email,
                Password=password,
                UserAttributes=[
                    {"Name": "email", "Value": email},
                    {"Name": "phone_number", "Value": phone},
                    # {"Name": "custom:client", "Value": str(bool(client)).lower()},  # si tienes schema custom
                ],
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            print("SignUp ERROR:", e.response)
            if code == "UsernameExistsException":
                return resp(400, {"error": "user already exists"})
            return resp(500, {"error": f"cognito sign_up failed: {code}"})

        # Confirmar (opcional, solo si quieres que quede activo de una)
        try:
            cognito.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=email)
        except ClientError as e:
            print("Confirm ERROR:", e.response)
            # Si no tienes permiso, el usuario quedará "UNCONFIRMED" y usará el flujo de código.

        return resp(201, {
            "message": "user registered successfully",
            "email": email
        })

    except Exception as e:
        print("UNHANDLED ERROR:", repr(e))
        return resp(500, {"error": "internal server error"})
