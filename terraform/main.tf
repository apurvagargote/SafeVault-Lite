terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# IAM role for SafeVault application
resource "aws_iam_role" "safevault_role" {
  name = "safevault-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

# IAM policy for Secrets Manager access
resource "aws_iam_policy" "secrets_manager_policy" {
  name = "safevault-secrets-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:CreateSecret",
          "secretsmanager:GetSecretValue",
          "secretsmanager:UpdateSecret",
          "secretsmanager:DeleteSecret",
          "secretsmanager:ListSecrets"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "safevault_policy_attachment" {
  role       = aws_iam_role.safevault_role.name
  policy_arn = aws_iam_policy.secrets_manager_policy.arn
}

# EC2 instance profile
resource "aws_iam_instance_profile" "safevault_profile" {
  name = "safevault-instance-profile"
  role = aws_iam_role.safevault_role.name
}

# Security group
resource "aws_security_group" "safevault_sg" {
  name = "safevault-sg"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance
resource "aws_instance" "safevault_instance" {
  ami                    = "ami-0c02fb55956c7d316" # Amazon Linux 2
  instance_type          = "t3.micro"
  iam_instance_profile   = aws_iam_instance_profile.safevault_profile.name
  vpc_security_group_ids = [aws_security_group.safevault_sg.id]

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker
              systemctl start docker
              systemctl enable docker
              usermod -a -G docker ec2-user
              EOF

  tags = {
    Name = "SafeVault-Instance"
  }
}