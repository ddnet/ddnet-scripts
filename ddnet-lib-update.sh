# Using a Debian 6 chroot, mingw and a Mac VM
# DO NOT COPY libogg, extract directly... Changing timestamps breaks the build and requires autotools (or cp -a)
# strip -s all Windows dlls, don't strip a files
# TODO: https://github.com/tpoechtrager/osxcross instead of VM at some point

wget https://www.openssl.org/source/openssl-1.1.0f.tar.gz
wget https://curl.haxx.se/download/curl-7.54.1.tar.gz

chroot debian6 bash
cat /etc/apt/sources.list
deb http://archive.debian.org/debian squeeze main contrib non-free
/root/x86-64/libogg-1.3.2/missingcd

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

cd ../libogg-1.3.2
./configure CFLAGS=-fPIC
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.2.1
./configure CFLAGS=-fPIC
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.7
DEPS_LIBS="-lopus -logg -L/root/x86-64/opus-1.2.1/.libs/ -L/root/x86-64/libogg-1.3.2/src/.libs/" DEPS_CFLAGS="-I/root/x86-64/opus-1.2.1/include -I/root/x86-64/libogg-1.3.2/include"  ./configure --disable-http CFLAGS=-fPIC
make -j4
cp .libs/libopusfile.a ..

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

cd ../libogg-1.3.2
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.2.1
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.7
CFLGS=-m32 LDFLAGS=-m32 DEPS_LIBS="-lopus -logg -L/root/x86/opus-1.2.1/.libs/ -L/root/x86/libogg-1.3.2/src/.libs/" DEPS_CFLAGS="-m32 -I/root/x86/opus-1.2.1/include -I/root/x86/libogg-1.3.2/include"  ./configure --disable-http
CFLGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopusfile.a ..

cd ../..

# win64
cd curl-7.54.1
./configure --host=x86_64-w64-mingw32 --with-winssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4 V=1
rm lib/.libs/libcurl-4.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.2
./configure --host=x86_64-w64-mingw32
make -j4
rm src/.libs/libogg-0.dll
x86_64-w64-mingw32-gcc -shared  src/.libs/framing.o src/.libs/bitwise.o    -O20 -O2   -o src/.libs/libogg.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker src/.libs/libogg.dll.a
x86_64-w64-mingw32-dlltool -v -D libogg.dll -l ../ogg.lib src/.libs/*.o
cp src/.libs/libogg.dll ../libogg.dll

cd ../opus-1.2.1
./configure --host=x86_64-w64-mingw32
make -j4 V=1
rm .libs/libopus-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v -D libopus.dll -l ../opus.lib src/*.o
cp .libs/libopus.dll ../libopus.dll

cd ../opusfile-0.7
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/win64/opus-1.2.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/win64/libogg-1.3.2/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian6/root/win64/opus-1.2.1/include -I/home/deen/isos/ddnet/debian6/root/win64/libogg-1.3.2/include" ./configure --host=x86_64-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.8
./configure --host=x86_64-w64-mingw32 --prefix=/usr/x86_64-w64-mingw32 CPPFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/x86_64-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
rm objs/.libs/libfreetype-6.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

# win32
cd curl-7.54.1
./configure --host=i686-w64-mingw32 --with-winssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
rm lib/.libs/libcurl-4.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.2
./configure --host=i686-w64-mingw32
make -j4
rm src/.libs/libogg-0.dll
i686-w64-mingw32-gcc -shared  src/.libs/framing.o src/.libs/bitwise.o    -O20 -O2   -o src/.libs/libogg.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker src/.libs/libogg.dll.a
i686-w64-mingw32-dlltool -v -D libogg.dll -l ../ogg.lib src/.libs/*.o
cp src/.libs/libogg.dll ../libogg.dll

cd ../opus-1.2.1
./configure --host=i686-w64-mingw32
make -j4 V=1
rm .libs/libopus-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v -D libopus.dll -l ../opus.lib src/*.o
cp .libs/libopus.dll ../libopus.dll

cd ../opusfile-0.7
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/win32/opus-1.2.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/win32/libogg-1.3.2/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian6/root/win32/opus-1.2.1/include -I/home/deen/isos/ddnet/debian6/root/win32/libogg-1.3.2/include" ./configure --host=i686-w64-mingw32 --disable-http
make -j4 V=1
rm src/.libs/libopusfile-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.8
./configure --host=i686-w64-mingw32 --prefix=/usr/i686-w64-mingw32 CPPFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/i686-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

# osx64
cd curl-7.54.1
CFLAGS="-arch x86_64" CPPFLAGS="-arch x86_64" LDFLAGS= LIBS= ./configure --host=x86_64-apple-darwin12.4.0 --with-darwinssl --enable-static --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cd lib/.libs
curl -F "uploadFile=@libcurl.a" felsing.hookrace.net/tw/upload.php
cd ../../

cd ../ogg-1.3.2
./configure LIBS= LDFLAGS= CFLAGS="-arch x86_64" CPPFLAGS="-arch x86_64" --host=x86_64-apple-darwin12.4.0
cd src/.libs
curl -F "uploadFile=@libogg.a" felsing.hookrace.net/tw/upload.php
cd ../..

cd ../opus-1.2.1
./configure LIBS= LDFLAGS= CFLAGS="-arch x86_64" CPPFLAGS="-arch x86_64" --host=x86_64-apple-darwin12.4.0
make -j4
cd .libs
curl -F "uploadFile=@libopus.a" felsing.hookrace.net/tw/upload.php
cd ..

cd ../opusfile-0.7
DEPS_LIBS="-lopus -logg -L/var/root/opus-1.2.1/.libs/ -L/var/root/libogg-1.3.2/src/.libs/" ./configure LIBS= LDFLAGS= CFLAGS="-arch x86_64 -I/var/root/opus-1.2.1/include -I/var/root/libogg-1.3.2/include" CPPFLAGS="-arch x86_64 -I/var/root/opus-1.2.1/include -I/var/root/libogg-1.3.2/include" --host=x86_64-apple-darwin12.4.0 --disable-http
make -j4
cd .libs
curl -F "uploadFile=@libopusfile.a" felsing.hookrace.net/tw/upload.php
cd ..

# osx32
cd curl-7.54.1-i686
CFLAGS="-arch i386" LDFLAGS="-arch i386" ./configure --host=i686-apple-darwin12.4.0 --with-darwinssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cd lib/.libs
curl -F "uploadFile=@libcurl.a" felsing.hookrace.net/tw/upload.php
cd ../../

cd ../ogg-1.3.2-i686
./configure LIBS= LDFLAGS= CFLAGS="-arch i386" CPPFLAGS="-arch i386" --host=i686-apple-darwin12.4.0
cd src/.libs
curl -F "uploadFile=@libogg.a" felsing.hookrace.net/tw/upload.php
cd ../..

cd ../opus-1.2.1-i686
./configure LIBS= LDFLAGS= CFLAGS="-arch i386" CPPFLAGS="-arch i386" --host=i686-apple-darwin12.4.0
make -j4
cd .libs
curl -F "uploadFile=@libopus.a" felsing.hookrace.net/tw/upload.php
cd ..

cd ../opusfile-0.7
DEPS_LIBS="-lopus -logg -L/var/root/opus-1.2.1-i686/.libs/ -L/var/root/libogg-1.3.2-i686/src/.libs/" ./configure CFLAGS="-arch i386 -I/var/root/opus-1.2.1-i686/include -I/var/root/libogg-1.3.2-i686/include" CPPFLAGS="-arch i386 -I/var/root/opus-1.2.1-i686/include -I/var/root/libogg-1.3.2-i686/include" --host=i686-apple-darwin12.4.0 --disable-http
make -j4
cd .libs
curl -F "uploadFile=@libopusfile.a" felsing.hookrace.net/tw/upload.php
cd ..

