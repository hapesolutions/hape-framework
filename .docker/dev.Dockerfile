FROM python:3.9-bullseye

WORKDIR /app
COPY .bashrc /root/.bashrc

ENTRYPOINT [ "python", "/app/main.py" ]

# Used for development and debugging the container
ENTRYPOINT [ "sleep", "infinity" ]
