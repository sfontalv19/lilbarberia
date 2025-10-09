## tabla usuarios

resource "aws_dynamodb_table" "users"{
    name = "${var.deploy_id}_${var.environment}_users"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "id_users"

    attribute {
        name = "id_users"
        type = "S"
    }

   global_secondary_index {
    name = "usersclient"
    hash_key = "id_users"
    projection_type = "ALL"
   } 
    
}