import json
import boto3
import os
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
        print("DEBUG: Event recibido:", event)

        # Manejar CORS
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": default_headers,
                "body": json.dumps({"message": "CORS ok"})
            }

        # Obtener user_id (puede venir del query o del body)
        user_id = None
        if "queryStringParameters" in event and event["queryStringParameters"]:
            user_id = event["queryStringParameters"].get("user_id")

        # Intentar obtener desde el body (por compatibilidad con pruebas POST)
        if not user_id and "body" in event and event["body"]:
            try:
                body = json.loads(event["body"])
                user_id = body.get("user_id")
            except Exception:
                pass

        # En el futuro, lo obtendremos desde Cognito (claims["sub"])
        if not user_id:
            return response(400, {"error": "user_id requerido"})

        # Escanear citas del usuario
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

def response(status, body):
    return {
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps(body)
    }
