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

#tabla de servicio

resource "aws_dynamodb_table" "services"{
    name = "${var.deploy_id}_${var.environment}_services"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "service_id"

    attribute {
        name = "service_id"
        type = "S"
    }

    tags = {
        Name = "services-table"
        Environment = var.environment
    }
}


# tabla cita

resource "aws_dynamodb_table" "appointments"{
    name = "${var.deploy_id}_${var.environment}_appointments"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "appointment_id"

    attribute{
        name = "appointment_id"
        type = "S"
    }
}