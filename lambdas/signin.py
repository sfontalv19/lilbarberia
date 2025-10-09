import json
import boto3
from botocore.exceptions import ClientError
import os

default_header = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Header": "*"
}

def handler(event, context):
    print("DEBUG: Event ->", json.dumps(event))

    if event.get("httpMethod") == "OPTIONS":
        return response (200, {"message": "CORS preflight OK"})
    
    try:
        body = json.loads(event.get("body", "{}"))
        email = body.get ("email")
        password = body.get ("password")

        if not email or not password:
            return response(400,{"error": "faltan parametros: email or password"})
        
        client = boto3.client("cognito-idp")
        client_id = os.environ["COGNITO_CLIENT_ID"]

        resp = client.initiate_auth(
            AuthFlow = "USER_PASSWORD_AUTH",
            AuthParameters = {
                "USERNAME": email,
                "PASSWORD": password
            },
            ClientId = client_id
        )

        tokens = resp [ "AuthenticationResult"]

        user_info = client.get_user(AccessToken = tokens ["AccessToken"])
        attributes = {attr ["Name"]: attr["Value"] for attr in user_info["UserAttributes"]}

        return response (200,{
            "message": "inicio de sesion correcto",
            "tokens" : {
                "access_token": tokens["AccessToken"],
                "id_token": tokens [ "IdToken"],
                "refresh_token": tokens.get("RefreshToken", "")
            },

            "user": {
                "email": attributes.get("email"),
                "status": user_info.get("UserStatus", "CONFIRMED")
            }
        })
    
    except ClientError as e:
        print ("ERROR", e)
        code = e.response ["Error"] ["Code"]

        if code == "NotAuthorizedException":
            return response(401, {"error": "Credenciales incorrectas"})
        elif code == "UserNotFoundException":
            return response(404, {"error": "Usuario no encontrado"})
        elif code == "UserNotConfirmedException":
            return response(403, {"error": "Cuenta no confirmada"})
        elif code == "PasswordResetRequiredException":
            return response(403, {"error": "Debes restablecer la contraseña"})
        else:
            return response(500, {"error": f"Error inesperado: {str(e)}"})

def response(status, body):
    return {
        "statusCode": status,
        "headers": default_header,
        "body": json.dumps(body)
    }