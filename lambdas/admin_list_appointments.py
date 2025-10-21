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

        if event.get("httpMethod") == "OPTIONS":
            return response(200, {"message": "CORS ok"})

        #  Obtener rol desde el token de Cognito
        claims = get_claims(event)
        role = claims.get("custom:role") if claims else None

        if role != "barber":
            return response(403, {"error": "Acceso denegado. Solo el barbero puede ver todas las citas."})

        # Obtener parámetro 'date'
        params = event.get("queryStringParameters", {}) or {}
        date_str = params.get("date")

        if not date_str:
            return response(400, {"error": "El parámetro 'date' es requerido. Ejemplo: ?date=2025-10-22"})

        # Buscar citas del día
        result = table_appointments.scan(
            FilterExpression=Attr("date").eq(date_str)
        )

        appointments = result.get("Items", [])
        appointments.sort(key=lambda x: x.get("hour", ""))

        grouped = {
            "scheduled": [a for a in appointments if a.get("status") == "scheduled"],
            "cancelled": [a for a in appointments if a.get("status") == "cancelled"],
            "completed": [a for a in appointments if a.get("status") == "completed"]
        }

        return response(200, {
            "date": date_str,
            "total": len(appointments),
            "appointments": appointments,
            "grouped": grouped
        })

    except Exception as e:
        print("ERROR:", str(e))
        return response(500, {"error": f"Error interno: {str(e)}"})


def get_claims(event):
    
    """Decodifica el token o extrae claims desde API Gateway Authorizer"""

    claims = event.get("requestContext", {}).get("authorizer", {}).get("claims")
    if claims:
        return claims

    # Si se prueba directo desde Function URL o Postman
    headers = event.get("headers", {})
    token = headers.get("Authorization") or headers.get("authorization")
    if not token:
        return None

    token = token.replace("Bearer ", "").strip()
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded
    except Exception as e:
        print("Error decodificando token:", str(e))
        return None


def response(status, body):
    return {
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps(body)
    }
