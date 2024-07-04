variable "prj_prefix" {}
variable "environment" {}

variable "region_api" {}
variable "region_site" {}
variable "region_acm" {}

variable "route53_zone_id" {}
variable "domain_api" {}
variable "domain_static_site" {}
variable "domain_media_site" {}

#variable "vpc_availability_zones" {}
#variable "app_is_enabled" {}


provider "aws" {
  region = var.region_api
}

terraform {
  backend "s3" {
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.74.2"
    }
  }
}

# Route53 and ACM
module "module_domain_api" {
  source          = "./modules/aws/domain_api"
  prj_prefix      = var.prj_prefix
  route53_zone_id = var.route53_zone_id
  domain_api      = var.domain_api
  region_api      = var.region_api
  region_acm      = var.region_acm
}

module "module_static_site" {
  source             = "./modules/aws/static_site"
  prj_prefix         = var.prj_prefix
  route53_zone_id    = var.route53_zone_id
  domain_static_site = var.domain_static_site
  domain_media_site  = var.domain_media_site
  region_site        = var.region_site
  region_acm         = var.region_acm
}

## VPC
#module "module_vpc" {
#  source             = "./modules/aws/vpc"
#  availability_zones = var.vpc_availability_zones
#  prj_prefix         = var.prj_prefix
#}

