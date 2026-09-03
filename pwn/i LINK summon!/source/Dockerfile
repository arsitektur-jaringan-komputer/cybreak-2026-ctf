FROM debian:trixie AS builder

RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build
COPY chall.c /build/chall.c

RUN gcc -no-pie -fno-stack-protector -fcf-protection -O0 -g -o chall chall.c

FROM debian:trixie

RUN apt-get update && apt-get install -y \
    socat \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m ctf
WORKDIR /home/ctf

COPY --from=builder /build/chall /home/ctf/chall
COPY flag.txt /home/ctf/flag.txt

RUN chmod +x /home/ctf/chall && \
    chown -R root:root /home/ctf && \
    chmod 755 /home/ctf && \          
    chmod 755 /home/ctf/chall && \
    chown ctf:ctf /home/ctf/flag.txt && \
    chmod 400 /home/ctf/flag.txt

USER ctf
EXPOSE 4282

CMD ["socat", "TCP-LISTEN:4282,reuseaddr,fork", "EXEC:/home/ctf/chall,stderr"]
