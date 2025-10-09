output "user_pool_id"{
    value = aws_cognito_user_pool.barberia.id
}

output "user_pool_arn"{
    value = aws_cognito_user_pool.barberia.arn
}

output "user_pool_client_id_attr" {
  value = aws_cognito_user_pool_client.barberia_client.id
}



output "identity_pool_id" {
  value = aws_cognito_identity_pool.barberia_identity_pool.id
}

output "identity_pool_arn" {
  value = aws_cognito_identity_pool.barberia_identity_pool.arn
}

output "app_client_id" {
  value = aws_cognito_user_pool_client.barberia_client.id
}