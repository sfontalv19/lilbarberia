import json
import boto3
import os
import jwt
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
table_appointments = dynamodb.Table(os.environ.get("DYNAMODB_APPOINTMENTS_TABLE", "appointments"))

default_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "OPTIONS,GET",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
}

def handler(event, context):
    try:
        print("DEBUG: Event recibido:", json.dumps(event))

        # Manejo de CORS
        if event.get("httpMethod") == "OPTIONS":
            return response(200, {"message": "CORS ok"})

        # Obtener el user_id (sub) desde Cognito
        user_id = get_user_id_from_event(event)
        if not user_id:
            return response(401, {"error": "Usuario no autenticado o token inválido"})

        print(f"DEBUG: user_id autenticado -> {user_id}")

        # Buscar citas del usuario autenticado
        result = table_appointments.scan(
            FilterExpression=Attr("user_id").eq(user_id)
        )
        appointments = result.get("Items", [])

        # Ordenar por fecha y hora (ascendente)
        appointments.sort(key=lambda x: (x.get("date", ""), x.get("hour", "")))

        return response(200, {
            "user_id": user_id,
            "count": len(appointments),
            "appointments": appointments
        })

    except Exception as e:
        print("ERROR:", str(e))
        return response(500, {"error": f"Error interno: {str(e)}"})


#  Extraer el sub desde Cognito (funciona con o sin API Gateway Authorizer)
def get_user_id_from_event(event):
    # Si viene de API Gateway con authorizer
    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
    if claims and "sub" in claims:
        return claims["sub"]

    # Si estás probando directo desde Function URL o Postman, decodifica el token manualmente
    headers = event.get("headers", {})
    auth_header = headers.get("Authorization") or headers.get("authorization")
    if not auth_header:
        return None

    token = auth_header.replace("Bearer ", "").strip()
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("sub")
    except Exception as e:
        print("ERROR al decodificar token:", str(e))
        return None


def response(status, body):
    return {
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps(body)
    }
