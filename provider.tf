terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "4.27.0"
    }
  }
  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "azurerm" {
  subscription_id = "92a7a0f2-c2e3-4662-8758-4bc61cfb1d60"
  features {}
}
