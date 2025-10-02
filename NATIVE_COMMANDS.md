# Native Command Setup

The model downloader scripts are configured to feel like native Linux commands inside the container.

## 🎯 How It Works

### Scripts are in PATH
Both scripts are installed to `/usr/local/bin/` which is automatically in the system PATH.

### Executable Permissions
Scripts have the executable bit set (`chmod +x`), so they can be run directly.

### Shebang Line
Both scripts start with `#!/usr/bin/env python3`, telling the system to use Python to execute them.

### Symlinks for Convenience
Multiple symlinks provide easy-to-remember command names without the `.py` extension.

## 📝 Available Commands

Inside the container, you can use any of these commands:

| Command | Points To | Description |
|---------|-----------|-------------|
| `download-models` | `download_models_portable.py` | Default command (portable version) |
| `download-models-portable` | `download_models_portable.py` | Explicit portable version |
| `download-models-original` | `download_models.py` | Explicit original version |
| `download_models_portable.py` | (direct) | Direct script execution |
| `download_models.py` | (direct) | Direct script execution |

## 💡 Usage Examples

### From Host (using docker compose exec)

```bash
# All of these work:
docker compose exec comfyui download-models manifest.json
docker compose exec comfyui download-models-portable manifest.json
docker compose exec comfyui download-models-original manifest.json
docker compose exec comfyui download_models_portable.py manifest.json
docker compose exec comfyui download_models.py manifest.json
```

### Inside Container (from bash or JupyterLab Terminal)

```bash
# Enter container
docker compose exec comfyui bash

# Now run commands directly (no 'docker compose exec' needed)
download-models manifest.json
download-models --help
download-models --list manifest.json
download-models-original --types checkpoints manifest.json

# Works from any directory
cd /tmp
download-models /app/ComfyUI/model-manifest.json
```

## 🔍 Why This Feels Native

1. **No Python prefix needed** - Scripts execute directly
2. **No .py extension required** - Use clean command names
3. **Tab completion works** - Commands are in PATH
4. **Works from any directory** - No need to cd to script location
5. **Standard --help flag** - Built-in argparse help
6. **Exit codes work** - Proper success/failure codes for scripting

## 🛠️ Technical Details

### Dockerfile Configuration

```dockerfile
# Copy scripts to /usr/local/bin/
COPY download_models.py /usr/local/bin/download_models.py
COPY download_models_portable.py /usr/local/bin/download_models_portable.py

# Make executable
RUN chmod +x /usr/local/bin/download_models.py \
             /usr/local/bin/download_models_portable.py

# Create symlinks without .py extension
RUN ln -sf /usr/local/bin/download_models_portable.py /usr/local/bin/download-models && \
    ln -sf /usr/local/bin/download_models.py /usr/local/bin/download-models-original && \
    ln -sf /usr/local/bin/download_models_portable.py /usr/local/bin/download-models-portable
```

### Script Shebang

Both scripts start with:
```python
#!/usr/bin/env python3
```

This tells Linux to:
1. Look for `python3` in the PATH using `env`
2. Execute the script using that Python interpreter
3. Pass any arguments to the script

## 🎨 Command Comparison

### Before (Not Native-Feeling)
```bash
# Have to specify Python and full path
docker compose exec comfyui python /usr/local/bin/download_models_portable.py manifest.json

# Or cd to directory first
docker compose exec comfyui bash -c "cd /usr/local/bin && python download_models_portable.py manifest.json"
```

### After (Native-Feeling)
```bash
# Simple, clean command
docker compose exec comfyui download-models manifest.json

# Works from anywhere
docker compose exec comfyui bash -c "cd /tmp && download-models manifest.json"
```

## 📚 Integration with Shell

### Works with Pipes
```bash
docker compose exec comfyui download-models --list manifest.json | grep SDXL
```

### Works with Exit Codes
```bash
docker compose exec comfyui download-models manifest.json
if [ $? -eq 0 ]; then
    echo "Download succeeded!"
fi
```

### Works with Command Substitution
```bash
# Get list of models
MODELS=$(docker compose exec comfyui download-models --list manifest.json)
echo "$MODELS"
```

## 🚀 Benefits

1. **User Friendly** - Intuitive command names
2. **Professional** - Follows Linux conventions
3. **Discoverable** - Easy to remember and tab-complete
4. **Flexible** - Multiple ways to invoke (pick your preference)
5. **Scriptable** - Works great in automated scripts

## ✅ Verification

To verify the setup works, try these commands:

```bash
# Check if commands are in PATH
docker compose exec comfyui which download-models
docker compose exec comfyui which download-models-portable
docker compose exec comfyui which download-models-original

# Check symlinks
docker compose exec comfyui ls -la /usr/local/bin/download-*

# Test execution
docker compose exec comfyui download-models --help
docker compose exec comfyui download-models-original --help
```

## 🎯 Result

The scripts now feel like built-in Linux commands, providing a professional and user-friendly experience! 🎉
