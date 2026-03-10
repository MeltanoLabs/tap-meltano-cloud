# tap-meltanocloud

`tap-meltanocloud` is a Singer tap for [MeltanoCloud](https://www.matatika.com), extracting workspaces, pipelines, datasets, jobs, channels, data stores, and data components.

Built with the [Meltano Singer SDK](https://sdk.meltano.com).

## Installation

Install from GitHub:

```bash
uv tool install git+https://github.com/Matatika/tap-meltanocloud.git@main
```

## Streams

| Stream | Endpoint | Primary Key |
|:-------|:---------|:------------|
| `workspaces` | `GET /workspaces/{workspace_id}` | `id` |
| `pipelines` | `GET /workspaces/{workspace_id}/pipelines` | `id` |
| `datasets` | `GET /workspaces/{workspace_id}/datasets` | `id` |
| `jobs` | `GET /workspaces/{workspace_id}/jobs` | `id` |
| `channels` | `GET /workspaces/{workspace_id}/channels` | `id` |
| `datastores` | `GET /workspaces/{workspace_id}/datastores` | `id` |
| `datacomponents` | `GET /workspaces/{workspace_id}/datacomponents` | `id` |

Schemas are derived directly from the [MeltanoCloud OpenAPI specification](tap_meltanocloud/openapi/openapi.json).

## Configuration

### Accepted Config Options

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| auth_token | True | None | The token to authenticate against the API service |
| workspace_ids | True | None | Workspace IDs to replicate |
| start_date | False | None | The earliest record date to sync |
| api_url | False | https://app.matatika.com/api | The url for the API service |

A full list of supported settings and capabilities is available by running:

```bash
tap-meltanocloud --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

### Source Authentication and Authorization

Authentication uses a **Bearer token**. Obtain your API token from the MeltanoCloud / Matatika platform and set it as `auth_token` (or `TAP_MELTANOCLOUD_AUTH_TOKEN` environment variable).

## Usage

### Executing the Tap Directly

```bash
tap-meltanocloud --version
tap-meltanocloud --help
tap-meltanocloud --config config.json --discover > ./catalog.json
tap-meltanocloud --config config.json --catalog catalog.json
```

Example `config.json`:

```json
{
  "auth_token": "your-token-here",
  "workspace_ids": ["your-workspace-id"]
}
```

### Using with Meltano

```bash
meltano add extractor tap-meltanocloud --from-ref https://raw.githubusercontent.com/Matatika/tap-meltanocloud/main/meltano.yml
meltano run tap-meltanocloud target-jsonl
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

Tests require `TAP_MELTANOCLOUD_AUTH_TOKEN` and `TAP_MELTANOCLOUD_WORKSPACE_IDS` environment variables to run against the live API. Copy `.env.example` to `.env` and fill in your credentials.

### SDK Dev Guide

See the [Singer SDK dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more details.
