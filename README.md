# tap-meltano-cloud

`tap-meltano-cloud` is a Singer tap for [MeltanoCloud](https://www.matatika.com), extracting workspaces, pipelines, datasets, jobs, channels, data stores, and data components.

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Installation

Install from GitHub:

```bash
uv tool install git+https://github.com/Matatika/tap-meltano-cloud.git@main
```

## Streams

| Stream | Endpoint | Primary Key |
|:-------|:---------|:------------|
| `workspaces` | `GET /workspaces` | `id` |
| `pipelines` | `GET /workspaces/{workspaceId}/pipelines` | `id` |
| `datasets` | `GET /workspaces/{workspaceId}/datasets` | `id` |
| `jobs` | `GET /workspaces/{workspaceId}/jobs` | `id` |
| `channels` | `GET /workspaces/{workspaceId}/channels` | `id` |
| `datastores` | `GET /workspaces/{workspaceId}/datastores` | `id` |
| `datacomponents` | `GET /workspaces/{workspaceId}/datacomponents` | `id` |

Schemas are derived directly from the [MeltanoCloud OpenAPI specification](tap_meltano_cloud/openapi/openapi.json).

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| auth_token | True | None | The token to authenticate against the API service |
| api_url | False | https://app.matatika.com/api | The url for the API service |
| workspace_ids | False | None | List of workspace IDs to sync. When set, only the specified workspaces are fetched individually without requiring the workspaces list endpoint. When omitted, all workspaces accessible to the authenticated user are discovered and synced. |

A full list of supported settings and capabilities is available by running:

```bash
tap-meltano-cloud --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

Authentication uses a **Bearer token**. Obtain your API token from the MeltanoCloud / Matatika platform and set it as `auth_token` (or `TAP_MELTANO_CLOUD_AUTH_TOKEN` environment variable).

## Usage

### Executing the Tap Directly

```bash
tap-meltano-cloud --version
tap-meltano-cloud --help
tap-meltano-cloud --config config.json --discover > ./catalog.json
tap-meltano-cloud --config config.json --catalog catalog.json
```

Example `config.json`:

```json
{
  "auth_token": "your-token-here"
}
```

### Using with Meltano

```bash
meltano add extractor tap-meltano-cloud --from-ref https://raw.githubusercontent.com/Matatika/tap-meltano-cloud/main/meltano.yml
meltano run tap-meltano-cloud target-jsonl
```

## Developer Resources

### Initialize your Development Environment

Prerequisites: Python 3.10+, [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### Running Tests

```bash
uv run pytest
```

Tests require `TAP_MELTANO_CLOUD_AUTH_TOKEN` to run against the live API. Copy `.env.example` to `.env` and fill in your credentials.

### SDK Dev Guide

See the [Singer SDK dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more details.
