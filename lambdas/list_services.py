import os
import boto3
import json

dynamodb = boto3.resource("dynamodb")
table_services = dynamodb.Table(os.environ.get("DYNAMODB_SERVICES_TABLE", "services"))

default_headers = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "OPTIONS,GET",
    "Access-Control-Allow-Headers": "Content-Type,Authorization"
}

### mostrar la lista de servicios que brinda la barberia


def handler(event, context):

    try:
        print ("DEBUG: event recibido", event)

        if event.get("httpMethod") == "OPTIONS":
            return {"statusCode": 200, "headers": default_headers, "body": json.dumps({"message": "CORS ok"})} 
        
        #scanear servicios

        response = table_services.scan()
        services = response.get("Items", [])

        return {
            "statusCode": 200,
            "headers": default_headers,
            "body": json.dumps({
                "count": len(services),
                "services": services
            })

    
        }
    
    except Exception as e:
        print("ERROR", str(e))
        return{
            "statusCode": 500,
            "headers": default_headers,
            "body": json.dumps({"error":f"error interno: {str(e)}"})
        }