terraform {
    required_version = ">= 0.12"
    required_providers {
      aws = {source = "hashicorp/aws", version=">=5.0"}
    }
    
}

provider aws{
    region = var.region
    profile = var.aws_profile
}

data "aws_caller_identity" "me"{}
data "aws_region" "current"{}

output "account_id"{value = data.aws_caller_identity.me.account_id}
output "caller_arn" {value= data.aws_caller_identity.me.arn}
output "region" {value= data.aws_region.current.name}
