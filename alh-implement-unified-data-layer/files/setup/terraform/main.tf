resource "oci_objectstorage_bucket" "workshop" {
  compartment_id = var.compartment_ocid
  namespace      = data.oci_objectstorage_namespace.current.namespace
  name           = local.bucket_name
  access_type    = "NoPublicAccess"
  storage_tier   = "Standard"
  versioning     = "Disabled"

  freeform_tags = {
    workshop = "alh-implement-unified-data-layer"
    managed  = "terraform"
  }
}

resource "oci_objectstorage_object" "csv_seed" {
  for_each = local.csv_files

  namespace    = data.oci_objectstorage_namespace.current.namespace
  bucket       = oci_objectstorage_bucket.workshop.name
  object       = "source-data/${each.value}"
  source       = "${local.source_data_root}/${each.value}"
  content_type = "text/csv"

  metadata = {
    layer       = "bronze-source"
    workshop-id = "alh-unified-data-layer"
  }
}

resource "oci_objectstorage_object" "document_seed" {
  for_each = local.document_files

  namespace    = data.oci_objectstorage_namespace.current.namespace
  bucket       = oci_objectstorage_bucket.workshop.name
  object       = "documents/${each.value}"
  source       = "${local.document_root}/${each.value}"
  content_type = "application/pdf"

  metadata = {
    content-kind = "unstructured-project-evidence"
    workshop-id  = "alh-unified-data-layer"
  }
}

resource "oci_database_autonomous_database" "lakehouse" {
  compartment_id           = var.compartment_ocid
  display_name             = local.database_display
  db_name                  = local.database_name
  db_workload              = "LH"
  db_version               = "26ai"
  compute_model            = "ECPU"
  compute_count            = var.compute_count
  data_storage_size_in_tbs = var.data_storage_size_in_tbs
  admin_password           = random_password.database_admin.result
  is_auto_scaling_enabled  = false
  # Public endpoints without an ACL must require wallet-based mTLS connections.
  is_mtls_connection_required = true
  license_model            = var.license_model

  freeform_tags = {
    workshop = "alh-implement-unified-data-layer"
    managed  = "terraform"
  }

  timeouts {
    create = "2h"
    update = "2h"
    delete = "2h"
  }
}

resource "oci_identity_dynamic_group" "lakehouse" {
  count = var.create_iam_resources ? 1 : 0

  compartment_id = var.tenancy_ocid
  name           = local.dynamic_group_name
  description    = "Allows the unified data layer workshop Autonomous AI Lakehouse to use its resource principal."
  matching_rule  = "resource.id = '${oci_database_autonomous_database.lakehouse.id}'"
}

resource "oci_identity_policy" "object_storage_read" {
  count = var.create_iam_resources ? 1 : 0

  compartment_id = var.tenancy_ocid
  name           = local.policy_name
  description    = "Allows the workshop lakehouse resource principal to list the workshop bucket and read its seed objects."
  statements = [
    "Allow dynamic-group ${oci_identity_dynamic_group.lakehouse[0].name} to inspect buckets in compartment id ${var.compartment_ocid}",
    "Allow dynamic-group ${oci_identity_dynamic_group.lakehouse[0].name} to read objects in compartment id ${var.compartment_ocid}"
  ]
}

resource "null_resource" "upload_embedding_model" {
  triggers = {
    bucket       = oci_objectstorage_bucket.workshop.name
    namespace    = data.oci_objectstorage_namespace.current.namespace
    model_uri    = var.embedding_model_download_uri
    model_object = local.model_object_name
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    environment = {
      BUCKET_NAME  = self.triggers.bucket
      NAMESPACE    = self.triggers.namespace
      MODEL_URI    = self.triggers.model_uri
      MODEL_OBJECT = self.triggers.model_object
      RUNTIME_DIR  = local.runtime_directory
    }
    command = <<-SCRIPT
      set -euo pipefail
      mkdir -p "$RUNTIME_DIR/model"
      curl --fail --location --retry 3 "$MODEL_URI" --output "$RUNTIME_DIR/model/model.zip"
      python3 -c "import zipfile; z=zipfile.ZipFile('$RUNTIME_DIR/model/model.zip'); n=next(x for x in z.namelist() if x.endswith('.onnx')); open('$RUNTIME_DIR/model/all_MiniLM_L12_v2.onnx','wb').write(z.read(n))"
      oci os object put \
        --namespace "$NAMESPACE" \
        --bucket-name "$BUCKET_NAME" \
        --name "$MODEL_OBJECT" \
        --file "$RUNTIME_DIR/model/all_MiniLM_L12_v2.onnx" \
        --content-type "application/octet-stream" \
        --force
    SCRIPT
  }

  provisioner "local-exec" {
    when        = destroy
    on_failure  = continue
    interpreter = ["/bin/bash", "-c"]
    environment = {
      BUCKET_NAME  = self.triggers.bucket
      NAMESPACE    = self.triggers.namespace
      MODEL_OBJECT = self.triggers.model_object
    }
    command = <<-SCRIPT
      oci os object delete \
        --namespace "$NAMESPACE" \
        --bucket-name "$BUCKET_NAME" \
        --object-name "$MODEL_OBJECT" \
        --force || true
    SCRIPT
  }

  depends_on = [oci_objectstorage_bucket.workshop]
}

resource "null_resource" "generate_wallet" {
  triggers = {
    database_id = oci_database_autonomous_database.lakehouse.id
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    environment = {
      DATABASE_ID    = oci_database_autonomous_database.lakehouse.id
      DATABASE_NAME  = oci_database_autonomous_database.lakehouse.db_name
      ADMIN_PASSWORD = nonsensitive(random_password.database_admin.result)
      RUNTIME_DIR    = local.runtime_directory
    }
    command = <<-SCRIPT
      set -euo pipefail
      mkdir -p "$RUNTIME_DIR"
      oci db autonomous-database generate-wallet \
        --autonomous-database-id "$DATABASE_ID" \
        --password "$ADMIN_PASSWORD" \
        --generate-type SINGLE \
        --file "$RUNTIME_DIR/wallet.zip"
      python3 -c "import json,re,zipfile; p='$RUNTIME_DIR/wallet.zip'; t=zipfile.ZipFile(p).read('tnsnames.ora').decode(); m=re.search(r'^(\\S+_high)\\s*=',t,re.M); json.dump({'wallet_path':p,'tns_alias':m.group(1) if m else '${local.database_name}_high'},open('$RUNTIME_DIR/connection.json','w'))"
    SCRIPT
  }
}

resource "null_resource" "bootstrap_database" {
  triggers = {
    database_id          = oci_database_autonomous_database.lakehouse.id
    workshop_username    = var.workshop_username
    workshop_password_id = sha256(nonsensitive(random_password.workshop_user.result))
    schema_script        = filesha256("${local.sql_root}/00_create_schemas.sql")
    ddl_script           = filesha256("${local.sql_root}/01_create_tables.sql")
    seed_script          = filesha256("${local.sql_root}/02_seed_data.sql")
    model_prep_script    = filesha256("${local.sql_root}/03_prepare_vector_model.sql")
    model_load_script    = filesha256("${local.sql_root}/04_load_vector_model.sql")
    finalize_script      = filesha256("${local.sql_root}/05_finalize_environment.sql")
  }

  provisioner "local-exec" {
    interpreter = ["/bin/bash", "-c"]
    environment = {
      ADMIN_PASSWORD    = nonsensitive(random_password.database_admin.result)
      WORKSHOP_USER     = var.workshop_username
      WORKSHOP_PASSWORD = nonsensitive(random_password.workshop_user.result)
      OBJECT_BASE_URI   = local.object_base_uri
      MODEL_OBJECT_URI  = local.model_object_uri
      RUNTIME_DIR       = local.runtime_directory
      SQL_ROOT          = local.sql_root
    }
    command = <<-SCRIPT
      set -euo pipefail
      TNS_ALIAS=$(python3 -c "import json; print(json.load(open('$RUNTIME_DIR/connection.json'))['tns_alias'])")
      WALLET_PATH=$(python3 -c "import json; print(json.load(open('$RUNTIME_DIR/connection.json'))['wallet_path'])")

      sql -cloudconfig "$WALLET_PATH" "admin/$ADMIN_PASSWORD@$TNS_ALIAS" @"$SQL_ROOT/00_create_schemas.sql" "$WORKSHOP_USER" "$WORKSHOP_PASSWORD"
      sql -cloudconfig "$WALLET_PATH" "admin/$ADMIN_PASSWORD@$TNS_ALIAS" @"$SQL_ROOT/01_create_tables.sql"
      sql -cloudconfig "$WALLET_PATH" "admin/$ADMIN_PASSWORD@$TNS_ALIAS" @"$SQL_ROOT/02_seed_data.sql" "$OBJECT_BASE_URI"
      sql -cloudconfig "$WALLET_PATH" "admin/$ADMIN_PASSWORD@$TNS_ALIAS" @"$SQL_ROOT/03_prepare_vector_model.sql" "$WORKSHOP_USER"
      MODEL_READY=false
      for attempt in $(seq 1 15); do
        if sql -cloudconfig "$WALLET_PATH" "$WORKSHOP_USER/$WORKSHOP_PASSWORD@$TNS_ALIAS" @"$SQL_ROOT/04_load_vector_model.sql" "$MODEL_OBJECT_URI"; then
          MODEL_READY=true
          break
        fi
        echo "Resource-principal access is not ready yet (attempt $attempt of 15); retrying in 60 seconds."
        sleep 60
      done
      if [ "$MODEL_READY" != "true" ]; then
        echo "ERROR: The database resource principal could not read the ONNX model object after 15 attempts."
        exit 1
      fi
      sql -cloudconfig "$WALLET_PATH" "admin/$ADMIN_PASSWORD@$TNS_ALIAS" @"$SQL_ROOT/05_finalize_environment.sql" "$WORKSHOP_USER"
    SCRIPT
  }

  depends_on = [
    null_resource.generate_wallet,
    null_resource.upload_embedding_model,
    oci_objectstorage_object.csv_seed,
    oci_objectstorage_object.document_seed,
    oci_identity_policy.object_storage_read
  ]
}
