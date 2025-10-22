resource "aws_api_gateway_rest_api" "lilbarberia_api" {
  name        = "${var.deploy_id}_${var.environment}_api"
  description = "api for barberia project ${var.environment}"

}


resource "aws_api_gateway_authorizer" "lilbarberia_apigateway_authorizer" {
  name          = "${var.deploy_id}_${var.environment}_apigateway_authorizer"
  rest_api_id   = aws_api_gateway_rest_api.lilbarberia_api.id
  type          = "COGNITO_USER_POOLS"
  provider_arns = [var.cognito_user_pool_arn]
}



##signup

#create resource "signup"
resource "aws_api_gateway_resource" "signup_resource" {
  rest_api_id = aws_api_gateway_rest_api.lilbarberia_api.id
  parent_id   = aws_api_gateway_rest_api.lilbarberia_api.root_resource_id
  path_part   = "signup"
}
# create method post for signup

resource "aws_api_gateway_method" "signup_post" {
  rest_api_id   = aws_api_gateway_rest_api.lilbarberia_api.id
  resource_id   = aws_api_gateway_resource.signup_resource.id
  http_method   = "POST"
  authorization = "NONE"

}

##integration wuth the signup lambda

resource "aws_api_gateway_integration" "signup_integration" {

  rest_api_id             = aws_api_gateway_rest_api.lilbarberia_api.id
  resource_id             = aws_api_gateway_resource.signup_resource.id
  http_method             = aws_api_gateway_method.signup_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.signup_arn

}

resource "aws_lambda_permission" "apigateway_signup_lambdda" {
  statement_id  = "AllowAPIGatewayInvokeSignUp"
  action        = "lambda:InvokeFunction"
  function_name = var.signup_name
  principal     = "apigateway.amazonaws.com"


  source_arn = "${aws_api_gateway_rest_api.lilbarberia_api.execution_arn}/*/POST/signup"
}

##confirmSignup

resource "aws_api_gateway_resource" "confirmSignup_resource" {
  rest_api_id = aws_api_gateway_rest_api.lilbarberia_api.id
  parent_id   = aws_api_gateway_rest_api.lilbarberia_api.root_resource_id
  path_part   = "confirmSignup"
}
# create method post for confirmSignup

resource "aws_api_gateway_method" "confirmSignup_post" {
  rest_api_id   = aws_api_gateway_rest_api.lilbarberia_api.id
  resource_id   = aws_api_gateway_resource.confirmSignup_resource.id
  http_method   = "POST"
  authorization = "NONE"

}

##integration wuth the confirmSignup lambda

resource "aws_api_gateway_integration" "confirmSignup_integration" {

  rest_api_id             = aws_api_gateway_rest_api.lilbarberia_api.id
  resource_id             = aws_api_gateway_resource.signup_resource.id
  http_method             = aws_api_gateway_method.confirmSignup_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = var.confirmSignup_arn

}

resource "aws_lambda_permission" "apigateway_confirmSignup_lambdda" {
  statement_id  = "AllowAPIGatewayInvokeSignUp"
  action        = "lambda:InvokeFunction"
  function_name = var.confirmSignup_name
  principal     = "apigateway.amazonaws.com"


  source_arn = "${aws_api_gateway_rest_api.lilbarberia_api.execution_arn}/*/POST/confirSignup"
}






resource "aws_api_gateway_deployment" "lilbarberia_deployment" {
  rest_api_id = aws_api_gateway_rest_api.lilbarberia_api.id
  stage_name  = var.environment

  depends_on = [
    aws_api_gateway_integration.signup_integration
  ]
}


resource "aws_api_gateway_stage" "prod_stage" {
  deployment_id = aws_api_gateway_deployment.lilbarberia_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.lilbarberia_api.id
  stage_name    = "prod"
}

