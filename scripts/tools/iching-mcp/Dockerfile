FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir mcp fastmcp
COPY server.py /app/server.py
COPY ichiRan.py /app/ichiRan.py
COPY iching.json /app/iching.json
EXPOSE 3000
CMD ["python", "/app/server.py"]
