FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY sejmwatch ./sejmwatch
RUN pip install --no-cache-dir .
RUN mkdir -p /app/data
ENV SEJMWATCH_DB=/app/data/sejmwatch.db SEJMWATCH_AUTO_SYNC=1
EXPOSE 8000
CMD ["uvicorn", "sejmwatch.app:app", "--host", "0.0.0.0", "--port", "8000"]
