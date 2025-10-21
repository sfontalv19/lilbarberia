import json
import boto3
import os

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

        # Manejar CORS
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
        new_status = body.get("status")

        if not appointment_id or not new_status:
            return response(400, {"error": "appointment_id y status son requeridos"})

        # Verificar si la cita existe
        result = table_appointments.get_item(Key={"appointment_id": appointment_id})
        appointment = result.get("Item")

        if not appointment:
            return response(404, {"error": "la cita no existe"})

        # Validar estado permitido
        allowed_status = ["scheduled", "completed", "cancelled"]
        if new_status not in allowed_status:
            return response(400, {"error": f"status inválido. Use uno de: {allowed_status}"})

        # Actualizar estado
        table_appointments.update_item(
            Key={"appointment_id": appointment_id},
            UpdateExpression="SET #st = :s",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={":s": new_status}
        )

        return response(200, {
            "message": f"Estado de cita actualizado a '{new_status}'",
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
