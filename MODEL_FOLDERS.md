# ComfyUI Model Folders Reference

This document describes all the model folders available in ComfyUI and what types of files go in each.

## Model Directory Structure

```
models/
├── audio_encoders/      # Audio encoding models
├── checkpoints/         # Main model checkpoints (SD 1.5, SDXL, Flux, etc.)
├── clip/               # CLIP text encoder models
├── clip_vision/        # CLIP vision models for image understanding
├── configs/            # Model configuration files
├── controlnet/         # ControlNet guidance models
├── diffusers/          # Diffusers format models
├── diffusion_models/   # Diffusion model components
├── embeddings/         # Textual inversion embeddings
├── gligen/             # GLIGEN models for grounded generation
├── hypernetworks/      # Hypernetwork models
├── loras/              # LoRA (Low-Rank Adaptation) models
├── model_patches/      # Model patches and modifications
├── photomaker/         # PhotoMaker models for face customization
├── style_models/       # Style transfer models
├── text_encoders/      # Text encoder models
├── unet/               # UNet model components
├── upscale_models/     # Upscaling models (ESRGAN, etc.)
├── vae/                # VAE (Variational Autoencoder) models
└── vae_approx/         # Approximate VAE models for faster previews
```

## Folder Descriptions

### checkpoints/
**Purpose:** Main Stable Diffusion model files  
**Common Files:**
- SD 1.5 models (.safetensors, .ckpt)
- SDXL models (.safetensors)
- SD3 models (.safetensors)
- Flux models (.safetensors)
- Merged/custom trained models

**Example:**
```json
{
  "name": "SDXL Base 1.0",
  "type": "checkpoints",
  "path": "models/checkpoints",
  "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
}
```

### vae/
**Purpose:** VAE models for improved image quality  
**Common Files:**
- SDXL VAE (.safetensors)
- SD 1.5 VAE (.safetensors, .pt)
- Custom VAE models

**Example:**
```json
{
  "name": "SDXL VAE",
  "type": "vae",
  "path": "models/vae",
  "url": "https://huggingface.co/stabilityai/sdxl-vae/resolve/main/sdxl_vae.safetensors"
}
```

### loras/
**Purpose:** LoRA fine-tuning models  
**Common Files:**
- Character LoRAs
- Style LoRAs
- Concept LoRAs
- Training output LoRAs

**Example:**
```json
{
  "name": "Detail Tweaker LoRA",
  "type": "loras",
  "path": "models/loras",
  "url": "https://civitai.com/api/download/models/xxxxx"
}
```

### controlnet/
**Purpose:** ControlNet models for guided generation  
**Common Files:**
- Canny edge detection
- Depth maps
- OpenPose
- Segmentation
- Line art
- Normal maps

**Example:**
```json
{
  "name": "ControlNet Canny",
  "type": "controlnet",
  "path": "models/controlnet",
  "url": "https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth"
}
```

### upscale_models/
**Purpose:** Image upscaling models  
**Common Files:**
- RealESRGAN models (.pth)
- UltraSharp models (.pth)
- 4x upscalers
- 2x upscalers

**Example:**
```json
{
  "name": "RealESRGAN x4plus",
  "type": "upscale_models",
  "path": "models/upscale_models",
  "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth"
}
```

### embeddings/
**Purpose:** Textual inversion embeddings  
**Common Files:**
- Negative embeddings (EasyNegative, BadPrompt)
- Style embeddings
- Concept embeddings

**Example:**
```json
{
  "name": "EasyNegative",
  "type": "embeddings",
  "path": "models/embeddings",
  "url": "https://huggingface.co/embed/EasyNegative/resolve/main/EasyNegative.safetensors"
}
```

### clip/
**Purpose:** CLIP text encoder models  
**Common Files:**
- clip_l (CLIP-L)
- clip_g (CLIP-G)
- T5 text encoders

**Example:**
```json
{
  "name": "CLIP-L",
  "type": "clip",
  "path": "models/clip",
  "url": "https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/pytorch_model.bin"
}
```

### clip_vision/
**Purpose:** CLIP vision models for image understanding  
**Common Files:**
- CLIP vision encoders for IP-Adapter
- Vision transformers

**Example:**
```json
{
  "name": "CLIP Vision",
  "type": "clip_vision",
  "path": "models/clip_vision",
  "url": "https://huggingface.co/openai/clip-vit-large-patch14/resolve/main/pytorch_model.bin"
}
```

### unet/
**Purpose:** UNet components for diffusion models  
**Common Files:**
- Separate UNet models
- Flux UNet components

**Example:**
```json
{
  "name": "Flux UNet",
  "type": "unet",
  "path": "models/unet",
  "url": "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/unet.safetensors"
}
```

### diffusers/
**Purpose:** Models in Hugging Face Diffusers format  
**Common Files:**
- Full diffusers model folders
- Converted models

### style_models/
**Purpose:** Style transfer and style conditioning models  
**Common Files:**
- T2I-Adapter style models
- Style conditioning models

**Example:**
```json
{
  "name": "T2I-Adapter Style",
  "type": "style_models",
  "path": "models/style_models",
  "url": "https://huggingface.co/TencentARC/T2I-Adapter/resolve/main/models/t2iadapter_style_sd14v1.pth"
}
```

### hypernetworks/
**Purpose:** Hypernetwork models  
**Common Files:**
- Hypernetwork .pt files
- Training outputs

### photomaker/
**Purpose:** PhotoMaker models for face customization  
**Common Files:**
- PhotoMaker encoders
- Face customization models

### gligen/
**Purpose:** GLIGEN models for grounded text-to-image generation  
**Common Files:**
- GLIGEN checkpoints
- Grounding models

### text_encoders/
**Purpose:** Text encoding models  
**Common Files:**
- T5 encoders
- BERT encoders
- Custom text encoders

### audio_encoders/
**Purpose:** Audio encoding models  
**Common Files:**
- Audio processing models
- Speech encoders

### diffusion_models/
**Purpose:** Diffusion model components  
**Common Files:**
- Separate diffusion components
- Model parts

### model_patches/
**Purpose:** Patches and modifications for models  
**Common Files:**
- Model patches
- Custom modifications

### configs/
**Purpose:** Model configuration files  
**Common Files:**
- .yaml configuration files
- Model definitions

### vae_approx/
**Purpose:** Approximate VAE for fast preview generation  
**Common Files:**
- Fast VAE decoders
- Preview models

## Manifest File Format

When creating a manifest, use the folder name as the `type`:

```json
{
  "version": "1.0",
  "description": "My ComfyUI Models",
  "models": [
    {
      "name": "Display Name",
      "type": "checkpoints",        // Folder name (audio_encoders, checkpoints, clip, etc.)
      "path": "models/checkpoints",  // Full path relative to ComfyUI root
      "url": "https://example.com/model.safetensors",
      "filename": "optional_custom_name.safetensors",  // Optional: override filename
      "sha256": "optional_hash_for_verification",      // Optional: for integrity check
      "description": "Optional description"
    }
  ]
}
```

## Type Filter Usage

Use the `--types` flag to download only specific model types:

```bash
# Download only checkpoints and LoRAs
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --types checkpoints loras manifest.json

# Download all upscaling and VAE models
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --types upscale_models vae vae_approx manifest.json

# Download ControlNet and CLIP models
docker compose exec comfyui python /usr/local/bin/download_models.py \
  --types controlnet clip clip_vision manifest.json
```

## Available Type Values

Use these exact values for the `--types` argument:

- `audio_encoders`
- `checkpoints`
- `clip`
- `clip_vision`
- `configs`
- `controlnet`
- `diffusers`
- `diffusion_models`
- `embeddings`
- `gligen`
- `hypernetworks`
- `loras`
- `model_patches`
- `photomaker`
- `style_models`
- `text_encoders`
- `unet`
- `upscale_models`
- `vae`
- `vae_approx`

## Tips

1. **Use the correct type name** that matches the folder name
2. **Path should always start with `models/`** followed by the folder name
3. **Filename is optional** - if not specified, uses the URL's filename
4. **Group related models** in the same manifest for easier management
5. **Test with `--list`** before downloading to verify manifest structure
