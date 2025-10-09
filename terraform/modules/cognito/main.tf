resource "aws_cognito_user_pool" "barberia"{
    name = "${var.cognito_user_pool_name}_${var.environment}"

    

// email
auto_verified_attributes = ["email"]
username_attributes = ["email"]

// password

password_policy{
    minimum_length = 8
    require_lowercase = true
    require_numbers = true
    require_symbols = false
    require_uppercase = true

}

verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject = "verifica tu cuenta - lilbarberia"
    email_message = "hola, tu codigo de verificacion es {####}"
    
}

admin_create_user_config {
    allow_admin_create_user_only = false
}

// configuracion de atributos personalizados
schema {
    name = "fullname"
    attribute_data_type = "String"
    required = false
    mutable = true
}

schema {
    name = "phone"
    attribute_data_type = "String"
    required = false
    mutable = true
    
}

schema {
    name = "client"
    attribute_data_type = "String"
    required = false
    mutable = true
}
  lifecycle{
    ignore_changes = [schema]
  }
}
############################################
# USER POOL CLIENT
############################################
resource "aws_cognito_user_pool_client" "barberia_client" {
  name         = "${var.cognito_user_pool_name}-${var.environment}-client"
  user_pool_id = aws_cognito_user_pool.barberia.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_ADMIN_USER_PASSWORD_AUTH",
  ]

  refresh_token_validity = 3650 # días
  access_token_validity  = 1440 # minutos
  id_token_validity      = 1440 # minutos

  token_validity_units {
    access_token  = "minutes"
    id_token      = "minutes"
    refresh_token = "days"
  }

  # Hosted UI / OAuth (opcional)
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_scopes                 = ["openid", "email", "profile"]
  supported_identity_providers         = ["COGNITO"]
  callback_urls                        = var.callback_urls
  logout_urls                          = var.logout_urls
}

############################################
# (OPCIONAL) IDENTITY POOL
############################################
resource "aws_cognito_identity_pool" "barberia_identity_pool" {
  identity_pool_name               = "${var.cognito_user_pool_name}-${var.environment}-identity"
  allow_unauthenticated_identities = false

  cognito_identity_providers {
    provider_name = "cognito-idp.${var.region}.amazonaws.com/${aws_cognito_user_pool.barberia.id}"
    client_id     = aws_cognito_user_pool_client.barberia_client.id
  }
}