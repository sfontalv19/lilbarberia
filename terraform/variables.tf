variable "region" {
  type    = string
  default = "us-east-1"
}
variable "aws_profile" {
    type = string 
    default= "lilbarberia"
}


variable "project" {
    description = "Nombre del proyecto"
    type        = string
    default     = "lilbarberia"
}

variable "stage_name" {
    description = "Nombre del entorno"
    type        = string
    default     = "dev"
}

variable "cognito_user_pool_id" {
  description = "ID del User Pool de Cognito"
  type        = string
  
}

variable "cognito_client_id"{
    description = "ID del App Client de Cognito"
    type        = string
}