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

        # Obtener parámetros
        params = event.get("queryStringParameters", {}) or {}
        date_str = params.get("date")

        if not date_str:
            return response(400, {"error": "El parámetro 'date' es requerido. Ejemplo: ?date=2025-10-22"})

        # Consultar DynamoDB por todas las citas de esa fecha
        result = table_appointments.scan(
            FilterExpression=Attr("date").eq(date_str)
        )

        appointments = result.get("Items", [])

        # Ordenar por hora
        appointments.sort(key=lambda x: x.get("hour", ""))

        # Agrupar resultados por estado (opcional)
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

def response(status, body):
    return {
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps(body)
    }
