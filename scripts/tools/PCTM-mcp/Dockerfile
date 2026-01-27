FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir mcp fastmcp numpy
COPY server.py /app/server.py
COPY PCTM.py /app/PCTM.py
COPY ichiRan.py /app/ichiRan.py
COPY UCCanon.json /app/UCCanon.json
COPY MDCanon.json /app/MDCanon.json
COPY Orders_Mathematical_Substrate.json /app/Orders_Mathematical_Substrate.json
EXPOSE 3000
CMD ["python", "/app/server.py"]
