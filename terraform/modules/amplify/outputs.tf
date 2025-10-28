# terraform/amplify/outputs.tf

output "amplify_app_id" {
  description = "ID de la aplicación Amplify"
  value       = aws_amplify_app.frontend.id
}

output "amplify_default_domain" {
  description = "Dominio generado automáticamente por Amplify"
  value       = aws_amplify_app.frontend.default_domain
}

output "amplify_main_branch_url" {
  description = "URL de despliegue de la rama main"
  value       = aws_amplify_branch.main.web_url
}


