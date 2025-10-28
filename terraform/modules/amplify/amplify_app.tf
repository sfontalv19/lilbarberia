resource "aws_amplify_app" "frontend" {
  provider = aws

  name        = "${var.project_name}-${var.environment}-frontend"
  repository  = var.github_repo_url
  oauth_token = var.github_token
  platform    = "WEB"

  enable_auto_branch_creation = true
  enable_branch_auto_build    = true

  environment_variables = {
    NODE_ENV            = "production"
    NEXT_PUBLIC_API_URL = var.api_gateway_url
  }

  custom_rule {
    source = "/<*>"
    target = "/index.html"
    status = "200"
  }

  #  Este va a nivel raíz, no dentro del bloque
  auto_branch_creation_patterns = ["main", "prod"]

  #  Este bloque es solo para configuración adicional de ramas
  auto_branch_creation_config {
    environment_variables = {
      NEXT_PUBLIC_API_URL = var.api_gateway_url
    }

    enable_auto_build = true
  }
}
