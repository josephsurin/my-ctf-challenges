FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-22.04

ENV JAIL_CWD=/chal

COPY ./flag.txt /home/ctf/chal/flag.txt
COPY ./greeter /home/ctf/chal/pwn

RUN chmod +x /home/ctf/chal/pwn