import json
import boto3
import os
import uuid
from datetime import datetime, time
from boto3.dynamodb.conditions import Attr

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
        print ("DEBUG: Event recibido", event)

        if event.get ("httpMethod") == "OPTIONS":
            return {"statusCode": 200, "headers": default_headers, "body": json.dumps({"message": "CORS ok"})}
        

        if "body" not in event or not event ["body"]:
            return response (400, {"error": "body requerido"})
        

        body = json.loads (event ["body"])
        user_id = body.get("user_id")
        service_id = body.get("service_id")
        date_str = body.get("date")
        hour_str = body.get ("hour")


        if not all ([user_id, service_id, date_str, hour_str]):
            return response(400,{"error": "faltan datos requieridos"})
        
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            hour_obj = datetime.strptime(hour_str, "%H:%M").time()

        except ValueError:
            return response (400, {"error": "formato de fecha u hora invalido"})



        #obtener servicio
        service = table_services.get_item(Key={ "service_id": service_id}).get("Item")
        if not service:
            return response(404, {"error": "el servicio no existe"})


        #validar horario disponible
        if not is_valid_time(date_obj, hour_obj):
            return response (400, {"error": "la hora selecionada esta fuera del horario"})



        conflict = table_appointments.scan(
            FilterExpression = Attr("date").eq(date_str) & Attr("hour").eq(hour_str) & Attr("status").eq("scheduled")
        )

        if conflict.get("Count", 0) > 0:
            return response(409,{"error": "horario no disponible"})
        

        # crear cita


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

        table_appointments.put_item(Item = item)


        return response (201, {
            "message": "cita agendada con exito",
            "appointment_id": appointment_id,
            "service_id": service_id,
            "date": date_str,
            "hour": hour_str
        })

    except Exception as e:
        print ("ERROR", str(e))
        return response (500, {"error" : f"Error interno: {str(e)}"})
    

def response (status, body):
        return {
            "statusCode": status,
            "headers": default_headers,
            "body": json.dumps(body)
        }
    
def is_valid_time(date_obj, hour_obj):
        weekday = date_obj.weekday()
        if weekday == 6:
            start, end = time (9, 0), time (16, 0)

        else: 
            start, end = time (9,0), time (19, 0)

        return start <= hour_obj <= end     