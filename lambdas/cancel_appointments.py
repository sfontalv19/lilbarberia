import json
import boto3
import os
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")
table_appointments = dynamodb.Table(os.environ.get("DYNAMODB_APPOINTMENTS_TABLE", "appointments"))

default_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "OPTIONS,PUT",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
}

def handler(event, context):
    try:
        print("DEBUG: Event recibido:", event)

        # Manejo CORS
        if event.get("httpMethod") == "OPTIONS":
            return {
                "statusCode": 200,
                "headers": default_headers,
                "body": json.dumps({"message": "CORS ok"})
            }

        # Validar body
        if "body" not in event or not event["body"]:
            return response(400, {"error": "body requerido"})

        body = json.loads(event["body"])
        appointment_id = body.get("appointment_id")
        user_id = body.get("user_id")  # opcional, útil para validar

        if not appointment_id:
            return response(400, {"error": "appointment_id requerido"})

        # Buscar la cita
        result = table_appointments.get_item(Key={"appointment_id": appointment_id})
        appointment = result.get("Item")

        if not appointment:
            return response(404, {"error": "la cita no existe"})

        # Validar que el usuario sea dueño de la cita (si se pasa user_id)
        if user_id and appointment.get("user_id") != user_id:
            return response(403, {"error": "no tienes permiso para cancelar esta cita"})

        # Verificar estado
        if appointment.get("status") == "cancelled":
            return response(400, {"error": "la cita ya fue cancelada"})

        # Actualizar estado
        table_appointments.update_item(
            Key={"appointment_id": appointment_id},
            UpdateExpression="SET #st = :s",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={":s": "cancelled"}
        )

        return response(200, {
            "message": "cita cancelada exitosamente",
            "appointment_id": appointment_id
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
