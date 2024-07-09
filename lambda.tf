terraform {
  required_providers {
    aws = {
        source = "hashicorp/aws"
    }
  }
}

provider "aws" {
  default_tags {
    tags = {
      "testo:region" = "eu"
      # "testo:owner" = "pi"
      "testo:application" = "metric-exporter-lambda"
      # "testo:stage" = "t"
    }
  }
  region = "eu-central-1"
  assume_role {
    role_arn = "arn:aws:iam::390233841206:role/cms-eu-t-terraform"
  }
}
module "metrics-exporter-lambda" {
  source        = "../../"
  region        = "eu"
  stage            = "t"
  name             = "metrics-exporter-lambda"
  owner            = "jus"
  lambda_handler   = "jira-skript.main"
  lambda_source    = abspath("./source/")
}
