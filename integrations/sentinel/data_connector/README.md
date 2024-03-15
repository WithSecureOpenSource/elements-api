# Sentinel Connector with Azure Function

## Requirements

- Python 3.10.x
- Poetry (https://python-poetry.org/)
- Azure CLI (https://learn.microsoft.com/en-us/cli/azure/)

## Project structure 

- `app/function_app.py` - entry point for Azure Function
- `app/lib/` - connector implementation responsible for reading data from Elements API and
   pushing data to Azure Log Workspace
- `deploy/` - Azure ARM deployment templates
- `tests/` - unit tests
- `scripts/` - additional scripts that can be executed from poetry
- `poetry.toml` - poetry configuration
- `pyproject.toml` - project configuration (dependencies, additional tools, scripts, etc)

## Installation in Azure Cloud

Connector installation has following steps:

1. Create Elements API credentials
2. Creating Azure Entra application.
3. Deploying Azure resources.
4. Preparing installation package.
5. Package installation.

Log Analytics Workspace is not managed with provided deployment templates. It can be created
manually in Azure Portal or from command line. All resources must be deployed in the same
resource group where Log Analytics Workspace is created. In next paragraphs this group is  
referenced as `$resource_group`.

Installation requires working Azure CLI. Run `az version` to verify if tool is available.

### Create Elements API credentials

Follow user guide to create Elements API credentials. Save credentials in safe place.

### Create Azure Entra application

Create new [Entra Application](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/tutorial-logs-ingestion-portal#create-microsoft-entra-application)
   and credentials. Save secret key in safe place.

### Deploying connector

In this step all resources that are required by Connector are deployed and linked with 
existing Log Analytics Workspace and Entra Application.

1. Adjust file `deploy/connector_app_parameters.json`. Set required values:
 - `workspaceName` - name of **existing** Log Analytics Workspace,
 - `entraObjectId` - principal id of Entra Application. Can be found in Entra Application,
    under link `Managed application in local directory` in field `Object ID`,
 - `elementsApiClientId` - client id from the WithSecure Elements Portal,
 - `elementsApiClientSecret` - client secret from WithSecure Elements Portal,
 - `entraTenantId`- value of `Directory (client) ID` property in Entra Application management console, 
 - `entraClientId`- value of `Application (client) ID` property in Entra Application management console,
 - `entraClientSecret` - secret key from Application credentials.
 
2. Execute command `az deployment group create --name ConnectorApp --resource-group $resource_group --template-file deploy/azuredeploy_connector_app.json --parameters deploy/connector_app_parameters.json` 

### Building installation package

1. Run `poetry install --only main --remove-untracked` to install connector's dependencies 
   in local `.venv` virtual environment. When `--only main` is present poetry will skip 
   development dependencies (`black`, `pytest`, etc).
   
2. Run `poetry run dist-app`. Command creates deployment package `app.zip` in `target` 
   directory.

### Connector installation

1. Run command `az functionapp deployment source config-zip --resource-group $resource_group --name $azure_function --src target/app.zip`

2. Use command `az functionapp show --resource-group $resource_group --name $azure_function` 
   to get function details. Find property `lastModifiedTimeUtc` to verify last modification 
   date.
3. Wait until new events arrive in table `WsSecurityEvents_CL`.

## Development

### Testing

1. Tests are kept in directory `tests/`. To execute whole suite run command `poetry run pytest`.
2. Run `poetry run pyflakes app/` to verify program correctness.

### Formatting

Execute `poetry run black .` to format all files in directory

### Local Run

Simplest way to test and run function locally is to use VS Code with following extensions:

* [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
* [Azure Functions](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-azurefunctions)
* [Azurite V3](https://marketplace.visualstudio.com/items?itemName=Azurite.azurite)

Start with verifying installation of Azure Functions Core Tools. In VS Code press `F1` then start command:

    Azure Functions: Install or Update Core Tools

Then next step is to start Azure emulator. In VS Code press `F1` and run command

    Azurite: Start

Running services should appear on the bottom status bar in VS Code.

To start function in emulator it needs to be appended to Azure Functions. To do so go to **Run and Debug** and select
**Attach to Python Functions** or simply use shortcut `F5` in VS Code. Function should automatically start locally.

To learn more visit:
[Quickstart: Create a function in Azure with Python using VS Code](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-decorators)


## Troubleshooting

**Security Events are missing**

1. Open invocation logs in Azure Function console.
2. Check if most recent logs contains entry starting with `Execution error`.
3. If there is no error it means that function works as expected. However in Log Analytics 
   workspace new events might appear with bigger delay.
4. Check if most recent logs contains entry starting with `Found 0 events since $date`.
5. Check security events in Elements Portal. If all events are older that `$date` then
   connector works as expected.
6. Otherwise find transaction id (`X-Transaction`) from last request to Elements API and 
   contact with support team.
   
**Function handler is not visible in functions list**

If `upload_security_events` function is missing on list it might indicate that Azure couldn't 
initialize it. It might be caused by missing dependencies, error in module initialization 
or wrong runtime used to build package. There is no easy way to find reason why Azure couldn't 
initialize function. The only method is `trial and error`.
