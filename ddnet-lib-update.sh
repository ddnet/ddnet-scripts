# Using a Debian 6 chroot, mingw and osxcross
# DO NOT COPY libogg, extract directly... Changing timestamps breaks the build and requires autotools (or cp -a)

wget http://libsdl.org/release/SDL2-2.0.12.tar.gz
wget https://curl.haxx.se/download/curl-7.69.1.tar.gz
wget http://download.savannah.gnu.org/releases/freetype/freetype-2.10.1.tar.gz
wget http://downloads.xiph.org/releases/ogg/libogg-1.3.4.tar.gz
wget https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz
wget https://downloads.xiph.org/releases/opus/opusfile-0.11.tar.gz

chroot debian6 bash
cat /etc/apt/sources.list
deb http://archive.debian.org/debian squeeze main contrib non-free
/root/x86-64/libogg-1.3.4/missingcd

mkdir x86-64
cd x86-64
tar xvf ../libogg-1.3.4.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.11.tar.gz

cd libogg-1.3.4
./configure CFLAGS=-fPIC
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS=-fPIC
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.11
DEPS_LIBS="-lopus -logg -L/root/x86-64/opus-1.3.1/.libs/ -L/root/x86-64/libogg-1.3.4/src/.libs/" DEPS_CFLAGS="-I/root/x86-64/opus-1.3.1/include -I/root/x86-64/libogg-1.3.4/include"  ./configure --disable-http CFLAGS=-fPIC
make -j4
cp .libs/libopusfile.a ..

cd ../..

mkdir x86
cd x86
tar xvf ../libogg-1.3.4.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.11.tar.gz

cd libogg-1.3.4
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.11
CFLGS=-m32 LDFLAGS=-m32 DEPS_LIBS="-lopus -logg -L/root/x86/opus-1.3.1/.libs/ -L/root/x86/libogg-1.3.4/src/.libs/" DEPS_CFLAGS="-m32 -I/root/x86/opus-1.3.1/include -I/root/x86/libogg-1.3.4/include"  ./configure --disable-http
CFLGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopusfile.a ..

cd ../..

mkdir win64
cd win64
tar xvf ../SDL2-2.0.12.tar.gz
tar xvf ../curl-7.69.1.tar.gz
tar xvf ../libogg-1.3.4.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.11.tar.gz
tar xvf ../freetype-2.10.1.tar.gz

cd SDL2-2.0.12
./configure --host=x86_64-w64-mingw32
make -j4
cp build/.libs/SDL2.dll build/.libs/libSDL2.dll.a ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D SDL2.dll -l ../SDL2.lib build/.libs/*.o

cd ../curl-7.69.1
./configure --host=x86_64-w64-mingw32 --with-winssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4 V=1
rm lib/.libs/libcurl-4.dll
cd lib
# Long command from make with fixed dll name
cd ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.4
./configure --host=x86_64-w64-mingw32
make -j4
rm src/.libs/libogg-0.dll
x86_64-w64-mingw32-gcc -shared  src/.libs/framing.o src/.libs/bitwise.o    -O20 -O2   -o src/.libs/libogg.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker src/.libs/libogg.dll.a
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libogg.dll -l ../ogg.lib src/.libs/*.o
cp src/.libs/libogg.dll ../libogg.dll

cd ../opus-1.3.1
./configure --host=x86_64-w64-mingw32 CFLAGS=-D_FORTIFY_SOURCE=0
make -j4 V=1
rm .libs/libopus-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libopus.dll -l ../opus.lib src/*.o
cp .libs/libopus.dll ../libopus.dll

cd ../opusfile-0.11
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/win64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/win64/libogg-1.3.4/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian6/root/win64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/win64/libogg-1.3.4/include" ./configure --host=x86_64-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.10.1
./configure --host=x86_64-w64-mingw32 --prefix=/usr/x86_64-w64-mingw32 CPPFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/x86_64-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
rm objs/.libs/libfreetype-6.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ..
for i in *.dll; do x86_64-w64-mingw32-strip -s $i; done

cd ../..

mkdir win32
cd win32
tar xvf ../SDL2-2.0.12.tar.gz
tar xvf ../curl-7.69.1.tar.gz
tar xvf ../libogg-1.3.4.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.11.tar.gz
tar xvf ../freetype-2.10.1.tar.gz

cd SDL2-2.0.12
./configure --host=i686-w64-mingw32
make -j4
cp build/.libs/SDL2.dll build/.libs/libSDL2.dll.a ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D SDL2.dll -l ../SDL2.lib build/.libs/*.o

cd ../curl-7.69.1
./configure --host=i686-w64-mingw32 --with-winssl --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4 V=1
rm lib/.libs/libcurl-4.dll
cd lib
# Long command from make with fixed dll name
cd ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.4
./configure --host=i686-w64-mingw32
make -j4
rm src/.libs/libogg-0.dll
i686-w64-mingw32-gcc -shared  src/.libs/framing.o src/.libs/bitwise.o    -O20 -O2   -o src/.libs/libogg.dll -Wl,--enable-auto-image-base -Xlinker --out-implib -Xlinker src/.libs/libogg.dll.a
i686-w64-mingw32-dlltool -v --export-all-symbols -D libogg.dll -l ../ogg.lib src/.libs/*.o
cp src/.libs/libogg.dll ../libogg.dll

cd ../opus-1.3.1
./configure --host=i686-w64-mingw32 CFLAGS=-D_FORTIFY_SOURCE=0
make -j4 V=1
rm .libs/libopus-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libopus.dll -l ../opus.lib src/*.o
cp .libs/libopus.dll ../libopus.dll

cd ../opusfile-0.11
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/win32/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/win32/libogg-1.3.4/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian6/root/win32/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/win32/libogg-1.3.4/include" ./configure --host=i686-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.10.1
./configure --host=i686-w64-mingw32 --prefix=/usr/i686-w64-mingw32 CPPFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/i686-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ..
for i in *.dll; do i686-w64-mingw32-strip -s $i; done

cd ../..

mkdir mac64
cd mac64
tar xvf ../curl-7.69.1.tar.gz
tar xvf ../libogg-1.3.4.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.11.tar.gz
tar xvf ../freetype-2.10.1.tar.gz

export PATH=/home/deen/git/osxcross/target/bin/:$PATH
export CC=o64-clang
export CXX=o64-clang++

cd curl-7.69.1
# Fix path to /System/Library/Frameworks/Security.framework in configure, fixed in curl in next release
CFLAGS="-mmacosx-version-min=10.9" ./configure --host=x86_64-apple-darwin15 --without-ssl --with-secure-transport --enable-static --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.4
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin15
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin15
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.11
PKG_CONFIG=/usr/sbin/pkg-config DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian6/root/mac64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian6/root/mac64/libogg-1.3.4/src/.libs/" ./configure CFLAGS="-mmacosx-version-min=10.9 -I/home/deen/isos/ddnet/debian6/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/mac64/libogg-1.3.4/include" CPPFLAGS="-I/home/deen/isos/ddnet/debian6/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian6/root/mac64/libogg-1.3.4/include" --host=x86_64-apple-darwin15 --disable-http
make -j4
cp .libs/libopusfile.a ..

cd ../freetype-2.10.1
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin15 --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4
cp objs/.libs/libfreetype.6.dylib ..
