# ComfyUI Docker Image
FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    COMFYUI_PATH=/app/ComfyUI

# Install system dependencies (git, image processing libraries)
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Clone ComfyUI from GitHub
RUN git clone https://github.com/comfyanonymous/ComfyUI.git ${COMFYUI_PATH}

WORKDIR ${COMFYUI_PATH}

# Install ComfyUI dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install JupyterLab for container management and CLI access
RUN pip install --no-cache-dir jupyterlab ipywidgets

# Expose ports: 8188 for ComfyUI, 8888 for JupyterLab
EXPOSE 8188 8888

# Create startup script to run both ComfyUI and JupyterLab
RUN echo '#!/bin/bash\n\
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token="" --NotebookApp.password="" &\n\
python main.py --listen 0.0.0.0 --port 8188\n\
' > /app/start.sh && chmod +x /app/start.sh

# Start both services
CMD ["/bin/bash", "/app/start.sh"]
