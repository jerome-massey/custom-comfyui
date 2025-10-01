# Model Downloader Script - Documentation

## Overview

The `download_models.py` script automates the process of downloading ComfyUI models and installing custom nodes from manifest files. It supports multiple manifests, automatic deduplication, and various filtering options.

## Features

✅ **Multiple Manifests**: Load and combine multiple manifest files in a single command
✅ **Automatic Deduplication**: Detects and skips duplicate models/nodes across manifests
✅ **Flexible Sources**: Load from GitHub URLs, web URLs, or local files
✅ **Type Filtering**: Download only specific model types (checkpoints, LoRAs, etc.)
✅ **Hash Verification**: Optional SHA256 verification for file integrity
✅ **Resume Support**: Automatically skips already downloaded files
✅ **Progress Bars**: Visual feedback during downloads
✅ **Dry Run Mode**: Preview what would be downloaded without downloading
✅ **List Mode**: View manifest contents without taking action

## Command Line Usage

### Basic Syntax

```bash
docker compose exec comfyui python /usr/local/bin/download_models.py [OPTIONS] MANIFEST [MANIFEST ...]
```

### Examples

#### Single Manifest

```bash
# Download from GitHub raw URL
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://raw.githubusercontent.com/user/repo/main/manifest.json

# Download from local file
docker compose exec comfyui python /usr/local/bin/download_models.py \
  /path/to/local-manifest.json
```

#### Multiple Manifests (Combines & Deduplicates)

```bash
# Combine multiple manifests - duplicates are automatically detected and skipped
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://example.com/manifest1.json \
  https://example.com/manifest2.json \
  /path/to/local-manifest.json
```

#### Type Filtering

```bash
# Download only checkpoints and LoRAs
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --types checkpoint lora \
  manifest.json

# Available types: checkpoint, vae, lora, controlnet, upscale, embeddings, clip
```

#### Models or Nodes Only

```bash
# Download only models (skip custom nodes)
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --models-only manifest.json

# Install only custom nodes (skip models)
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --nodes-only manifest.json
```

#### Preview and List Modes

```bash
# List manifest contents without downloading
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --list manifest.json

# Dry run - show what would be downloaded
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --dry-run manifest.json
```

## Manifest File Format

### Complete Example

```json
{
  "version": "1.0",
  "description": "Optional description of this manifest",
  "models": [
    {
      "name": "Model Display Name",
      "type": "checkpoint",
      "url": "https://example.com/model.safetensors",
      "path": "models/checkpoints",
      "filename": "custom_filename.safetensors",
      "sha256": "optional-sha256-hash-for-verification",
      "description": "Optional description"
    }
  ],
  "custom_nodes": [
    {
      "name": "Node Display Name",
      "repo": "https://github.com/user/repo.git",
      "path": "custom_nodes",
      "description": "Optional description"
    }
  ]
}
```

### Model Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the model |
| `type` | Yes | Model type: `checkpoint`, `vae`, `lora`, `controlnet`, `upscale`, `embeddings`, `clip` |
| `url` | Yes | Direct download URL (Hugging Face, GitHub releases, etc.) |
| `path` | Yes | Destination folder relative to ComfyUI root (e.g., `models/checkpoints`) |
| `filename` | No | Override the filename (defaults to URL filename) |
| `sha256` | No | SHA256 hash for verification |
| `description` | No | Human-readable description |

### Custom Node Entry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name for the custom node |
| `repo` | Yes | Git repository URL |
| `path` | Yes | Destination folder relative to ComfyUI root (usually `custom_nodes`) |
| `description` | No | Human-readable description |

## Model Types and Paths

| Type | Typical Path | Description |
|------|-------------|-------------|
| `checkpoint` | `models/checkpoints` | Main model files (SD 1.5, SDXL, Flux, etc.) |
| `vae` | `models/vae` | VAE models for improved quality |
| `lora` | `models/loras` | LoRA fine-tuning models |
| `controlnet` | `models/controlnet` | ControlNet guidance models |
| `upscale` | `models/upscale_models` | Upscaling models |
| `embeddings` | `models/embeddings` | Textual inversion embeddings |
| `clip` | `models/clip_vision` | CLIP vision models |

## Hosting Your Manifest

### Option 1: GitHub Repository (Recommended)

1. Create a repository for your ComfyUI setup
2. Add your `manifest.json` file
3. Use the raw URL:
   ```
   https://raw.githubusercontent.com/username/repo/main/manifest.json
   ```

**Benefits:**
- Version control
- Easy sharing
- Community contributions
- Free hosting

### Option 2: GitHub Gist

1. Create a gist with your manifest
2. Use the raw URL:
   ```
   https://gist.githubusercontent.com/username/gist-id/raw/manifest.json
   ```

**Benefits:**
- Simple and quick
- Good for single-file manifests

### Option 3: Cloud Storage

Host on AWS S3, Azure Blob Storage, Google Cloud Storage, etc.

**Benefits:**
- Reliable
- Fast CDN delivery
- Full control

### Option 4: Your Own Server

Host on your own web server or domain.

**Benefits:**
- Complete control
- Custom domain

## Duplicate Detection

When loading multiple manifests, the script automatically detects duplicates:

- **Models**: Detected by URL (case-insensitive)
- **Custom Nodes**: Detected by repository URL (case-insensitive)

**Example Output:**
```
[1/2] https://example.com/manifest1.json
  ✓ Added: 10 models, 3 custom nodes

[2/2] https://example.com/manifest2.json
  ✓ Added: 5 models, 2 custom nodes
  ⚠ Skipped duplicates: 3 models, 1 custom nodes

Combined manifest summary:
  Models: 15 unique (skipped 3 duplicates)
  Custom Nodes: 5 unique (skipped 1 duplicates)
```

## Best Practices

### Creating Manifests

1. **Use descriptive names**: Make it clear what each model is
2. **Include descriptions**: Help users understand what they're downloading
3. **Group by purpose**: Create themed manifests (e.g., "SDXL-workflow", "portrait-pack")
4. **Add SHA256 hashes**: Ensure file integrity (optional but recommended)
5. **Test your manifest**: Use `--list` or `--dry-run` to verify

### Using Manifests

1. **Start with minimal**: Use a small manifest to test first
2. **Combine manifests**: Create modular manifests and combine them
3. **Use type filtering**: Download only what you need with `--types`
4. **Check before downloading**: Use `--list` to see what's included

### URL Best Practices

1. **Use direct download URLs**: Avoid HTML pages
2. **Hugging Face**: Use `/resolve/main/` URLs, not `/blob/`
   - ✅ `https://huggingface.co/user/model/resolve/main/file.safetensors`
   - ❌ `https://huggingface.co/user/model/blob/main/file.safetensors`
3. **GitHub releases**: Use direct asset URLs
   - `https://github.com/user/repo/releases/download/v1.0/file.pth`
4. **Test URLs**: Verify they download directly (not redirect to HTML)

## Troubleshooting

### Downloads Failing

- Check URL is a direct download link (not HTML page)
- Verify file is publicly accessible
- Check available disk space
- Try manual download to test URL

### Hash Verification Failed

- File may be corrupted
- URL may have changed
- Hash may be incorrect
- Script will delete and prompt re-download

### Git Clone Failed

- Check repository URL is correct
- Verify git is installed in container
- Check repository is public or credentials are provided

### Duplicates Not Detected

- URLs must match exactly (case-insensitive)
- Different URLs to the same file won't be detected as duplicates

## Script Return Codes

- `0`: All downloads/installs succeeded
- `1`: One or more downloads/installs failed

## Tips

- Use `--list` first to preview before downloading large files
- Combine a "base" manifest with specialized ones
- Share your manifests with the community
- Version your manifests (v1, v2, etc.)
- Document what each manifest contains

## Example Workflows

### Initial Setup

```bash
# 1. List what's in the manifest
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --list https://example.com/manifest.json

# 2. Download everything
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://example.com/manifest.json

# 3. Restart ComfyUI
docker compose restart
```

### Incremental Updates

```bash
# Add more models from another manifest
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://example.com/new-models.json

# Duplicates will be automatically skipped
```

### Selective Download

```bash
# Only checkpoints from multiple sources
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --types checkpoint \
  https://example.com/manifest1.json \
  https://example.com/manifest2.json
```
