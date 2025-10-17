variable region {
  type        = string
  default     = "us-east-1"
  description = "description"
}

variable environment {
    type = string
    default = "dev"
}

variable deploy_id {
    type = string
    default = "barberia"
}

variable "cognito_user_pool_name" {
    type = string
    description = "cognito_user_pool_name"
}


variable "callback_urls" {
    type = list(string)
    default = ["https://tudominio.com/callback"]
}

variable "logout_urls" {
    type = list(string)
    default = ["https://tudominio.com/logout"]
}

