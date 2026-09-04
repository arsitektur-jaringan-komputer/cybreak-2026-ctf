FROM python:3.12-alpine

WORKDIR /app
COPY main.py /app/main.py

RUN addgroup -S ctf && adduser -S -G ctf ctf && chown -R ctf:ctf /app
USER ctf

EXPOSE 31338
CMD ["python", "-u", "/app/main.py", "--host", "0.0.0.0", "--port", "31338"]
