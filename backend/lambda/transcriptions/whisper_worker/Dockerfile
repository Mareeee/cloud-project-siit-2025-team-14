FROM public.ecr.aws/lambda/python:3.9

# 1. Instalirajte EPEL repozitorijum i ažurirajte
# 2. Instalirajte ffmpeg (dostupan preko EPEL-a)
# Koristimo 'dnf' jer je moderniji ekvivalent 'yum' na AL2 i bolje rešava zavisnosti
RUN yum install -y amazon-linux-extras && \
    amazon-linux-extras install epel -y && \
    yum clean metadata && \
    yum install -y ffmpeg && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir openai-whisper boto3

# Copy function code
COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.handler"]