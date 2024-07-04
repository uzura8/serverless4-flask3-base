variable "prj_prefix" {}
variable "availability_zones" {}

#data "aws_availability_zones" "available" {
#  state = "available"
#}


resource "aws_vpc" "this" {
  cidr_block           = "10.0.0.0/16"
  instance_tenancy     = "default"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name      = join("-", [var.prj_prefix, "vpc"])
    ManagedBy = "terraform"
  }
}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags = {
    Name      = join("-", [var.prj_prefix, "igw"])
    ManagedBy = "terraform"
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.this.id
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "rtb", "public"])
    ManagedBy = "terraform"
  }
}

resource "aws_subnet" "public_web1" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.0.0.0/24"
  availability_zone       = var.availability_zones[0]
  map_public_ip_on_launch = true
  #availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name      = join("-", [var.prj_prefix, "subnet", "web-1"])
    ManagedBy = "terraform"
  }
}
resource "aws_route_table_association" "public_web1" {
  subnet_id      = aws_subnet.public_web1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_subnet" "public_web2" {
  vpc_id                  = aws_vpc.this.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = var.availability_zones[1]
  map_public_ip_on_launch = true
  #availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name      = join("-", [var.prj_prefix, "subnet", "web-2"])
    ManagedBy = "terraform"
  }
}
resource "aws_route_table_association" "public_web2" {
  subnet_id      = aws_subnet.public_web2.id
  route_table_id = aws_route_table.public_rt.id
}

# network db
resource "aws_subnet" "private_db1" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.0.10.0/24"
  availability_zone = var.availability_zones[0]
  #availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name      = join("-", [var.prj_prefix, "subnet", "db-1"])
    ManagedBy = "terraform"
  }
}

resource "aws_subnet" "private_db2" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.0.20.0/24"
  availability_zone = var.availability_zones[1]
  #availability_zone = data.aws_availability_zones.available.names[1]

  tags = {
    Name      = join("-", [var.prj_prefix, "subnet", "db-2"])
    ManagedBy = "terraform"
  }
}

resource "aws_db_subnet_group" "main" {
  description = "It is a DB subnet group on tf_vpc."
  subnet_ids  = [aws_subnet.private_db1.id, aws_subnet.private_db2.id]

  tags = {
    Name      = join("-", [var.prj_prefix, "subnet", "db"])
    ManagedBy = "terraform"
  }
}

# Security Group for Lambda
resource "aws_security_group" "private_lambda_sg" {
  name        = "${var.prj_prefix}-lambda-sg"
  description = "Security group for Lambda functions in VPC"
  vpc_id      = aws_vpc.this.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "${var.prj_prefix}-lambda-sg"
    ManagedBy = "terraform"
  }
}

# Private Subnet for Lambada and NAT Gateway: for availability_zones[0]
resource "aws_subnet" "private_lambda1" {
  vpc_id            = aws_vpc.this.id
  cidr_block        = "10.0.100.0/24"
  availability_zone = var.availability_zones[0]

  tags = {
    Name      = join("-", [var.prj_prefix, "subnet", "lambda-1"])
    ManagedBy = "terraform"
  }
}
resource "aws_eip" "nat1" {
  vpc = true
}
resource "aws_nat_gateway" "nat1" {
  allocation_id = aws_eip.nat1.id
  subnet_id     = aws_subnet.public_web1.id
  depends_on    = [aws_internet_gateway.this]
}
# Route Table to use NAT Gateway for lambda subnet
resource "aws_route_table" "private_lambda1_rt" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat1.id
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "rtb", "private-lambda"])
    ManagedBy = "terraform"
  }
}
resource "aws_route_table_association" "private_lambda1" {
  subnet_id      = aws_subnet.private_lambda1.id
  route_table_id = aws_route_table.private_lambda1_rt.id
}
