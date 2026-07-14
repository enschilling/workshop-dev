terraform {
  required_version = ">= 1.5.0"

  required_providers {
    oci = {
      source  = "oracle/oci"
      version = ">= 8.21.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.7.0"
    }
    null = {
      source  = "hashicorp/null"
      version = ">= 3.2.0"
    }
  }
}

provider "oci" {
  region = var.region
}
