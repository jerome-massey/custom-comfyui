# Custom ComfyUI Docker Setup

This is a Docker container setup for ComfyUI, the powerful and modular visual AI engine.

## Prerequisites

- Docker Desktop with WSL2 backend (Windows)
- NVIDIA GPU with CUDA support
- NVIDIA Container Toolkit installed

## Directory Structure

```
custom-comfyui/
├── Dockerfile              # Container definition
├── compose.yaml           # Docker Compose configuration
├── compose.debug.yaml     # Debug configuration
├── download_models.py     # Automated model downloader
├── model-manifest.json    # Example model manifest
└── [Docker Volumes]       # Data stored in Docker-managed volumes
    └── comfyui_data/      # All ComfyUI data (created on first run)
        ├── models/            # AI models
        │   ├── checkpoints/   # Stable Diffusion checkpoints
        │   ├── vae/          # VAE models
        │   ├── loras/        # LoRA models
        │   ├── controlnet/   # ControlNet models
        │   └── ...
        ├── input/            # Input images
        ├── output/           # Generated images
        ├── custom_nodes/     # Custom node extensions
        ├── user/             # User settings and workflows
        │   └── default/
        │       └── workflows/  # Saved workflows
        └── ...
```

**Note:** This setup uses Docker named volumes (not bind mounts) for better performance and portability. The `comfyui_data` volume is automatically created on first run and contains the entire ComfyUI installation with all your data.

## Quick Start

### Option 1: Using Docker Compose (Recommended)

1. **Build the image:**
   ```bash
   docker compose build
   ```

2. **Run the container:**
   ```bash
   docker compose up
   ```

3. **Run in detached mode:**
   ```bash
   docker compose up -d
   ```

### Option 2: Using Docker CLI

1. **Build the image:**
   ```bash
   docker build -t custom-comfyui:latest .
   ```

2. **Run the container:**
   ```bash
   docker run -d `
     --name comfyui `
     --gpus all `
     -p 8188:8188 `
     -p 8888:8888 `
     -v comfyui_data:/app/ComfyUI `
     --restart unless-stopped `
     custom-comfyui:latest
   ```

3. **View logs:**
   ```bash
   docker logs -f comfyui
   ```

4. **Stop the container:**
   ```bash
   docker stop comfyui
   ```

5. **Remove the container:**
   ```bash
   docker rm comfyui
   ```

**First Run:** The container will automatically create the `comfyui_data/` volume and populate it with the ComfyUI installation.

## Quick Reference

### Download Models Automatically

```bash
# Download from manifest (supports multiple manifests with auto-deduplication)
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://raw.githubusercontent.com/jerome-massey/custom-comfyui/main/model-manifest.json

# List what would be downloaded
docker compose exec comfyui python /usr/local/bin/download_models.py --list manifest.json

# Download only specific types
docker compose exec comfyui python /usr/local/bin/download_models.py --types checkpoint lora manifest.json
```

### Copy Files to Container

```bash
# Copy model file
docker compose cp model.safetensors comfyui:/app/ComfyUI/models/checkpoints/

# Copy directory
docker compose cp models/ comfyui:/app/ComfyUI/models/
```

### Access Container Terminal

```bash
# Via docker exec
docker compose exec comfyui bash

# Or use JupyterLab Terminal at http://localhost:8888
```

## Accessing the Environment

Once the container is running, you have two web interfaces available:

### ComfyUI Web Interface
- **URL:** http://localhost:8188
- **Purpose:** Main ComfyUI workflow interface for creating and running AI workflows

### JupyterLab Interface
- **URL:** http://localhost:8888
- **Purpose:** Container management, file browsing, terminal access, and Python notebooks
- **Features:**
  - **Terminal:** Click "+" → Terminal for full CLI access inside the container
  - **File Browser:** Navigate and edit files in the ComfyUI directory
  - **Notebooks:** Create Python notebooks for custom scripts and automation
  - **Text Editor:** Edit configuration files, workflows, and custom nodes
  - **Python Console:** Interactive Python REPL with access to all installed packages

**No password required** - JupyterLab is configured for local development access.

## Adding Models and Files to the Container

Since this setup uses Docker volumes (not bind mounts), there are several methods to add files.

### Method 1: Automated Download from Manifests (Recommended) 🚀

The container includes a powerful script that downloads models from manifest files. Manifests are JSON files that define what models and custom nodes to install.

#### Basic Usage

```bash
# Download from a single manifest (GitHub raw URL)
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://raw.githubusercontent.com/username/repo/main/model-manifest.json

# Download from multiple manifests (automatically combines and deduplicates)
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://example.com/manifest1.json \
  https://example.com/manifest2.json \
  /path/to/local-manifest.json

# Use the included example manifest
docker compose exec comfyui python /usr/local/bin/download_models.py \
  https://raw.githubusercontent.com/jerome-massey/custom-comfyui/main/model-manifest.json
```

#### Advanced Options

```bash
# List what would be downloaded without downloading (dry run)
docker compose exec comfyui python /usr/local/bin/download_models.py --list manifest.json

# See what would be downloaded
docker compose exec comfyui python /usr/local/bin/download_models.py --dry-run manifest.json

# Download only specific model types
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --types checkpoint lora vae \
  manifest.json

# Download only models (skip custom nodes)
docker compose exec comfyui python /usr/local/bin/download_models.py --models-only manifest.json

# Install only custom nodes (skip models)
docker compose exec comfyui python /usr/local/bin/download_models.py --nodes-only manifest.json
```

#### Creating Your Own Manifest

Create a JSON file with your models and custom nodes:

```json
{
  "version": "1.0",
  "description": "My custom ComfyUI setup",
  "models": [
    {
      "name": "SDXL Base 1.0",
      "type": "checkpoint",
      "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors",
      "path": "models/checkpoints",
      "filename": "sd_xl_base_1.0.safetensors",
      "sha256": "optional-hash-for-verification"
    }
  ],
  "custom_nodes": [
    {
      "name": "ComfyUI-Manager",
      "repo": "https://github.com/ltdrdata/ComfyUI-Manager.git",
      "path": "custom_nodes"
    }
  ]
}
```

**Manifest Fields:**
- `name`: Display name
- `type`: Model type (`checkpoint`, `vae`, `lora`, `controlnet`, `upscale`, `embeddings`, `clip`)
- `url`: Direct download URL (Hugging Face, GitHub releases, etc.)
- `path`: Destination folder relative to ComfyUI root
- `filename`: (Optional) Override filename
- `sha256`: (Optional) Hash for verification
- `repo`: Git repository URL for custom nodes

**Where to Host Manifests:**
- GitHub repository (use raw URL)
- GitHub Gist
- Any web server
- Local file (copy to container first)

See [model-manifest.json](model-manifest.json) for a complete example.

### Method 2: JupyterLab Upload (For Small Files)

1. Access http://localhost:8888
2. Navigate to the desired folder in the file browser
3. Click the upload button (↑) or drag & drop files

### Method 3: Docker Copy Command

```bash
# Copy single files
docker compose cp /path/to/model.safetensors comfyui:/app/ComfyUI/models/checkpoints/

# Copy entire directories
docker compose cp /path/to/models/ comfyui:/app/ComfyUI/models/
```

### Method 4: Download Directly in Container

```bash
# Using JupyterLab Terminal (http://localhost:8888)
cd /app/ComfyUI/models/checkpoints
wget https://example.com/model.safetensors

# Or using docker exec
docker compose exec comfyui wget -P /app/ComfyUI/models/checkpoints/ \
  https://example.com/model.safetensors
```

### Method 5: Git Clone Custom Nodes

```bash
# Via JupyterLab Terminal
cd /app/ComfyUI/custom_nodes
git clone https://github.com/user/custom-node.git

# Or via docker exec
docker compose exec comfyui git clone \
  https://github.com/user/custom-node.git \
  /app/ComfyUI/custom_nodes/custom-node
```

### Model Directory Structure

```
models/
├── checkpoints/     # SD 1.5, SDXL, SD3, Flux models (.safetensors, .ckpt)
├── vae/            # VAE models
├── loras/          # LoRA models
├── controlnet/     # ControlNet models
├── upscale_models/ # Upscaling models
├── embeddings/     # Textual inversion embeddings
└── clip_vision/    # CLIP vision models
```

**Note:** You can add/remove models while the container is running. ComfyUI will detect them automatically or after a browser refresh.

## Installing Custom Nodes

**Recommended Method:** Use the automated manifest download (see "Method 1" above) to install custom nodes via git repositories.

**Alternative Methods:**

1. **Via Manifest Script:**
   ```bash
   docker compose exec comfyui python /usr/local/bin/download_models.py --nodes-only manifest.json
   ```

2. **Manual Git Clone:**
   ```bash
   docker compose exec comfyui git clone https://github.com/user/custom-node.git \
     /app/ComfyUI/custom_nodes/custom-node
   ```

3. **ComfyUI Manager:** Use ComfyUI Manager (if installed) to install custom nodes directly from the web interface.

After installing custom nodes, restart the container:
```bash
docker compose restart
```

## Environment Variables

You can customize the ComfyUI startup by setting environment variables in `compose.yaml`:

```yaml
environment:
  - COMFYUI_PORT=8188
  - COMMANDLINE_ARGS=--preview-method auto
```

## Useful Commands

**View logs:**
```bash
docker compose logs -f
```

**Stop the container:**
```bash
docker compose down
```

**Rebuild after changes:**
```bash
docker compose up --build
```

**Execute commands inside container (CLI):**
```bash
docker compose exec comfyui bash
```

**Or use JupyterLab Terminal:**
- Navigate to http://localhost:8888
- Click the "+" button in the sidebar
- Select "Terminal"

**Install packages inside container:**
```bash
docker compose exec comfyui pip install package-name
```

## GPU Support

The container is configured to use NVIDIA GPUs. Make sure:
1. NVIDIA drivers are installed
2. NVIDIA Container Toolkit is installed
3. Docker Desktop has GPU support enabled

To verify GPU access:
```bash
docker compose exec comfyui nvidia-smi
```

## Troubleshooting

### Container won't start
- Check if port 8188 is already in use
- Verify NVIDIA Container Toolkit is installed
- Check Docker logs: `docker compose logs`

### Out of memory errors
- Reduce batch size in workflows
- Close other GPU-intensive applications
- Add `--lowvram` or `--novram` flags to CMD in Dockerfile

### Models not appearing
- Ensure models are in `comfyui_data/models/` subdirectories
- Refresh your browser or restart ComfyUI
- Verify the first run completed successfully and `comfyui_data/` was created
- Check file permissions on the host `comfyui_data/` directory

## Customization

### Adding Python Packages

To add additional Python packages for custom nodes:

1. **Option 1 - Install inside running container:**
   ```bash
   docker compose exec comfyui pip install package-name
   ```
   Note: This will persist in the `comfyui_data/` volume.

2. **Option 2 - Modify Dockerfile:**
   Add a RUN command before the CMD:
   ```dockerfile
   RUN pip install --no-cache-dir package-name another-package
   ```
   Then rebuild:
   ```bash
   docker compose up --build
   ```

### Data Persistence

All ComfyUI data is stored in the `comfyui_data/` directory:
- **Backup:** Simply copy the entire `comfyui_data/` folder
- **Restore:** Place the backed-up folder back and run the container
- **Migration:** Move the `comfyui_data/` folder to a new system with Docker

### Volume Management

The entire ComfyUI installation is mounted as a single volume. This means:
- All your work (models, workflows, custom nodes, outputs) persists across container rebuilds
- You can easily backup everything by backing up the `comfyui_data/` folder
- Updates to the container (rebuilds) won't affect your data

### Changing the ComfyUI Version

Edit the Dockerfile and change the git clone command to use a specific branch or commit:
```dockerfile
RUN git clone --branch v0.7.0 https://github.com/comfyanonymous/ComfyUI.git ${COMFYUI_PATH}
```

## License

This Docker setup is provided as-is. ComfyUI itself is licensed under GPL-3.0.
