import json
import os
import boto3
import re
import uuid
import base64
from datetime import datetime


# error_response
def error_response(status, message):
    return {
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps({"error": message}),
    }
    
    
#CORS HEADERs

default_headers = {
    "access-control-allow-origin": "*",
    "access-control-allow-methods": "OPTIONS,POST,GET",
    "access-control-allow-headers": "Content-Type",
    "Content-Type": "application/json"
}

def handler(event, context):
    try:
        method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
        if method == "OPTIONS":
            return {"statusCode": 200, "headers": default_headers, "body": json.dumps({"ok": True})}

        # parsear body

        body_raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            body_raw = base64.b64decode(body_raw).decode("utf-8")
        body = json.loads(body_raw)

        # datos de entrada :)

        required_fields = ["email", "password", "phone", "client"]
        for f in required_fields:
            if f not in body:
                return error_response(400, f"missing required field: {f}")

        email = str(body["email"]).strip()
        password = str(body["password"])
        phone = str(body["phone"]).strip()
        client_val = body["client"]
        client = (
            client_val if isinstance(client_val, bool)
            else str(client_val).lower() in {"true", "1", "yes", "si"}
        )

        # validar algunos datos :)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return error_response(400, "invalid email format")
        if len(password) < 8:
            return error_response(400, "password must be at least 8 characters long")
        if not phone.startswith("+"):
            phone = "+57" + phone  # solo numero de colombia

        # configurar cognito

        region = os.getenv("AWS_REGION", "us-east-1")
        client_id = os.getenv("COGNITO_CLIENT_ID")
        user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        if not client_id or not user_pool_id:
            return error_response(500, "missing cognito configuration")

        cognito = boto3.client("cognito-idp", region_name=region)

        # verificar si el usuario ya existe

        try:
            cognito.admin_get_user(UserPoolId=user_pool_id, Username=email)
            return error_response(400, "user already exists")

        except cognito.exceptions.UserNotFoundException:
            pass  # pasa

        # sign up

        cognito.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {"Name": "email", "Value": email},
                {"Name": "custom:phone", "Value": phone},
                {"Name": "custom:client", "Value": str(client).lower()},
            ]
        )

        # confirmar cliente

        user_data = cognito.admin_get_user(UserPoolId=user_pool_id, Username=email)
        if user_data.get("UserStatus") != "CONFIRMED":
            cognito.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=email)

        # obtener sub(id_user)

        user_data = cognito.admin_get_user(UserPoolId=user_pool_id, Username=email)
        attrs = {a["Name"]: a["Value"] for a in user_data.get("UserAttributes", [])}
        id_user = attrs.get("sub")

        # guardar en tabla de cliente

        customers_table = os.getenv("CUSTOMERS_TABLE_NAME")
        if not customers_table:
            return error_response(500, "Missing customer_table_name env var")

        dynamodb = boto3.resource("dynamodb", region_name=region)
        table = dynamodb.Table(customers_table)

        customer_item = {
            "id_customer": str(uuid.uuid4(), ),
            "id_user": id_user,
            "email": email,
            "phone": phone,
            "is_customer": "true" if client else "false",
            "created_at": datetime.utcnow().isoformat(),
            "status": "active",
        }

        table.put_item(Item=customer_item)

        # respuesta

        return {
            "statusCode": 201,
            "headers": default_headers,
            "body": json.dumps({
                "message": "customer registered succesfully",
                "id_user": id_user,
                "id_customer": customer_item["id_customer"]
            }),
        }

    except Exception as e:
        print("unhandled error", repr(e))
        return error_response(500, "internal server error")

            
 
        