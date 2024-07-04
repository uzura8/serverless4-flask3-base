variable "prj_prefix" {}

variable "region_api" {}
variable "region_acm" {}

variable "route53_zone_id" {}
variable "domain_api" {}

provider "aws" {
  region = var.region_api
  alias  = "api"
}

provider "aws" {
  region = var.region_acm
  alias  = "acm"
}

locals {
  fqdn = {
    api = var.domain_api
  }
}

resource "aws_acm_certificate" "api" {
  provider          = aws.api
  domain_name       = local.fqdn.api
  validation_method = "DNS"

  tags = {
    Name      = join("-", [var.prj_prefix, "acm"])
    ManagedBy = "terraform"
  }
}

resource "aws_route53_record" "api_acm_c" {
  for_each = {
    for d in aws_acm_certificate.api.domain_validation_options : d.domain_name => {
      name   = d.resource_record_name
      record = d.resource_record_value
      type   = d.resource_record_type
    }
  }
  zone_id         = var.route53_zone_id
  name            = each.value.name
  type            = each.value.type
  ttl             = 172800
  records         = [each.value.record]
  allow_overwrite = true
}

### Related ACM Certification and CNAME record
resource "aws_acm_certificate_validation" "api" {
  provider                = aws.api
  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [for record in aws_route53_record.api_acm_c : record.fqdn]
}
