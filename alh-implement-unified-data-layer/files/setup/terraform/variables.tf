variable "tenancy_ocid" {
  description = "OCID of the OCI tenancy. Required to create the Autonomous Database dynamic group and policy."
  type        = string
}

variable "compartment_ocid" {
  description = "OCID of the compartment in which the Autonomous AI Lakehouse and Object Storage bucket are created."
  type        = string
}

variable "region" {
  description = "OCI region identifier, for example us-ashburn-1."
  type        = string
}

variable "name_prefix" {
  description = "Prefix used for workshop resource display names."
  type        = string
  default     = "alh-unified-data"

  validation {
    condition     = can(regex("^[a-zA-Z][a-zA-Z0-9-]{2,30}$", var.name_prefix))
    error_message = "name_prefix must begin with a letter and contain 3-31 letters, digits, or hyphens."
  }
}

variable "workshop_username" {
  description = "Database user used by workshop attendees to sign in to Database Actions."
  type        = string
  default     = "SEER_WORKSHOP"

  validation {
    condition     = can(regex("^[A-Z][A-Z0-9_]{2,29}$", var.workshop_username))
    error_message = "workshop_username must be an uppercase Oracle identifier of 3-30 characters."
  }
}

variable "compute_count" {
  description = "ECPU count for the Autonomous AI Lakehouse."
  type        = number
  default     = 2

  validation {
    condition     = var.compute_count >= 2
    error_message = "Autonomous AI Lakehouse with the ECPU model requires at least 2 ECPUs outside an elastic pool."
  }
}

variable "data_storage_size_in_tbs" {
  description = "Data storage assigned to the Autonomous AI Lakehouse, in terabytes."
  type        = number
  default     = 1
}

variable "license_model" {
  description = "Autonomous AI Database license model."
  type        = string
  default     = "LICENSE_INCLUDED"

  validation {
    condition     = contains(["LICENSE_INCLUDED", "BRING_YOUR_OWN_LICENSE"], var.license_model)
    error_message = "license_model must be LICENSE_INCLUDED or BRING_YOUR_OWN_LICENSE."
  }
}

variable "create_iam_resources" {
  description = "Create the dynamic group and Object Storage read policy required by the database resource principal."
  type        = bool
  default     = true
}

variable "embedding_model_download_uri" {
  description = "Oracle public download URL for the augmented all-MiniLM-L12-v2 ONNX model ZIP. Override if Oracle rotates the published PAR URL."
  type        = string
  default     = "https://adwc4pm.objectstorage.us-ashburn-1.oci.customer-oci.com/p/TtH6hL2y25EypZ0-rrczRZ1aXp7v1ONbRBfCiT-BDBN8WLKQ3lgyW6RxCfIFLdA6/n/adwc4pm/b/OML-ai-models/o/all_MiniLM_L12_v2_augmented.zip"
}
