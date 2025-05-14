terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# Demo S3 bucket (this will violate our SSE policy)
resource "aws_s3_bucket" "demo" {
  bucket = "compliance-remediator-demo-${random_id.suffix.hex}"
}

resource "random_id" "suffix" {
  byte_length = 4
}
