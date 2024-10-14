#!/bin/sh

git clone https://github.com/pq-crystals/kyber.git
cd kyber/ref
git checkout 10b478fc3cc4ff6215eb0b6a11bd758bf0929cbd
git apply ../../my.patch
gcc -shared -O0 -fPIC -DKYBER_K=4 randombytes.c fips202.c symmetric-shake.c indcpa.c polyvec.c poly.c ntt.c cbd.c reduce.c verify.c kem.c -o libpqcrystals_kyber1024_ref.so
cp libpqcrystals_kyber1024_ref.so ../../libpqcrystals_kyber1024_ref.so
cd ../../
rm -rf kyber
