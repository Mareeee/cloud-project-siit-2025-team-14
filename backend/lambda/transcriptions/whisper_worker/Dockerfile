FROM public.ecr.aws/lambda/python:3.9

RUN yum install -y tar xz curl && \
    yum clean all

RUN curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o /tmp/ffmpeg.tar.xz && \
    tar -xf /tmp/ffmpeg.tar.xz -C /tmp/ && \
    mv /tmp/ffmpeg-*/ffmpeg /usr/bin/ffmpeg && \
    rm -rf /tmp/ffmpeg* && \
    chmod +x /usr/bin/ffmpeg

RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir boto3

RUN pip install --no-cache-dir tiktoken==0.7.0

RUN pip install --no-cache-dir openai-whisper

COPY app.py ${LAMBDA_TASK_ROOT}

CMD ["app.handler"]