# Installation guide

This guide provides step-by-step procedure of installing WithSecure data connector for 
Azure Sentinel.

## Prerequisites

1. Access to Azure account with installed Sentinel solution.
2. Workstation with installed [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/).
3. Access to [WithSecure Elements Security Center](https://elements.withsecure.com).

### Installation

Connector installation has following steps:

1. Create Elements API credentials
2. Create Azure Entra application.
3. Deploy Azure resources.
4. Preparing installation package.
5. Package installation.

Log Analytics Workspace is not managed with provided deployment templates. It can be created
manually in Azure Portal or from command line. All resources that are mentioned in this 
guide must be deployed in the same resource group where the Log Analytics Workspace is 
created. In next paragraphs we will be using example resource group called `UserGuide`.

![UserGuide resource group with Log Analytics Workspace and Sentinel solution](images/resource_group_before_ok.png)

#### Create Elements API credentials

#### Create Azure Entra application
