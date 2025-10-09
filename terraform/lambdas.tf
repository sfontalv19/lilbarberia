resource "aws_iam_role" "lambda_exec_barberia"{
    name = "${var.deploy_id}_${var.environment}_lambda_exec_role"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Principal = {Service = "lambda.amazonaws.com"}
                Action = "sts:AssumeRole"
            }
        ]
    })
}
#dynamodb
resource "aws_iam_policy" "lambda_combined_policy_barberia"{
    name = "${var.deploy_id}_${var.environment}_lambda_combined_policy"
    description = "consolidate policiy for all lambdas"

    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
           {  Effect = "Allow",
            Action= [
                "logs:CreateLogGroup",
                "logs:CreateLogsStream",
                "logs:PutLogEvents"
            ],
            Resource = "arn:aws:logs:${var.region_aws}:${var.aws_account_id}:log-group:/aws/lambda/*"
           },

           {Effect = "Allow",
           Action = [
            "dynamodb:PutItem",
            "dynamodb:GetItem",
            "dynamodb:UpdateItem",
            "dynamodb:DeleteItem",
            "dynamodb:Scan",
            "dynamodb:Query"
           ],
           Resource = "arn:aws:dynamodb:${var.region_aws}:${var.aws_account_id}:table/${var.deploy_id}_${var.environment}_*"

           },

           {Effect = "Allow",
            Action = [
                "cognito-idp:SignUp",
                "cognito-idp:ConfirmSignUp",
                "cognito-idp:ConfirmForgotPassword",
                "cognito-idp:InitiateAuth",
                "cognito-idp:AdminCreateUser",
                "cognito-idp:ConfirmSignUp",
                "cognito-idp:AdminGetUser",
                "cognito-idp:AdminSetUserPassword",
                "cognito-idp:AdminSetUserPassword",
                "cognito-idp:ListUsers"
            ]
            Resource = "*"
           },

           #apigateway


           #secret manager

         
        ]
    })
}

resource "aws_iam_role_policy_attachment" "lambda_combined_attachment_barberia"{
    role = aws_iam_role.lambda_exec_barberia.name
    policy_arn = aws_iam_policy.lambda_combined_policy_barberia.arn
}

resource "aws_cloudwatch_log_group" "lambda_logs_barberia" {
    for_each  =toset(local.lambdas)
    name = "/aws/lambda/${var.deploy_id}_${var.environment}_${replace(each.value, "/", "_")}"
    retention_in_days = 30

    tags = {
        Environment = var.environment
        Service = "lambdaLogs"
    }

   
}


locals{
    lambdas = [
        "signup",
        "signin",
        "confirmSignup"
    ]
}

##lambda package


resource "null_resource" "ensure_build_dir" {
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/build"
  }
}

data "archive_file" "lambda_package"{
    for_each = toset(local.lambdas)
    type = "zip"
    source {
        content = file("${path.root}/../lambdas/${each.value}.py")
        filename = "${each.value}.py"
    }

    depends_on = [null_resource.ensure_build_dir]
    output_path = "${path.module}/build/${each.value}.zip"

}





resource "aws_lambda_function" "lambdas"{
    for_each = toset(local.lambdas)
    function_name = "${var.deploy_id}_${var.environment}_${replace(each.value, "/", "_")}"
    role = aws_iam_role.lambda_exec_barberia.arn
    handler = "${each.value}.handler"
    runtime = "python3.9"
    filename = data.archive_file.lambda_package[each.value].output_path
    source_code_hash = data.archive_file.lambda_package[each.value].output_base64sha256
    timeout = 600
    memory_size = 512

    depends_on = [aws_cloudwatch_log_group.lambda_logs_barberia]


    environment{
        variables = {
            DYNAMODB_TABLE = "${var.deploy_id}_${var.environment}_${lookup(var.dynamodb_tables, split("/", each.value)[0], "NO_DYNAMODB_TABLE")}"
            COGNITO_CLIENT_ID = module.cognito.app_client_id
            COGNITO_USER_POOL_ID = module.cognito.user_pool_id
            ENVIROMENT = var.environment
            
        }
    }

}

resource "aws_lambda_function_url" "lambdas_urls"{
    for_each = toset(local.lambdas)
    function_name = aws_lambda_function.lambdas[each.value].arn
    authorization_type = "NONE"
}

output "lambdas_urls" {
    value = {for k, v in aws_lambda_function_url.lambdas_urls : k => v.function_url }
}