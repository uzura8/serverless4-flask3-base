output "vpc_id" {
  value = aws_vpc.this.id
}

output "subnet_public_web_ids" {
  value = [aws_subnet.public_web1.id, aws_subnet.public_web2.id]
}

output "subnet_group_db_name" {
  value = aws_db_subnet_group.main.name
}

output "subnet_private_db_ids" {
  value = [aws_subnet.private_db1.id, aws_subnet.private_db2.id]
}

output "security_group_private_lambda_id" {
  value = aws_security_group.private_lambda_sg.id
}
