# terraform/amplify/amplify_branch.tf

resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.frontend.id
  branch_name = "main"

  stage     = "PRODUCTION"
  framework = "Next.js"

  environment_variables = {
    NEXT_PUBLIC_API_URL = var.api_gateway_url
  }

  enable_auto_build = true
  display_name      = "main"

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

