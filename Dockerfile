
FROM python:3.11-slim
WORKDIR /app

ARG REQUIREMENTS_FILE=requirements.txt 

COPY ${REQUIREMENTS_FILE} .
RUN --mount=type=secret,id=github_token [ -f '/run/secrets/github_token' ] && git config --global url."https://$(cat /run/secrets/github_token)@github.com/".insteadOf "ssh://git@github.com/" && python3 -m pip install -r ${REQUIREMENTS_FILE} --no-cache || true

RUN [ ! -f '/run/secrets/github_token' ] && mkdir -p -m 0700 ~/.ssh && cp ~/.ssh/known_hosts ~/.ssh/known_hosts.bak || touch ~/.ssh/known_hosts.bak && ssh-keyscan github.com >> ~/.ssh/known_hosts &&  --mount=type=ssh,id=default python3 -m pip install -r ${REQUIREMENTS_FILE} --no-cache && rm -f ~/.ssh/known_hosts && mv ~/.ssh/known_hosts.bak ~/.ssh/known_hosts || true

COPY pyproject.toml .
COPY temporary_python_project temporary_python_project

RUN python3 -m pip install . --no-dependencies

