FROM python:3.9-slim

RUN apt-get update && \
    apt-get -y install socat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m ctf
WORKDIR /home/ctf

COPY main.py /home/ctf/

RUN chown -R root:root /home/ctf && \
    chmod -R 555 /home/ctf && touch /home/ctf/answers.log && chmod 666 /home/ctf/answers.log

USER ctf
EXPOSE 1337

ENTRYPOINT ["socat", "-d", "-d", "TCP-LISTEN:1337,reuseaddr,fork,nodelay", "EXEC:'timeout 120 python3 main.py'"]