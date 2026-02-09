FROM python:3.11

# Install system dependencies for Chrome + Selenium
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libgtk-3-0 \
    libxss1 \
    libasound2 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    xdg-utils \
    libpango-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libvulkan1 \
    libcurl4 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb

# Install Poetry
ENV POETRY_HOME=/opt/poetry \
    POETRY_VERSION=1.8.5 \
    POETRY_NO_INTERACTION=1 \
    POETRY_NO_ANSI=1 \
    WORKDIR=/app

RUN python3 -m venv $POETRY_HOME
RUN $POETRY_HOME/bin/pip install poetry==$POETRY_VERSION
RUN ln -s $POETRY_HOME/bin/poetry /usr/local/bin/
RUN poetry config virtualenvs.create false

# Set working directory
WORKDIR ${WORKDIR}

# Copy all your package in the working directory.
COPY ./ ${WORKDIR}/
RUN rm -rf ${WORKDIR}/poetry.toml

# Install poetry so all the packages are in the correct version.
RUN poetry install --only main --sync

# Define a command to run your app using the entrypoint
ENTRYPOINT ["poetry", "run", "book-bot", "run"]
