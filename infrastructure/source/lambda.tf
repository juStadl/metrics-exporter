module "metrics-exporter-lambda" {
  source         = "git::https://gitlab.cds.testo/infrastructure/terraform/aws-lambda.git?ref=tags/4.1.1"
  region         = var.region
  stage          = var.stage
  name           = var.name
  owner          = var.owner
  lambda_handler = "jira-skript.main"
  lambda_runtime = "python3.12"
  lambda_source  = abspath("./src/")
}
