output "api_gateway_url" {
  value = "${aws_api_gateway_stage.prod_stage.invoke_url}/"
}

output "api_gateway_arn" {
  value = aws_api_gateway_rest_api.lilbarberia_api.arn
}