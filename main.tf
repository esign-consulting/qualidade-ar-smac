resource "azurerm_resource_group" "qualidadearsmac_data_resource_group" {
  name     = "qualidadearsmac-data-rg"
  location = "Brazil South"
}

data "azurerm_log_analytics_workspace" "default_log_analytics_workspace" {
  name                = "DefaultWorkspace-92a7a0f2-c2e3-4662-8758-4bc61cfb1d60-CQ"
  resource_group_name = "DefaultResourceGroup-CQ"
}

resource "azurerm_container_app_environment" "qualidadearsmac_container_app_environment" {
  name                       = "qualidadearsmac-data-container-app-env"
  location                   = azurerm_resource_group.qualidadearsmac_data_resource_group.location
  resource_group_name        = azurerm_resource_group.qualidadearsmac_data_resource_group.name
  log_analytics_workspace_id = data.azurerm_log_analytics_workspace.default_log_analytics_workspace.id
}

resource "azurerm_storage_account" "qualidadearsmac_data_storage_account" {
  name                     = "qualidadearsmacdatasa"
  resource_group_name      = azurerm_resource_group.qualidadearsmac_data_resource_group.name
  location                 = azurerm_resource_group.qualidadearsmac_data_resource_group.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_share" "qualidadearsmac_data_storage_share" {
  name               = "qualidadearsmac-data-storage-share"
  storage_account_id = azurerm_storage_account.qualidadearsmac_data_storage_account.id
  quota              = 5
}

resource "azurerm_container_app_environment_storage" "qualidadearsmac_data_container_app_environment_storage" {
  name                         = "qualidadearsmacdatacaes"
  container_app_environment_id = azurerm_container_app_environment.qualidadearsmac_container_app_environment.id
  account_name                 = azurerm_storage_account.qualidadearsmac_data_storage_account.name
  share_name                   = azurerm_storage_share.qualidadearsmac_data_storage_share.name
  access_key                   = azurerm_storage_account.qualidadearsmac_data_storage_account.primary_access_key
  access_mode                  = "ReadOnly"
}

resource "azurerm_storage_container" "timescaledb_storage_container" {
  name                  = "timescaledb"
  storage_account_id    = azurerm_storage_account.qualidadearsmac_data_storage_account.id
  container_access_type = "private"
}

resource "azurerm_storage_blob" "timescaledb_storage_blob" {
  for_each               = fileset("${path.module}/timescaledb", "**/*")
  name                   = each.key
  storage_account_name   = azurerm_storage_account.qualidadearsmac_data_storage_account.name
  storage_container_name = azurerm_storage_container.timescaledb_storage_container.name
  type                   = "Block"
  source                 = "${path.module}/timescaledb/${each.key}"
}

resource "azurerm_container_app" "timescaledb_container_app" {
  name                         = "timescaledb"
  container_app_environment_id = azurerm_container_app_environment.qualidadearsmac_container_app_environment.id
  resource_group_name          = azurerm_resource_group.qualidadearsmac_data_resource_group.name
  revision_mode                = "Single"

  template {
    container {
      name   = "timescaledb"
      image  = "timescale/timescaledb-ha:pg17.2-ts2.18.0-all"
      cpu    = 0.25
      memory = "0.5Gi"
      env {
        name  = "POSTGRES_PASSWORD"
        value = "SuperSecret"
      }
    }
  }

  ingress {
    target_port = 5432
    traffic_weight {
      latest_revision = true
      percentage = 100
    }
  }
}
