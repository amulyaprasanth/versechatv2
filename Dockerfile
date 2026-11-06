# Use the official PostgreSQL 18 image
FROM postgres:18

# Install build dependencies and PostgreSQL development files
RUN apt-get update && apt-get install -y \
  build-essential \
  git \
  postgresql-server-dev-18 \
  && rm -rf /var/lib/apt/lists/*

# Clone pgvector at a specific version tag (e.g., v0.8.7)
RUN git clone --branch v0.8.7 https://github.com/pgvector/pgvector.git \
  && cd pgvector \
  && make \
  && make install

# Clean up unnecessary build tools to reduce image size
RUN apt-get remove -y build-essential git postgresql-server-dev-18 \
  && apt-get autoremove -y   
