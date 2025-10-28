variable "region_aws" {
  type    = string
  default = "us-east-1"
}
variable "aws_profile" {
  type    = string
  default = "lilbarberia"
}


variable "project" {
  description = "Nombre del proyecto"
  type        = string
  default     = "lilbarberia"
}

variable "stage_name" {
  description = "Nombre del entorno"
  type        = string
  default     = "prod"
}

## cognito 

variable "deploy_id" {
  description = "Deploy_id"
  type        = string
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "prod"

}

variable "cognito_user_pool_arn" {
  description = "cognito_user_pool_arn"
  type        = string
  default     = "arn:aws:cognito-idp:us-east-1:000000000000:userpool/dummy"

}

variable "cognito_user_pool_name" {
  description = "cognito_user_pool_name"
  type        = string
  default     = "lilbarberia"
}

variable "aws_account_id" {
  description = "AWS account for id for resource arns"
  type        = string
  default     = "307946681447"

}

variable "dynamodb_tables" {
  type        = map(string)
  description = "map nomber logic lambda"
  default = {
    users = "users"
    auth  = "auth"
  }
}

##amplify

variable "github_token" {
  description = "Token personal de GitHub para conectar Amplify"
  type        = string
  sensitive   = true
}
