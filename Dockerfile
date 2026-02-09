FROM python:3.11

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
