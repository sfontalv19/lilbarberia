# modules/dynamodb/outputs.tf
output "users_table_name" {
  value = aws_dynamodb_table.users.name
}

output "users_table_arn" {
  value = aws_dynamodb_table.users.arn
}


output "appointments_table_name" {
  value = aws_dynamodb_table.appointments.name
}

output "services_table_name" {
  value = aws_dynamodb_table.services.name
}