output "topic_arn" {
  description = "arn del topic sns"
  value = aws_sns_topic.lilbarberia.arn
}


output "publish_policy_arn" {
  value = aws_iam_policy.publish_policy.arn
}
