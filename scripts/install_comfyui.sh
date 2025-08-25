#!/bin/bash

# Install ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI /content/ComfyUI
cd /content/ComfyUI
pip install -r requirements.txt

# Install Mochi custom node (example - adjust as needed)
git clone https://github.com/mochi-node-repo /content/ComfyUI/custom_nodes/mochi-node
# Install any additional dependencies for Mochi