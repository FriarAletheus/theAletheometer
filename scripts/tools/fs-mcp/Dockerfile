FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir mcp fastmcp
COPY server.py /app/server.py
EXPOSE 3000
CMD ["python", "/app/server.py"]
