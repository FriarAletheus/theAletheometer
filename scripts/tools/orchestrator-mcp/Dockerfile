FROM python:3.12-slim

# Ontological substrate
WORKDIR /app
RUN pip install --no-cache-dir \
    mcp \
    fastmcp \
    numpy

# Transcendental copies
COPY server.py orchestrator.py /app/
RUN mkdir -p /app/workspace && \
    chmod +x server.py

# Phenomenal exposure
EXPOSE 3000

# Eternal recurrence
CMD ["python", "server.py"]
