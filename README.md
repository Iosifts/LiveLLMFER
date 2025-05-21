Real-Time Facial Emotion Recognition Demo

This is a simple web demo using llama.cpp and the SmolVLM 500M model to detect facial emotions from your webcam in real time.

How to run:

Install llama.cpp.
Follow the instructions on the official GitHub page (ggerganov/llama.cpp).
Make sure you build and use llava-server.

Start the model server.
Run:
llama-server -hf ggml-org/SmolVLM-500M-Instruct-GGUF -ngl 99
The -ngl 99 option enables GPU acceleration (macOS Metal, CUDA, etc.).

Start the backend.
Run:
python app.py
This starts a server at http://localhost:5050

Open the interface.
In your browser, visit http://localhost:5050
Click Start to begin detection.
The webcam feed will start, captions will appear, and a word cloud will update in real time.

Notes:
You can edit the prompt in prompts/prompt_formatted.txt
The app filters out only emotion-related words for the word cloud
Optional background removal can be enabled in the code
Works best with SmolVLM 500M Instruct model and a good webcam
