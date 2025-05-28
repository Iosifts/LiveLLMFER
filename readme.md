This repository is a simple demo for how to use llama.cpp server with SmolVLM 500M to get real-time object detection

How to setup
Install llama.cpp
Run llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF
Note: you may need to add -ngl 99 to enable GPU (if you are using NVidia/AMD/Intel GPU)
Note (2): You can also try other models here
Open index.html
Optionally change the instruction (for example, make it returns JSON)
Click on "Start" and enjoy