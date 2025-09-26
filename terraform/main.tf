terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws     = { source = "hashicorp/aws", version = ">= 5.0" }
    archive = { source = "hashicorp/archive", version = ">= 2.4" }
  }
    backend "s3"{
        bucket = "lilbarberia-terraform-state"
        key    = "global/s3/terraform.tfstate"
        region = "us-east-1"
    }
}

provider "aws" {
  region = var.region
}

data "aws_caller_identity" "current" {}

# ===== DynamoDB =====
locals {
  customers_table = "${var.project}_${var.stage_name}_customers"
}

resource "aws_dynamodb_table" "customers" {
  name         = local.customers_table
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id_customer"

  attribute { 
   name = "id_customer"
   type = "S" 
   
   }
}



# ===== Definición de lambdas =====
variable "lambdas" {
  description = "Configuración de lambdas"
  type = map(object({
    file    = string
    handler = string
    memory  = number
    timeout = number
    route   = string
  }))
  default = {
    signup = {
      file    = "../lambdas/signup.py"
      handler = "signup.handler"
      memory  = 256
      timeout = 15
      route   = "POST /signup"
    }
    booking = {
      file    = "../lambdas/booking.py"
      handler = "booking.handler"
      memory  = 256
      timeout = 15
      route   = "POST /booking"
    }
  }
}

# ===== IAM para todas las lambdas =====
resource "aws_iam_role" "lambda_role" {
  name = "${var.project}-${var.stage_name}-lambda-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = { Service = "lambda.amazonaws.com" },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "lambda_custom" {
  name = "${var.project}-${var.stage_name}-lambda-policy"
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = ["dynamodb:PutItem"],
        Resource = aws_dynamodb_table.customers.arn
      },
      {
        Effect = "Allow",
        Action = [
          "cognito-idp:SignUp",
          "cognito-idp:AdminGetUser",
          "cognito-idp:AdminConfirmSignUp"
        ],
        Resource = "arn:aws:cognito-idp:${var.region}:${data.aws_caller_identity.current.account_id}:userpool/${var.cognito_user_pool_id}"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_custom" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.lambda_custom.arn
}

# ===== Empaquetado dinámico =====
data "archive_file" "zips" {
  for_each    = var.lambdas
  type        = "zip"
  source_file = each.value.file
  output_path = "${path.module}/../${each.key}.zip"
}

# ===== Lambdas dinámicas =====
resource "aws_lambda_function" "lambda" {
  for_each = var.lambdas

  function_name = "${var.project}-${var.stage_name}-${each.key}"
  role          = aws_iam_role.lambda_role.arn
  runtime       = "python3.11"
  handler       = each.value.handler
  filename      = data.archive_file.zips[each.key].output_path
  memory_size   = each.value.memory
  timeout       = each.value.timeout

  environment {
    variables = {
      AWS_REGION           = var.region
      COGNITO_USER_POOL_ID = var.cognito_user_pool_id
      COGNITO_CLIENT_ID    = var.cognito_client_id
      CUSTOMERS_TABLE_NAME = aws_dynamodb_table.customers.name
    }
  }
}

# ===== API Gateway HTTP API único =====
resource "aws_apigatewayv2_api" "http" {
  name          = "${var.project}-${var.stage_name}-http-api"
  protocol_type = "HTTP"
  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["OPTIONS", "POST"]
    allow_headers = ["Content-Type", "Authorization"]
  }
}

# Integraciones por lambda
resource "aws_apigatewayv2_integration" "lambda" {
  for_each              = aws_lambda_function.lambda
  api_id                = aws_apigatewayv2_api.http.id
  integration_type      = "AWS_PROXY"
  integration_uri       = each.value.arn
  payload_format_version = "2.0"
}

# Rutas dinámicas
resource "aws_apigatewayv2_route" "routes" {
  for_each   = var.lambdas
  api_id     = aws_apigatewayv2_api.http.id
  route_key  = each.value.route
  target     = "integrations/${aws_apigatewayv2_integration.lambda[each.key].id}"
}

resource "aws_apigatewayv2_stage" "stage" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = var.stage_name
  auto_deploy = true
}

# Permisos de invocación
resource "aws_lambda_permission" "apigw" {
  for_each      = aws_lambda_function.lambda
  statement_id  = "AllowAPIGatewayInvoke-${each.key}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}
