## Track Github repositories with Azure functions

Use the Github API to track the views and clones
of all of your Github repositories.

### Setup
- For local testing rename `local.settings.json.sample` to `local.settings.json`
  and setup the environemnt variables: 
    - `API_KEY`: the Github api key obtained from [here](https://github.com/settings/tokens)
    - `TABLE_SERVICE_CONNECTION_STRING`: the connection string to an Azure storage account
    that has two tables - `gitubclones` and `githubviews`. The results will be stored there.
    - `AzureWebJobsStorage`: the connection string to the storage that is created automatically 
    with the Azure Function App. It can be retrieved from `Settings` -> `Configuration` -> `Application settings`.

- When deploying make sure that all varialbes in `local.settings.json` are also present in
  `Settings` -> `Configuration` -> `Application settings`
