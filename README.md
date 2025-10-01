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
└── comfyui_data/          # All ComfyUI data (created on first run)
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

**Note:** The `comfyui_data/` directory is automatically created on first run and contains the entire ComfyUI installation with all your data.

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

**First Run:** The container will automatically create the `comfyui_data/` directory and populate it with the ComfyUI installation.

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

## Adding Models

**Important:** Models must be added to the `comfyui_data/` directory after the first run.

Place your Stable Diffusion models in the appropriate directories:

1. **Checkpoints:** `comfyui_data/models/checkpoints/`
   - SD 1.5, SDXL, SD3, Flux models (.safetensors, .ckpt)
   - Example: `comfyui_data/models/checkpoints/sd_xl_base_1.0.safetensors`

2. **VAE:** `comfyui_data/models/vae/`
   - VAE models for better quality

3. **LoRAs:** `comfyui_data/models/loras/`
   - LoRA fine-tuning models

4. **ControlNet:** `comfyui_data/models/controlnet/`
   - ControlNet models for guided generation

**Note:** You can add/remove models while the container is running. ComfyUI will detect them automatically or after a browser refresh.

## Installing Custom Nodes

1. Place custom node folders in `comfyui_data/custom_nodes/`
2. Restart the container:
   ```bash
   docker compose restart
   ```

**Alternative:** Use ComfyUI Manager (if installed) to install custom nodes directly from the web interface.

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
