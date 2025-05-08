resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_app_environment" "env" {
  name                = "qualidadearsmac-env"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_storage_account" "storage" {
  name                     = "qualidadearsmacstorage"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_share" "timescaledb_share" {
  name               = "timescaledb-share"
  storage_account_id = azurerm_storage_account.storage.id
  quota              = 5
}

resource "azurerm_storage_share" "pgadmin_share" {
  name               = "pgadmin-share"
  storage_account_id = azurerm_storage_account.storage.id
  quota              = 5
}

resource "azurerm_storage_share" "airflow_share" {
  name               = "airflow-share"
  storage_account_id = azurerm_storage_account.storage.id
  quota              = 5
}

resource "azurerm_storage_share" "grafana_share" {
  name               = "grafana-share"
  storage_account_id = azurerm_storage_account.storage.id
  quota              = 5
}

resource "azurerm_container_app_environment_storage" "timescaledb_env_storage" {
  name                         = "timescaledb-env-storage"
  container_app_environment_id = azurerm_container_app_environment.env.id
  account_name                 = azurerm_storage_account.storage.name
  share_name                   = azurerm_storage_share.timescaledb_share.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  access_mode                  = "ReadOnly"
}

resource "azurerm_container_app_environment_storage" "pgadmin_env_storage" {
  name                         = "pgadmin-env-storage"
  container_app_environment_id = azurerm_container_app_environment.env.id
  account_name                 = azurerm_storage_account.storage.name
  share_name                   = azurerm_storage_share.pgadmin_share.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  access_mode                  = "ReadOnly"
}

resource "azurerm_container_app_environment_storage" "airflow_env_storage" {
  name                         = "airflow-env-storage"
  container_app_environment_id = azurerm_container_app_environment.env.id
  account_name                 = azurerm_storage_account.storage.name
  share_name                   = azurerm_storage_share.airflow_share.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  access_mode                  = "ReadOnly"
}

resource "azurerm_container_app_environment_storage" "grafana_env_storage" {
  name                         = "grafana-env-storage"
  container_app_environment_id = azurerm_container_app_environment.env.id
  account_name                 = azurerm_storage_account.storage.name
  share_name                   = azurerm_storage_share.grafana_share.name
  access_key                   = azurerm_storage_account.storage.primary_access_key
  access_mode                  = "ReadOnly"
}

# Upload all files in the timescaledb folder to the storage share
resource "azurerm_storage_share_file" "timescaledb_files" {
  for_each           = fileset("${path.root}/timescaledb", "*")
  name               = each.value
  storage_share_id   = azurerm_storage_share.timescaledb_share.url
  source             = "${path.root}/timescaledb/${each.value}"
}

# Upload all files in the pgadmin folder to the storage share
resource "azurerm_storage_share_file" "pgadmin_files" {
  for_each           = fileset("${path.root}/pgadmin", "*")
  name               = each.value
  storage_share_id   = azurerm_storage_share.pgadmin_share.url
  source             = "${path.root}/pgadmin/${each.value}"
}

# Upload all files in the airflow folder to the storage share
resource "azurerm_storage_share_file" "airflow_files" {
  for_each           = fileset("${path.root}/airflow", "*")
  name               = each.value
  storage_share_id   = azurerm_storage_share.airflow_share.url
  source             = "${path.root}/airflow/${each.value}"
}

# Upload all files in the grafana folder to the storage share
resource "azurerm_storage_share_directory" "grafana_dashboards_files" {
  name               = "dashboards"
  storage_share_id   = azurerm_storage_share.grafana_share.url
}
resource "azurerm_storage_share_directory" "grafana_datasources_files" {
  name               = "datasources"
  storage_share_id   = azurerm_storage_share.grafana_share.url
}
resource "azurerm_storage_share_file" "grafana_files" {
  for_each           = fileset("${path.root}/grafana", "**/*")
  path               = dirname(each.value)
  name               = basename(each.value)
  storage_share_id   = azurerm_storage_share.grafana_share.url
  source             = "${path.root}/grafana/${each.value}"
  depends_on = [
    azurerm_storage_share_directory.grafana_dashboards_files,
    azurerm_storage_share_directory.grafana_datasources_files,
  ]
}

resource "azurerm_container_app" "timescaledb" {
  name                         = "timescaledb"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {

    revision_suffix = "first-revision"

    container {
      name   = "timescaledb"
      image  = "timescale/timescaledb-ha:pg17.2-ts2.18.0-all"
      cpu    = 2
      memory = "4Gi"
      env {
        name  = "POSTGRES_PASSWORD"
        value = "SuperSecret"
      }
      volume_mounts {
        name = "init-script-volume"
        path = "/docker-entrypoint-initdb.d/init.sh"
        sub_path = "init.sh"
      }
      volume_mounts {
        name = "dump-file-volume"
        path = "/docker-entrypoint-initdb.d/postgres.dump"
        sub_path = "postgres.dump"
      }
    }

    volume {
      name         = "init-script-volume"
      storage_name = azurerm_container_app_environment_storage.timescaledb_env_storage.name
      storage_type = "AzureFile"
    }

    volume {
      name         = "dump-file-volume"
      storage_name = azurerm_container_app_environment_storage.timescaledb_env_storage.name
      storage_type = "AzureFile"
    }
  }

  ingress {
    external_enabled = false
    exposed_port     = 5432
    target_port      = 5432
    transport        = "tcp"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

}

resource "azurerm_container_app" "pgadmin" {
  name                         = "pgadmin"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {

    revision_suffix = "first-revision"

    container {
      name   = "pgadmin"
      image  = "dpage/pgadmin4:8.14.0"
      cpu    = 2
      memory = "4Gi"
      env {
        name  = "PGADMIN_DEFAULT_EMAIL"
        value = "esign@esign.com.br"
      }
      env {
        name  = "PGADMIN_DEFAULT_PASSWORD"
        value = "S3cr3t"
      }
      env {
        name  = "PGADMIN_CONFIG_UPGRADE_CHECK_ENABLED"
        value = "False"
      }
      env {
        name  = "PGADMIN_LISTEN_PORT"
        value = "8080"
      }
      volume_mounts {
        name = "servers-json-volume"
        path = "/pgadmin4/servers.json"
        sub_path = "servers.json"
      }
      volume_mounts {
        name = "pgpass-volume"
        path = "/pgadmin4/pgpass"
        sub_path = "pgpass"
      }
      command = [
        "/bin/sh"
      ]
      args = [
        "-c",
        "mkdir /var/lib/pgadmin/storage && mkdir /var/lib/pgadmin/storage/esign_esign.com.br && cp /pgadmin4/pgpass /var/lib/pgadmin/storage/esign_esign.com.br/ && chmod 600 /var/lib/pgadmin/storage/esign_esign.com.br/pgpass && /entrypoint.sh"
      ]
    }

    volume {
      name         = "servers-json-volume"
      storage_name = azurerm_container_app_environment_storage.pgadmin_env_storage.name
      storage_type = "AzureFile"
    }

    volume {
      name         = "pgpass-volume"
      storage_name = azurerm_container_app_environment_storage.pgadmin_env_storage.name
      storage_type = "AzureFile"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "http"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  depends_on = [ azurerm_container_app.timescaledb ]

}

resource "azurerm_container_app" "airflow" {
  name                         = "airflow"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {

    revision_suffix = "first-revision"

    container {
      name   = "airflow"
      image  = "apache/airflow:slim-2.10.4-python3.9"
      cpu    = 2
      memory = "4Gi"
      env {
        name  = "_AIRFLOW_DB_MIGRATE"
        value = "true"
      }
      env {
        name  = "_AIRFLOW_WWW_USER_CREATE"
        value = "true"
      }
      env {
        name  = "_AIRFLOW_WWW_USER_USERNAME"
        value = "airflow"
      }
      env {
        name  = "_AIRFLOW_WWW_USER_PASSWORD"
        value = "airflow"
      }
      env {
        name  = "_PIP_ADDITIONAL_REQUIREMENTS"
        value = "qarsmac[timescaledb]"
      }
      env {
        name  = "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION"
        value = "false"
      }
      volume_mounts {
        name = "airflow-dags-volume"
        path = "/opt/airflow/dags"
      }
      args = [ "standalone" ]
    }

    volume {
      name         = "airflow-dags-volume"
      storage_name = azurerm_container_app_environment_storage.airflow_env_storage.name
      storage_type = "AzureFile"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 8080
    transport        = "http"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  depends_on = [ azurerm_container_app.timescaledb ]

}

resource "azurerm_container_app" "grafana" {
  name                         = "grafana"
  container_app_environment_id = azurerm_container_app_environment.env.id
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"

  template {

    revision_suffix = "first-revision"

    container {
      name   = "grafana"
      image  = "grafana/grafana:11.4.0"
      cpu    = 2
      memory = "4Gi"
      env {
        name  = "GF_SECURITY_ADMIN_PASSWORD"
        value = "S3cr3t"
      }
      env {
        name  = "GF_AUTH_ANONYMOUS_ENABLED"
        value = "true"
      }
      env {
        name  = "POSTGRES_URL"
        value = "timescaledb:5432"
      }
      env {
        name  = "POSTGRES_PASSWORD"
        value = "SuperSecret"
      }
      volume_mounts {
        name = "datasources-volume"
        path = "/etc/grafana/provisioning/datasources"
        sub_path = "datasources"
      }
      volume_mounts {
        name = "dashboards-volume"
        path = "/etc/grafana/provisioning/dashboards"
        sub_path = "dashboards"
      }
    }

    volume {
      name         = "datasources-volume"
      storage_name = azurerm_container_app_environment_storage.grafana_env_storage.name
      storage_type = "AzureFile"
    }

    volume {
      name         = "dashboards-volume"
      storage_name = azurerm_container_app_environment_storage.grafana_env_storage.name
      storage_type = "AzureFile"
    }
  }

  ingress {
    external_enabled = true
    target_port      = 3000
    transport        = "http"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  depends_on = [ azurerm_container_app.timescaledb ]

}
