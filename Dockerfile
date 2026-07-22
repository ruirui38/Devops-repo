FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN sed -i 's/\r//' entrypoint.sh && chmod +x entrypoint.sh

# 非rootユーザーを作成し、/appの所有権を付与
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser \
  && chown -R appuser:appuser /app

USER appuser

CMD ["/bin/bash", "entrypoint.sh"]