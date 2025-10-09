import json
import boto3
from botocore.exceptions import ClientError
import os

default_header = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*"
}

def handler(event, context):
    print("DEBUG: Event:", json.dumps(event))

    # Manejo de preflight CORS
    if event.get("httpMethod") == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": default_header,
            "body": json.dumps({"message": "CORS preflight ok"})
        }

    # ✅ Manejo universal del body
    body = event.get("body", {})
    if isinstance(body, str):
        body = json.loads(body)

    try:
        email = body.get("email")
        code = body.get("code")

        if not email or not code:
            return response(400, {"error": "Faltan parámetros: email o code"})

        client = boto3.client("cognito-idp")
        client_id = os.environ["COGNITO_CLIENT_ID"]

        # ✅ Llamada correcta a Cognito
        client.confirm_sign_up(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=code
        )

        return response(200, {"message": "Cuenta confirmada correctamente"})

    except ClientError as e:
        print("ERROR:", e)
        error_code = e.response["Error"]["Code"]

        if error_code == "CodeMismatchException":
            return response(400, {"error": "Código incorrecto"})
        elif error_code == "ExpiredCodeException":
            return response(400, {"error": "Código expirado"})
        elif error_code == "NotAuthorizedException":
            return response(400, {"error": "El usuario ya fue confirmado"})
        elif error_code == "UserNotFoundException":
            return response(404, {"error": "Usuario no encontrado"})
        else:
            return response(500, {"error": f"Error inesperado: {str(e)}"})

    except Exception as e:
        print("ERROR INESPERADO:", e)
        return response(500, {"error": f"Error inesperado: {str(e)}"})


def response(status, body):
    return {
        "statusCode": status,
        "headers": default_header,
        "body": json.dumps(body)
    }
