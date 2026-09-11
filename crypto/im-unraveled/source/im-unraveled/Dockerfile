FROM python:3.12-slim

RUN pip install --no-cache-dir pycryptodome setproctitle

RUN useradd -m ctf
WORKDIR /home/ctf

COPY chall.py .
COPY utils/ utils/

RUN mkdir -p /home/ctf/logs && \
    chown -R root:root /home/ctf && \
    chmod -R 755 /home/ctf && \
    chown ctf:ctf /home/ctf/logs

USER ctf
EXPOSE 13337

CMD ["python3", "-u", "chall.py"]
