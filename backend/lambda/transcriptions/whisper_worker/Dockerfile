FROM public.ecr.aws/lambda/python:3.9

# Install Whisper + FFmpeg + dependencies
RUN yum install -y ffmpeg && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir openai-whisper boto3

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.handler"]
