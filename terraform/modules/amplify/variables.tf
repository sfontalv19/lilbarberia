# terraform/amplify/variables.tf

variable "project_name" {
  description = "Nombre del proyecto"
  type        = string
  default     = "lilbarberia"
}

variable "environment" {
  description = "Nombre del entorno"
  type        = string
  default     = "prod"
}

variable "github_repo_url" {
  description = "URL del repositorio GitHub del frontend"
  type        = string
  default     = "https://github.com/sfontalv19/lilbarberia_ui.git"
}

variable "github_token" {
  description = "Token personal de GitHub con permisos repo y admin:repo_hook"
  type        = string
  sensitive   = true

}

variable "api_gateway_url" {
  description = "URL del API Gateway del backend"
  type        = string
}



