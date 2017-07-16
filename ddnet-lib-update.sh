wget https://www.openssl.org/source/openssl-1.1.0f.tar.gz
wget https://curl.haxx.se/download/curl-7.54.1.tar.gz

chroot debian6 bash
cd

mkdir x86-64
cd x86-64
tar xvf ../openssl-1.1.0f.tar.gz
tar xvf ../curl-7.54.1.tar.gz

cd openssl-1.1.0f
./config
make -j4
cp libssl.a libcrypto.a ..

cd ../curl-7.54.1
LDFLAGS="-L/root/x86-64/openssl-1.1.0f" LD_LIBRARY_PATH="/root/x86-64/openssl-1.1.0f" ./configure --with-ssl=/root/x86-64/openssl-1.1.0f --disable-shared --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --enable-file
CPPFLAGS="-I/root/x86-64/openssl-1.1.0f/include" LDFLAGS="-L/root/x86-64/openssl-1.1.0f" LD_LIBRARY_PATH="/root/x86-64/openssl-1.1.0f" make -j4
cp lib/.libs/libcurl.a ..

cd ../..

mkdir x86
cd x86
tar xvf ../openssl-1.1.0f.tar.gz
tar xvf ../curl-7.54.1.tar.gz

cd openssl-1.1.0f
CFLAGS=-m32 LDFLAGS=-m32 PKG_CONFIG_PATH=/usr/lib32/pkgconfig MACHINE=i686-pc-linux-gnu ./config
CFLAGS=-m32 LDFLAGS=-m32 PKG_CONFIG_PATH=/usr/lib32/pkgconfig MACHINE=i686-pc-linux-gnu make -j4
cp libssl.a libcrypto.a ..

cd ../curl-7.54.1
# Somehow need to create libz.so and librt.so manually in /lib32 and /usr/lib32...
CFLAGS=-m32 LDFLAGS="-m32 -L/root/x86/openssl-1.1.0f" LD_LIBRARY_PATH="/root/x86/openssl-1.1.0f" ./configure --host=i686-pc-linux-gnu --with-ssl=/root/x86/openssl-1.1.0f --disable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --enable-file
LD_LIBRARY_PATH="/root/x86/openssl-1.1.0f" CFLAGS=-m32 LDFLAGS="-m32 -L/root/x86/openssl-1.1.0f" make -j4
cp lib/.libs/libcurl.a ..

cd ../..

# win64
cd curl-7.54.1
./configure --host=i686-w64-mingw32 --with-winssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cp lib/.libs/libcurl-4.dll ../libcurl.dll

# win32
cd curl-7.54.1
./configure --host=x86_64-w64-mingw32 --with-winssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cp lib/.libs/libcurl-4.dll ../libcurl.dll

# osx
cd curl-7.54.1
CFLAGS="-arch i386" LDFLAGS="-arch i386" ./configure --with-darwinssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cd lib/.libs
curl -F "uploadFile=@libcurl.a" felsing.hookrace.net/tw/upload.php

cd curl-7.54.1-i686
CFLAGS="-arch x86_64" LDFLAGS="-arch x86_64" ./configure --host=i686-apple-darwin12.4.0 --with-darwinssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cd lib/.libs
curl -F "uploadFile=@libcurl.a" felsing.hookrace.net/tw/upload.php
