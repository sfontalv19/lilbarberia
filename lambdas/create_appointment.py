import json
import boto3
import os
import uuid
from datetime import datetime, time, timedelta
from boto3.dynamodb.conditions import Attr

sns = boto3.client("sns")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")

dynamodb = boto3.resource("dynamodb")
table_appointments = dynamodb.Table(os.environ.get("DYNAMODB_APPOINTMENTS_TABLE", "appointments"))
table_services = dynamodb.Table(os.environ.get("DYNAMODB_SERVICES_TABLE", "services"))

default_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "OPTIONS,POST",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
}


def handler(event, context):
    try:
        print("DEBUG: Event recibido", json.dumps(event))
        print(f"DEBUG: SNS_TOPIC_ARN configurado: {SNS_TOPIC_ARN}")

        if event.get("httpMethod") == "OPTIONS":
            return {"statusCode": 200, "headers": default_headers, "body": json.dumps({"message": "CORS ok"})}
        
        if "body" not in event or not event["body"]:
            return response(400, {"error": "body requerido"})
        
        body = json.loads(event["body"])
        user_id = None

        claims = event.get("requestContext", {}).get("authorizer", {}).get("claims", {})
        if claims:
            user_id = claims.get("sub")

        if not user_id:
            user_id = body.get("user_id")

        if not user_id:
            return response(401, {"error": "No se encontró usuario autenticado"})

        service_id = body.get("service_id")
        date_str = body.get("date")
        hour_str = body.get("hour")

        if not all([user_id, service_id, date_str, hour_str]):
            return response(400, {"error": "Faltan datos requeridos"})
        
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            hour_obj = datetime.strptime(hour_str, "%H:%M").time()
        except ValueError:
            return response(400, {"error": "Formato de fecha u hora inválido"})
        
        now = datetime.utcnow() - timedelta(hours=5)
        appointment_datetime = datetime.combine(date_obj, hour_obj)

        if appointment_datetime <= now:
            return response (400, {
                "error": "la cita debe programarse en una fecha y hora futura"
                         "no se permiten citas para horas ya pasada"
            })

        # Obtener servicio
        service = table_services.get_item(Key={"service_id": service_id}).get("Item")
        if not service:
            return response(404, {"error": "El servicio no existe"})

        # Validar horario disponible
        if not is_valid_time(date_obj, hour_obj):
            return response(400, {"error": "La hora seleccionada está fuera del horario"})

        conflict = table_appointments.scan(
            FilterExpression=Attr("date").eq(date_str) & Attr("hour").eq(hour_str) & Attr("status").eq("scheduled")
        )

        if conflict.get("Count", 0) > 0:
            return response(409, {"error": "Horario no disponible"})
        
        # Crear cita
        appointment_id = f"APT#{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S-05:00")

        item = {
            "appointment_id": appointment_id,
            "user_id": user_id,
            "service_id": service_id,
            "date": date_str,
            "hour": hour_str,
            "status": "scheduled",
            "created_at": created_at
        }

        table_appointments.put_item(Item=item)

        # ✅ Enviar notificación SNS con validación
        try:
            if not SNS_TOPIC_ARN:
                print("WARNING: SNS_TOPIC_ARN no está configurado. No se enviará notificación.")
            else:
                message = (
                    
                    f"🔔 Nueva cita agendada\n\n"
                    f"📅 Fecha: {date_str}\n"
                    f"🕐 Hora: {hour_str}\n"
                    f"👤 Cliente: {user_id}\n"
                    f"✂️ Servicio: {service.get('name', 'Desconocido')}\n"
                    f"🆔 ID: {appointment_id}"
                )
                
                sns_response = sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Message=message,
                    Subject="Nueva Cita - Barbería"
                )
                
                print(f"DEBUG: Mensaje SNS enviado correctamente. MessageId: {sns_response.get('MessageId')}")
        
        except Exception as e:
            print(f"ERROR SNS: {str(e)}")
            # La cita se creó pero no se pudo enviar la notificación
            # No fallamos la operación por esto

        return response(201, {
            "message": "Cita agendada con éxito",
            "appointment_id": appointment_id,
            "service_id": service_id,
            "date": date_str,
            "hour": hour_str,
            
        })
    except Exception as e:
        print("ERROR:", str(e))
        import traceback
        print("TRACEBACK:", traceback.format_exc())
        return response(500, {"error": f"Error interno: {str(e)}"})


def response(status, body):
    return {
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps(body)
    }


def is_valid_time(date_obj, hour_obj):
    weekday = date_obj.weekday()
    if weekday == 6:
        start, end = time(9, 0), time(16, 0)
    else: 
        start, end = time(9, 0), time(19, 0)
    return start <= hour_obj <= end