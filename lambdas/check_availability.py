import json
import boto3
import os 
from datetime import datetime, time, timedelta
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource("dynamodb")
table_appointments = dynamodb.Table(os.environ.get("DYNAMODB_APPOINTMENTS_TABLE", "appointments"))

default_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "OPTIONS,GET",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
}


def handler (event, context):
    try:
        print ("DEBUG: Event recibido", event)

        if event.get("HttpMethod") == "OPTIONS":
            return{"statusCode": 200, "headers": default_headers, "body": json.dumps({"message": "CORS ok"})}
        
        #si viene desde apigateway

        params = event.get("queryStringParameters", {}) or {}
        date_str = params.get("date")
        service_id  = params.get("service_id")

        if not date_str or not service_id:
            return response(400, {"error": "faltan parametros:date y service_id son requeridos"})
        
        # validar formato de fecha

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d"). date()
        except ValueError:
            return response (400, {"error": "formato de fecha invalido"})
        
        weekday = date_obj.weekday()
        if weekday == 6: #domingo
            start, end = time (9,0), time (16,0)
        else:
            start, end = time(9,0), time (19,0)

        avalible_hours = []
        current = datetime.combine(date_obj, start)
        while  current.time () <= end:
            avalible_hours.append(current.strftime("%H:%M"))
            current += timedelta(minutes=60)

        result = table_appointments.scan(
            FilterExpression = Attr("date").eq(date_str) & Attr("status").eq("scheduled")
        )

        taken_hours = [item["hour"] for item in result.get("Items", [])]
        print("DEBUG: horas ya tomada", taken_hours)


        #filtrar horas ocupadas
        free_hours = [h for h in avalible_hours if h not in taken_hours]

        return response (200,{
            "date": date_str,
            "service_id": service_id,
            "available_hours": free_hours
        })
    
    except Exception as e:
        print("ERROR:", str(e))
        return response (500, {"error": f"error interno:{str(e)}"})

def response(status,body):
    return{
        "statusCode": status,
        "headers": default_headers,
        "body": json.dumps(body)
    }    
            

