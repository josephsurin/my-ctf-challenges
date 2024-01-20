FROM ghcr.io/downunderctf/docker-vendor/nsjail:ubuntu-22.04

RUN pip install -t /lib/python3/dist-packages pycryptodome

env FLAG=oiccflag{ecb_could_also_stand_for_easy_crypto_brainteaser_:)}

COPY ./server.py /home/ctf/chal/pwn

RUN chmod +x /home/ctf/chal/pwn
