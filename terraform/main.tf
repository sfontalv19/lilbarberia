terraform {
  required_version = ">= 1.4.2"

  backend "s3" {
    bucket  = "silviobarberia-app"
    key     = "terraform.tfstate"
    region  = "us-east-1"
    encrypt = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    awscc = {
      source  = "hashicorp/awscc"
      version = "0.53.0"
    }
  }
}

provider "aws" {
  region = var.region_aws

  default_tags {
    tags = {
      Project = var.project
      Owner   = "sergio"
    }
  }
}


# Cuenta AWS actual (para obtener account_id)
data "aws_caller_identity" "current" {}

# (opcional, más portable si usas GovCloud/China)
data "aws_partition" "current" {}


data "aws_iam_policy_document" "lambda_combined_barberia" {
  # Permisos de logs (para que Lambda cree/uses sus log groups/streams)
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      "arn:aws:logs:${var.region_aws}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/*"
    ]
  }

  # Ejemplo: permisos mínimos para tu tabla DynamoDB de users
  statement {
    effect = "Allow"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:GetItem",
      "dynamodb:UpdateItem",
      "dynamodb:Query",
      "dynamodb:Scan"
    ]
    resources = [
      module.dynamodb.users_table_arn # ajusta al output real de tu módulo
    ]
  }

  # (Opcional) Cognito, si tus Lambdas llaman a Cognito
  # statement {
  #   effect  = "Allow"
  #   actions = [
  #     "cognito-idp:AdminInitiateAuth",
  #     "cognito-idp:AdminCreateUser",
  #     "cognito-idp:AdminGetUser"
  #   ]
  #   resources = [ module.cognito.user_pool_arn ]
  # }
}



resource "aws_iam_role_policy_attachment" "lambda_combined_attach_barberia" {
  role       = aws_iam_role.lambda_exec_barberia.name
  policy_arn = aws_iam_policy.lambda_combined_policy_barberia.arn
}


#cognito

module "cognito" {
  source                 = "./modules/cognito"
  environment            = var.environment
  deploy_id              = var.deploy_id
  cognito_user_pool_name = var.cognito_user_pool_name
  cognito_user_pool_arn  = module.cognito.user_pool_arn
  region                 = var.region_aws
}


# dynamodb

module "dynamodb" {
  source                 = "./modules/dynamodb"
  environment            = var.environment
  deploy_id              = var.deploy_id
  cognito_user_pool_arn  = module.cognito.user_pool_arn
  cognito_user_pool_name = var.cognito_user_pool_name

}



## apigateway

module "apigateway" {
  source                 = "./modules/apigateway"
  environment            = var.environment
  deploy_id              = var.deploy_id
  cognito_user_pool_arn  = module.cognito.user_pool_arn
  cognito_user_pool_name = var.cognito_user_pool_name


  signup_arn  = aws_lambda_function.lambdas["signup"].invoke_arn
  signup_name = aws_lambda_function.lambdas["signup"].function_name
  confirmSignup_arn = aws_lambda_function.lambdas["confirmSignup"].invoke_arn
  confirmSignup_name = aws_lambda_function.lambdas["confirmSignup"].function_name
  signin_arn = aws_lambda_function.lambdas["signin"].invoke_arn
  signin_name = aws_lambda_function.lambdas["signin"].function_name



}