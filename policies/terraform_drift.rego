package terraform

# Deny any aws_s3_bucket without server-side encryption
deny[msg] {
  resource := input.planned_values.root_module.resources[_]
  resource.type == "aws_s3_bucket"
  not resource.values.server_side_encryption_configuration
  msg := sprintf("Bucket %v has no SSE config", [resource.address])
}
