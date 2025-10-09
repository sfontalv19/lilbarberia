variable "deploy_id" {
    description = "Deploy_id"
    type = string
}

variable "environment" {
    description = "Environment"
    type = string

}

variable "cognito_user_pool_arn"{
    description = "cognito_user_pool_arn"
    type = string
}

variable "cognito_user_pool_name" {
    description = "cognito_user_pool_name"
    type = string
}