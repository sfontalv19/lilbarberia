## RESOURCE FOR SNS 

resource "aws_sns_topic" "lilbarberia"{
    name = var.topic_name
    display_name = var.display_name
}


# resourse for sms del barbero

resource "aws_sns_topic_subscription" "barbero_sms"{
    topic_arn = aws_sns_topic.lilbarberia.arn
    protocol = "sms"
    endpoint = var.barber_phone_number
}

###############################################
#  Política para permitir publicar en SNS
###############################################
resource "aws_iam_policy" "publish_policy" {
  name        = "${var.topic_name}-publish-policy"
  description = "Permite a las Lambdas publicar mensajes en el Topic SNS"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "sns:Publish"
        ],
        Resource = aws_sns_topic.lilbarberia.arn
      }
    ]
  })
}