output "database_admin_password" {
  description = "Generated password for the fixed Autonomous AI Lakehouse ADMIN user. Intentionally shown in plain text for workshop environment creation."
  value       = nonsensitive(random_password.database_admin.result)
  sensitive   = false
}

output "workshop_username" {
  description = "Database Actions user created for workshop attendees."
  value       = var.workshop_username
  sensitive   = false
}

output "workshop_user_password" {
  description = "Generated password for the workshop database user. Intentionally shown in plain text for workshop environment creation."
  value       = nonsensitive(random_password.workshop_user.result)
  sensitive   = false
}

output "autonomous_ai_lakehouse_id" {
  description = "OCID of the Autonomous AI Lakehouse."
  value       = oci_database_autonomous_database.lakehouse.id
}

output "autonomous_ai_lakehouse_display_name" {
  description = "Display name of the Autonomous AI Lakehouse."
  value       = oci_database_autonomous_database.lakehouse.display_name
}

output "autonomous_ai_lakehouse_database_name" {
  description = "Database name used in wallet service aliases."
  value       = oci_database_autonomous_database.lakehouse.db_name
}

output "database_connection_urls" {
  description = "Database Actions and other generated Autonomous AI Lakehouse connection URLs."
  value       = oci_database_autonomous_database.lakehouse.connection_urls
}

output "object_storage_bucket_name" {
  description = "Private Object Storage bucket containing workshop CSVs, PDFs, and the embedding model."
  value       = oci_objectstorage_bucket.workshop.name
}

output "object_storage_namespace" {
  description = "OCI Object Storage namespace."
  value       = data.oci_objectstorage_namespace.current.namespace
}

output "object_storage_base_uri" {
  description = "Base URI used when creating a Data Studio cloud store location."
  value       = local.object_base_uri
}

output "supplier_csv_object_uri" {
  description = "URI of the CSV participants link as their Bronze external table."
  value       = "${local.object_base_uri}source-data/suppliers/supplier_extract.csv"
}

output "environment_bootstrap_status" {
  description = "Completes only after schemas, seeded data, the embedding model, and the vector index are ready."
  value       = null_resource.bootstrap_database.id == null ? "NOT_READY" : "READY"
}
