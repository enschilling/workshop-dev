data "oci_objectstorage_namespace" "current" {
  compartment_id = var.tenancy_ocid
}

resource "random_string" "deployment_id" {
  length  = 8
  upper   = false
  lower   = true
  numeric = true
  special = false
}

resource "random_password" "database_admin" {
  length      = 20
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  special     = false
}

resource "random_password" "workshop_user" {
  length      = 20
  min_upper   = 2
  min_lower   = 2
  min_numeric = 2
  special     = false
}

locals {
  deployment_id = random_string.deployment_id.result

  bucket_name         = "${lower(var.name_prefix)}-${local.deployment_id}"
  database_name       = "alh${local.deployment_id}"
  database_display    = "${var.name_prefix}-${local.deployment_id}"
  runtime_directory   = "${path.module}/.terraform-runtime"
  source_data_root    = fileexists("${path.module}/source-data/suppliers/supplier_extract.csv") ? "${path.module}/source-data" : "${path.module}/../../source-data"
  document_root       = fileexists("${path.module}/documents/austin_structural_engineering_specification.pdf") ? "${path.module}/documents" : "${path.module}/../../documents"
  sql_root            = fileexists("${path.module}/sql/00_create_schemas.sql") ? "${path.module}/sql" : "${path.module}/../../sql"
  object_base_uri     = "https://objectstorage.${var.region}.oraclecloud.com/n/${data.oci_objectstorage_namespace.current.namespace}/b/${local.bucket_name}/o/"
  model_object_name   = "models/all_MiniLM_L12_v2.onnx"
  model_object_uri    = "${local.object_base_uri}${local.model_object_name}"
  csv_files           = fileset(local.source_data_root, "**/*.csv")
  document_files      = fileset(local.document_root, "**/*.pdf")
}
