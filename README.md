# Custom ComfyUI Docker Setup

A production-ready Docker container for ComfyUI with automated model management, GPU support, and JupyterLab integration.

## 🚀 Quick Start

```bash
# Build and run
docker compose up -d

# Access ComfyUI at: http://localhost:8188
# Access JupyterLab at: http://localhost:8888

# Download models (uses portable script by default)
docker compose exec comfyui download-models model-manifest.json
```

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
- [Model Downloader](#model-downloader)
- [Web Interfaces](#web-interfaces)
- [Managing Files and Models](#managing-files-and-models)
- [Manifest Format Reference](#manifest-format-reference)
- [Model Types and Folders](#model-types-and-folders)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

## Prerequisites

- Docker Desktop with WSL2 backend (Windows) or Docker Engine (Linux)
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit installed

### Verify GPU Support

```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

## Directory Structure

```text
custom-comfyui/
├── Dockerfile                      # Container definition
├── compose.yaml                   # Docker Compose configuration
├── compose.debug.yaml             # Debug configuration with separate volumes
├── download_models_portable.py    # Portable model downloader (curl-based, recommended)
├── download_models.py             # Original model downloader (tqdm-based)
├── model-manifest.json            # Example manifest (10 popular models)
├── model-manifest-minimal.json    # Minimal starter manifest
└── [Docker Volumes]               # Data stored in Docker-managed volumes
    └── comfyui_data/              # All ComfyUI data (auto-created on first run)
        ├── models/                # AI models
        │   ├── checkpoints/       # Stable Diffusion checkpoints
        │   ├── vae/              # VAE models
        │   ├── loras/            # LoRA models
        │   ├── controlnet/       # ControlNet models
        │   └── [18 more types]   # See "Model Types" section
        ├── input/                # Input images
        ├── output/               # Generated images
        ├── custom_nodes/         # Custom node extensions
        └── user/                 # User settings and workflows
            └── default/
                └── workflows/    # Saved workflows
```

**Note:** This setup uses Docker named volumes (not bind mounts) for better performance and portability.

## Getting Started

### Build and Run

**Using Docker Compose (Recommended):**

```bash
# Build the image
docker compose build

# Run in detached mode
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

**Using Docker CLI:**

```bash
# Build
docker build -t custom-comfyui:latest .

# Run (matches all settings from compose.yaml)
docker run -d \
  --name comfyui \
  --gpus all \
  -p 8188:8188 \
  -p 8888:8888 \
  -v comfyui_data:/app/ComfyUI \
  -e NVIDIA_VISIBLE_DEVICES=all \
  -e NVIDIA_DRIVER_CAPABILITIES=compute,utility \
  --restart unless-stopped \
  custom-comfyui:latest

# View logs
docker logs -f comfyui

# Stop and remove
docker stop comfyui
docker rm comfyui
```

## Model Downloader

This container includes an automated model downloader with the following features:

- ✅ **Fast Downloads** - Uses curl for optimal speed (~150+ MB/s)
- ✅ **Smart Resume** - Automatically resumes interrupted downloads
- ✅ **Multiple Manifests** - Combine and deduplicate across sources
- ✅ **Hash Verification** - Optional SHA256 integrity checking
- ✅ **Type Filtering** - Download only specific model types
- ✅ **Progress Tracking** - Visual feedback during downloads

### Quick Reference

```bash
# Download from manifest
docker compose exec comfyui download-models manifest.json

# Common options
docker compose exec comfyui download-models --help
docker compose exec comfyui download-models --list manifest.json
docker compose exec comfyui download-models --dry-run manifest.json
docker compose exec comfyui download-models --types checkpoints loras manifest.json
```

### Available Commands

```bash
# Download from single manifest
download-models manifest.json

# Download from multiple manifests (auto-combines and deduplicates)
download-models manifest1.json manifest2.json https://example.com/manifest3.json

# Download from URL
download-models https://raw.githubusercontent.com/user/repo/main/manifest.json

# List what's in the manifest without downloading
download-models --list manifest.json

# Preview what would be downloaded (dry run)
download-models --dry-run manifest.json

# Download only specific model types
download-models --types checkpoints loras vae manifest.json

# Get help
download-models --help

# All available types
download-models --types checkpoints vae loras controlnet upscale_models \
  embeddings clip_vision diffusion_models unet manifest.json
```

### Example: Download Models

```bash
# Start the container
docker compose up -d

# Download example models (SDXL, Flux, upscalers, ControlNet)
docker compose exec comfyui download-models model-manifest.json

# Or use minimal manifest (just SDXL Base + VAE)
docker compose exec comfyui download-models model-manifest-minimal.json

# Download from GitHub-hosted manifest
docker compose exec comfyui download-models \
  https://raw.githubusercontent.com/yourusername/yourrepo/main/manifest.json

# Combine multiple manifests
docker compose exec comfyui download-models \
  model-manifest.json \
  https://example.com/extra-models.json
```



## Web Interfaces

### ComfyUI Interface

- **URL:** <http://localhost:8188>
- **Purpose:** Main workflow interface for creating and running AI workflows
- **Features:** Node-based visual programming, real-time generation, workflow saving

### JupyterLab Interface

- **URL:** <http://localhost:8888>
- **Purpose:** Container management, file browsing, terminal access
- **No password required** - configured for local development

**JupyterLab Features:**

- **Terminal:** Full bash terminal inside the container
- **File Browser:** Navigate, upload, download, and edit files
- **Python Console:** Interactive REPL with all installed packages
- **Text Editor:** Edit configs, workflows, and scripts
- **Notebooks:** Create Python notebooks for automation

## Managing Files and Models

### Method 1: Automated Download (Recommended) 🚀

Use the built-in model downloader scripts with manifest files:

```bash
# Download from manifest
docker compose exec comfyui download-models your-manifest.json

# Download from multiple manifests (combines automatically)
docker compose exec comfyui download-models \
  https://example.com/base-models.json \
  https://example.com/loras.json \
  /path/to/local-manifest.json
```

See [Manifest Format Reference](#manifest-format-reference) for creating your own manifests.

### Method 2: JupyterLab Upload

1. Open <http://localhost:8888>
2. Navigate to desired folder (e.g., `models/checkpoints`)
3. Click upload button (↑) or drag and drop files

### Method 3: Docker Copy

```bash
# Copy single file
docker compose cp model.safetensors comfyui:/app/ComfyUI/models/checkpoints/

# Copy entire directory
docker compose cp models/ comfyui:/app/ComfyUI/models/
```

### Method 4: Download Inside Container

```bash
# Using wget
docker compose exec comfyui wget -P /app/ComfyUI/models/checkpoints/ \
  https://example.com/model.safetensors

# Or from JupyterLab Terminal (http://localhost:8888)
cd /app/ComfyUI/models/checkpoints
wget https://example.com/model.safetensors
```

### Method 5: Git Clone Custom Nodes

```bash
# Via docker exec
docker compose exec comfyui git clone \
  https://github.com/user/custom-node.git \
  /app/ComfyUI/custom_nodes/custom-node

# Or from JupyterLab Terminal
cd /app/ComfyUI/custom_nodes
git clone https://github.com/user/custom-node.git
```

After installing custom nodes, restart:

```bash
docker compose restart
```

## Manifest Format Reference

Create JSON manifest files to define models for automated downloading.

### Complete Manifest Example

```json
{
  "version": "1.0",
  "description": "My custom ComfyUI setup",
  "models": [
    {
      "name": "SDXL Base 1.0",
      "type": "checkpoints",
      "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
      "path": "models/checkpoints",
      "filename": "sd_xl_base_1.0.safetensors",
      "sha256": "31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b",
      "description": "Stable Diffusion XL base model"
    },
    {
      "name": "SDXL VAE",
      "type": "vae",
      "url": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors",
      "path": "models/vae",
      "sha256": "235745af8d86bf4a4c1b5b4f529868b37019a10f7c0b2e79ad0bc8a3d25f0eef"
    }
  ]
}
```

### Manifest Fields

**Required Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Display name for the model | `"SDXL Base 1.0"` |
| `type` | Model type (see table below) | `"checkpoints"` |
| `url` | Direct download URL | `"https://..."` |
| `path` | Destination folder relative to ComfyUI | `"models/checkpoints"` |

**Optional Fields:**

| Field | Description | Example |
|-------|-------------|---------|
| `filename` | Override filename (defaults to URL filename) | `"my_model.safetensors"` |
| `sha256` | SHA256 hash for verification | `"31e35c80fc..."` |
| `description` | Human-readable description | `"Base SDXL model"` |

### Hosting Manifests

You can load manifests from:

- **GitHub Repository:** `https://raw.githubusercontent.com/user/repo/main/manifest.json`
- **GitHub Gist:** `https://gist.githubusercontent.com/user/gist-id/raw/manifest.json`
- **Web Server:** Any publicly accessible URL
- **Local File:** `/path/to/manifest.json` or `./manifest.json`

### Multiple Manifest Support

Combine multiple manifests in a single command - duplicates are automatically detected and skipped:

```bash
docker compose exec comfyui download-models \
  https://example.com/base-models.json \
  https://example.com/loras.json \
  https://example.com/controlnets.json
```

**Duplicate Detection:**

- Models are identified by their URL (case-insensitive)
- First occurrence wins, subsequent duplicates are skipped
- Console shows which manifest a duplicate was already loaded from

## Model Types and Folders

The downloader supports all 20 ComfyUI model folder types:

| Type | Path | Description | Common Formats |
|------|------|-------------|----------------|
| `checkpoints` | `models/checkpoints` | Main SD models (SD 1.5, SDXL, SD3, Flux) | .safetensors, .ckpt |
| `vae` | `models/vae` | VAE models for improved quality | .safetensors, .pt |
| `loras` | `models/loras` | LoRA fine-tuning models | .safetensors |
| `controlnet` | `models/controlnet` | ControlNet guidance models | .safetensors |
| `upscale_models` | `models/upscale_models` | Image upscaling models | .pth, .pt |
| `embeddings` | `models/embeddings` | Textual inversion embeddings | .pt, .safetensors |
| `clip_vision` | `models/clip_vision` | CLIP vision models | .safetensors |
| `clip` | `models/clip` | CLIP text encoders | .safetensors |
| `diffusion_models` | `models/diffusion_models` | Diffusion model components | .safetensors |
| `unet` | `models/unet` | U-Net model components | .safetensors |
| `text_encoders` | `models/text_encoders` | Text encoder models | .safetensors |
| `configs` | `models/configs` | Model configuration files | .yaml, .json |
| `hypernetworks` | `models/hypernetworks` | Hypernetwork models | .pt |
| `style_models` | `models/style_models` | Style transfer models | .safetensors |
| `gligen` | `models/gligen` | GLIGEN grounded generation | .safetensors |
| `photomaker` | `models/photomaker` | PhotoMaker models | .safetensors |
| `model_patches` | `models/model_patches` | Model patches and modifications | .safetensors |
| `diffusers` | `models/diffusers` | Hugging Face Diffusers format | directory |
| `vae_approx` | `models/vae_approx` | Fast approximate VAE decoders | .pth |
| `audio_encoders` | `models/audio_encoders` | Audio encoding models | .safetensors |

### Type Filtering

Download only specific types:

```bash
# Just checkpoints and VAEs
docker compose exec comfyui download-models --types checkpoints vae manifest.json

# LoRAs and ControlNets only
docker compose exec comfyui download-models --types loras controlnet manifest.json
```

## Configuration

### Environment Variables

Customize ComfyUI startup in `compose.yaml`:

```yaml
environment:
  - COMFYUI_PORT=8188
  - COMFYUI_PATH=/app/ComfyUI
  - COMMANDLINE_ARGS=--preview-method auto
```

### Adding Python Packages

**Option 1 - Runtime Installation (temporary):**

```bash
docker compose exec comfyui pip install package-name
```

**Option 2 - Dockerfile (permanent):**

Add to Dockerfile before CMD:

```dockerfile
RUN pip install --no-cache-dir package-name another-package
```

Then rebuild:

```bash
docker compose up --build
```

### Changing ComfyUI Version

Edit Dockerfile and specify a branch or tag:

```dockerfile
RUN git clone --branch v0.7.0 https://github.com/comfyanonymous/ComfyUI.git ${COMFYUI_PATH}
```

### Volume Management

**Backup Everything:**

```bash
# List volumes
docker volume ls

# Create backup
docker run --rm -v comfyui_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/comfyui_backup.tar.gz /data
```

**Restore from Backup:**

```bash
# Create new volume and restore
docker volume create comfyui_data
docker run --rm -v comfyui_data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/comfyui_backup.tar.gz -C /data --strip-components=1
```

**Inspect Volume:**

```bash
docker run --rm -v comfyui_data:/data ubuntu ls -lah /data
```

## Troubleshooting

### Container Won't Start

**Check port conflicts:**

```bash
# Check if port 8188 is in use
netstat -ano | findstr :8188  # Windows
lsof -i :8188                 # Linux/Mac

# Use different port in compose.yaml:
ports:
  - "8189:8188"
```

**Verify GPU access:**

```bash
# Check NVIDIA drivers
nvidia-smi

# Test GPU in container
docker compose exec comfyui nvidia-smi
```

**View detailed logs:**

```bash
docker compose logs -f
```

### Out of Memory Errors

**Reduce VRAM usage:**

Edit Dockerfile CMD line:

```dockerfile
# Low VRAM mode
CMD ["python", "main.py", "--listen", "0.0.0.0", "--lowvram"]

# Very low VRAM mode (CPU fallback)
CMD ["python", "main.py", "--listen", "0.0.0.0", "--novram"]
```

**Close other GPU applications:**

```bash
# Check GPU usage
nvidia-smi

# Kill specific process
kill -9 <PID>
```

### Models Not Appearing

**Check model placement:**

```bash
# List models directory
docker compose exec comfyui ls -lah /app/ComfyUI/models/checkpoints/

# Check file permissions
docker compose exec comfyui ls -l /app/ComfyUI/models/
```

**Refresh ComfyUI:**

1. Refresh browser (Ctrl+F5)
2. Or restart container: `docker compose restart`

### Downloads Failing

**Check network connectivity:**

```bash
# Test from inside container
docker compose exec comfyui curl -I https://huggingface.co

# Test with verbose output
docker compose exec comfyui download-models --dry-run manifest.json
```

**Verify curl is available:**

```bash
docker compose exec comfyui which curl
docker compose exec comfyui curl --version
```

### JupyterLab Not Accessible

**Check if port is open:**

```bash
# Test connection
curl http://localhost:8888

# Check container logs
docker compose logs comfyui | grep jupyter
```

**Restart JupyterLab:**

```bash
docker compose exec comfyui pkill jupyter
docker compose restart
```

## Useful Commands

```bash
# Container management
docker compose up -d              # Start in background
docker compose down               # Stop and remove
docker compose restart            # Restart
docker compose logs -f            # Follow logs
docker compose ps                 # List containers

# Execute commands
docker compose exec comfyui bash  # Open bash shell
docker compose exec comfyui nvidia-smi  # Check GPU

# File operations
docker compose cp file.txt comfyui:/app/  # Copy to container
docker compose cp comfyui:/app/file.txt . # Copy from container

# Rebuild after changes
docker compose up --build

# Clean up
docker compose down -v            # Remove volumes too
docker system prune -a            # Clean all unused Docker data
```

## Example Workflows

### First-Time Setup

```bash
# 1. Build and start
docker compose up -d

# 2. Download essential models
docker compose exec comfyui download-models model-manifest-minimal.json

# 3. Access ComfyUI
# Open http://localhost:8188 in browser

# 4. Load a workflow and start creating!
```

### Adding Custom Models

```bash
# Create your manifest file (my-models.json)
cat > my-models.json << 'EOF'
{
  "version": "1.0",
  "models": [
    {
      "name": "My Custom Model",
      "type": "checkpoints",
      "url": "https://example.com/model.safetensors",
      "path": "models/checkpoints"
    }
  ]
}
EOF

# Download
docker compose exec comfyui download-models my-models.json
```

### Backup and Migrate

```bash
# Backup on old system
docker run --rm -v comfyui_data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/comfyui_backup.tar.gz /data

# Copy comfyui_backup.tar.gz to new system

# Restore on new system
docker volume create comfyui_data
docker run --rm -v comfyui_data:/data -v $(pwd):/backup \
  ubuntu tar xzf /backup/comfyui_backup.tar.gz -C /data --strip-components=1

docker compose up -d
```

## Performance Tips

1. **Use type filtering** - Only download what you need: `--types checkpoints vae`
2. **Combine manifests** - Download from multiple sources in one command
3. **Use hash verification** - Add `sha256` fields to manifests for integrity checking
4. **Monitor GPU usage** - Run `nvidia-smi` to ensure GPU is being utilized
5. **Use --lowvram flag** - If running out of memory

## Additional Resources

- **ComfyUI GitHub:** <https://github.com/comfyanonymous/ComfyUI>
- **ComfyUI Examples:** <https://comfyanonymous.github.io/ComfyUI_examples/>
- **NVIDIA Container Toolkit:** <https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/>
- **Docker Compose Docs:** <https://docs.docker.com/compose/>

## License

This Docker setup is provided as-is under MIT License. ComfyUI itself is licensed under GPL-3.0.

---

**Made with ❤️ for the ComfyUI community**
