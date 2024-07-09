module "label" {
  source      = "git::https://github.com/cloudposse/terraform-null-label.git?ref=tags/0.25.0"
  namespace   = var.namespace
  environment = var.region
  stage       = var.stage
  name        = var.name
  tags        = var.additional_tags
}
