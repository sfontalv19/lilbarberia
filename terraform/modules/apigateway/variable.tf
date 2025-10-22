variable "deploy_id" {
  description = "deploy id"
  type        = string
}

variable "environment" {
  description = "enviroment "
  type        = string
}

variable "cognito_user_pool_arn" {
  description = "cognito arn"
  type        = string
}

variable "cognito_user_pool_name" {
  description = "cognito name"
  type        = string
}

variable "signup_arn" {
  description = "ARN de la lambda signup"
  type        = string
}
variable "signup_name" {
  description = "nombre de la lambda signup"
  type        = string
}


variable "confirmSignup_arn" { 
  description = "ARN de la lambda confirmSignup"
  type = string
}

variable "confirmSignup_name" {
  description =  "nombre lambda confirmSignup"
  type = string
}
