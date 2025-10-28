# terraform/amplify/amplify_app.tf

resource "aws_amplify_app" "frontend" {
  name = "${var.project_name}-${var.environment}-frontend"

  # Repositorio GitHub (usa el tuyo real)
  repository  = var.github_repo_url
  oauth_token = var.github_token

  # Activar builds automáticos y ramas
  enable_auto_branch_creation = true
  enable_branch_auto_build    = true

  platform = "WEB"

  # Variables de entorno para el build de Next.js
  environment_variables = {
    NODE_ENV            = "production"
    NEXT_PUBLIC_API_URL = var.api_gateway_url
  }

  # Reglas para manejar rutas dinámicas en Next.js/React
  custom_rules = [
    {
      source = "/<*>"
      target = "/index.html"
      status = "200"
    }
  ]

  # Configuración del dominio por defecto (puedes agregar Route53 luego)
  auto_branch_creation_patterns = ["main", "prod"]
}
