# Using a Debian 10 chroot, mingw and osxcross (with compiler-rt built)
# DO NOT COPY libogg, extract directly... Changing timestamps breaks the build and requires autotools (or cp -a)

cd debian10/root
rm -rf *
wget http://libsdl.org/release/SDL2-2.30.5.tar.gz
wget https://curl.haxx.se/download/curl-8.8.0.tar.gz
wget https://download.savannah.gnu.org/releases/freetype/freetype-2.13.2.tar.gz
wget http://downloads.xiph.org/releases/ogg/libogg-1.3.5.tar.gz
wget https://archive.mozilla.org/pub/opus/opus-1.3.1.tar.gz
wget https://downloads.xiph.org/releases/opus/opusfile-0.12.tar.gz
wget https://sqlite.org/2024/sqlite-autoconf-3460000.tar.gz
wget https://code.videolan.org/videolan/x264/-/archive/master/x264-master.tar.bz2
wget https://ffmpeg.org/releases/ffmpeg-7.0.1.tar.gz
wget https://github.com/warmcat/libwebsockets/archive/v4.3-stable.tar.gz
wget https://download.sourceforge.net/libpng/libpng-1.6.43.tar.gz

# Causes issues, see https://github.com/ddnet/ddnet/pull/5475
#git clone --recurse-submodules https://github.com/jrfonseca/drmingw
#cd drmingw
#git checkout 0.9.5
#wget https://github.com/Jupeyy/drmingw/commit/08ab91c4897c04b5919d14fc2d7c21.diff
#wget https://github.com/Jupeyy/drmingw/commit/c04387280fa3c33e70cc083ff664ed.diff
## Disable wine stuff in ci/build.sh, set -DPOSIX_THREADS=ON
#patch -p1 < 08ab91c4897c04b5919d14fc2d7c21.diff
#patch -p1 < c04387280fa3c33e70cc083ff664ed.diff
#ci/build.sh
#for i in build/mingw64/bin/*.dll; do x86_64-w64-mingw32-strip -s $i; done
#for i in build/mingw32/bin/*.dll; do i686-w64-mingw32-strip -s $i; done

cd ../..
chroot debian10 bash
cd

mkdir x86-64
cd x86-64
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL2-2.30.5.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz

cd curl-8.8.0
./configure --with-openssl --enable-static --disable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.5
./configure CFLAGS=-fPIC
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS=-fPIC
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
DEPS_LIBS="-lopus -logg -L/root/x86-64/opus-1.3.1/.libs/ -L/root/x86-64/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/root/x86-64/opus-1.3.1/include -I/root/x86-64/libogg-1.3.5/include"  ./configure --disable-http CFLAGS=-fPIC
make -j4
cp .libs/libopusfile.a ..

cd ../SDL2-2.30.5
./configure --enable-ime CFLAGS=-fPIC --disable-video-wayland
CFLAGS=-fPIC make -j4
cp build/.libs/libSDL2-2.0.so.0.*.* ../libSDL2-2.0.so.0
strip -s ../libSDL2-2.0.so.0

cd ../sqlite-autoconf-3460000
./configure CFLAGS="-fPIC -DSQLITE_OMIT_LOAD_EXTENSION"
make -j4
cp .libs/libsqlite3.a ..

cd ../x264-master
CFLAGS="-O2 -fno-fast-math" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --enable-pic
CFLAGS="-O2 -fno-fast-math" make -j4
cp libx264.a ..

cd ../ffmpeg-7.0.1
PKG_CONFIG_PATH=/root/x86-64/x264-master/ ./configure --disable-all --disable-vdpau --disable-vaapi --disable-libdrm --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-fPIC -I/root/x86-64/x264-master" --extra-cxxflags="-fPIC -I/root/x86-64/x264-master" --extra-ldflags="-L/root/x86-64/x264-master -ldl" --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j4
cp */*.a ..

cd ../libwebsockets-4.3-stable
CXXFLAGS=-fPIC CFLAGS=-fPIC LDFLAGS=-fPIC cmake -DLWS_IPV6=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.a ..

cd ../libpng-1.6.43
./configure CFLAGS=-FPIC
make -j4
cp .libs/libpng16.a ..

cd ../..

mkdir x86
cd x86
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL2-2.30.5.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz

cd curl-8.8.0
CFLAGS=-m32 LDFLAGS=-m32 ./configure --with-openssl --enable-static --disable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.5
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
CFLAGS=-m32 LDFLAGS=-m32 ./configure
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
CFLAGS=-m32 LDFLAGS=-m32 DEPS_LIBS="-lopus -logg -L/root/x86/opus-1.3.1/.libs/ -L/root/x86/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-m32 -I/root/x86/opus-1.3.1/include -I/root/x86/libogg-1.3.5/include"  ./configure --disable-http
CFLAGS=-m32 LDFLAGS=-m32 make -j4
cp .libs/libopusfile.a ..

cd ../SDL2-2.30.5
./configure --enable-ime CFLAGS="-fPIC -m32" LDFLAGS=-m32 --disable-video-wayland
LDFLAGS=-m32 CFLAGS="-fPIC -m32" make -j4
cp build/.libs/libSDL2-2.0.so.0.*.* ../libSDL2-2.0.so.0
strip -s ../libSDL2-2.0.so.0

cd ../sqlite-autoconf-3460000
./configure CFLAGS="-fPIC -m32 -DSQLITE_OMIT_LOAD_EXTENSION"
make -j4
cp .libs/libsqlite3.a ..

cd ../x264-master
AS=nasm CFLAGS="-m32 -O2 -fno-fast-math" LDFLAGS=-m32 ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --enable-pic --host=i686-linux
CFLAGS="-m32 -O2 -fno-fast-math" LDFLAGS=-m32 make -j4
cp libx264.a ..

cd ../ffmpeg-7.0.1
PKG_CONFIG_PATH=/root/x86/x264-master ./configure --disable-all --disable-vdpau --disable-vaapi --disable-libdrm --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-m32 -fPIC -I/root/x86/x264-master" --extra-cxxflags="-m32 -fPIC -I/root/x86/x264-master" --extra-ldflags="-m32 -L/root/x86/x264-master -ldl" --cpu=i686 --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j4
cp */*.a ..

cd ../libwebsockets-4.3-stable
CXXFLAGS="-m32 -fPIC" CFLAGS="-m32 -fPIC" LDFLAGS="-m32 -fPIC" cmake -DLWS_IPV6=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.a ..

cd ../libpng-1.6.43
./configure CFLAGS="-m32 -FPIC" --host=i686-linux
make -j4
cp .libs/libpng16.a ..

cd ../..
[exit chroot]
mkdir win64
cd win64
tar xvf ../SDL2-2.30.5.tar.gz
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz

cd SDL2-2.30.5
./configure --host=x86_64-w64-mingw32 --enable-ime
make -j4
cp build/.libs/SDL2.dll build/.libs/libSDL2.dll.a ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D SDL2.dll -l ../SDL2.lib build/.libs/*.o

cd ../curl-8.8.0
./configure --host=x86_64-w64-mingw32 --with-schannel --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4 V=1
rm lib/.libs/libcurl-4.dll
cd lib
# Long command from make with fixed dll name
cd ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.5
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

cd ../opusfile-0.12
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian10/root/win64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian10/root/win64/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian10/root/win64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian10/root/win64/libogg-1.3.5/include" ./configure --host=x86_64-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.13.2
./configure --host=x86_64-w64-mingw32 --prefix=/usr/x86_64-w64-mingw32 CPPFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/x86_64-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
rm objs/.libs/libfreetype-6.dll
# Long command from make with fixed dll name
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ../sqlite-autoconf-3460000
./configure --host=x86_64-w64-mingw32 CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j4
cp .libs/libsqlite3-0.dll ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols  -D sqlite3.dll -l ../sqlite3.lib .libs/*.o

cd ../x264-master
AS=nasm CFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=x86_64-mingw32 --prefix=/usr/x86_64-w64-mingw32 --cross-prefix=x86_64-w64-mingw32-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian10/root/win64/x264-master PKG_CONFIG_LIBDIR=/usr/x86_64-w64-mingw32/lib/pkgconfig ./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-I/home/deen/isos/ddnet/debian10/root/win64/x264-master" --extra-cxxflags="-I/home/deen/isos/ddnet/debian10/root/win64/x264-master" --extra-ldflags="-L/home/deen/isos/ddnet/debian10/root/win64/x264-master" --arch=x86_64 --target_os=mingw32 --cross-prefix=x86_64-w64-mingw32- --disable-static --enable-shared --extra-libs="-lpthread -lm" --pkg-config-flags="--static"
make -j4
cp libavcodec/avcodec-61.dll libavformat/avformat-61.dll libavutil/avutil-59.dll libswresample/swresample-5.dll libswscale/swscale-8.dll libavcodec/avcodec.lib libavformat/avformat.lib libavutil/avutil.lib libswresample/swresample.lib libswscale/swscale.lib ..

cd ../libwebsockets-4.3-stable
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-w64.cmake -DLWS_IPV6=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp bin/libwebsockets.dll ..

cd ../libpng-1.6.43
CFLAGS="-I/usr/x86_64-w64-mingw32/include" LDFLAGS="-L/usr/x86_64-w64-mingw32/lib" ./configure --host=x86_64-w64-mingw32
make -j4
cp .libs/libpng16-16.dll ..
x86_64-w64-mingw32-dlltool -v --export-all-symbols -D libpng16-16.dll -l ../libpng16-16.lib **/*.o

cd ..
for i in *.dll; do x86_64-w64-mingw32-strip -s $i; done

cd ../..

mkdir win32
cd win32
tar xvf ../SDL2-2.30.5.tar.gz
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../sqlite-autoconf-3460000.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz

cd SDL2-2.30.5
./configure --host=i686-w64-mingw32 --enable-ime
make -j4
cp build/.libs/SDL2.dll build/.libs/libSDL2.dll.a ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D SDL2.dll -l ../SDL2.lib build/.libs/*.o

cd ../curl-8.8.0
./configure --host=i686-w64-mingw32 --with-schannel --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4 V=1
rm lib/.libs/libcurl-4.dll
cd lib
# Long command from make with fixed dll name
cd ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D libcurl.dll -l ../curl.lib lib/.libs/*.o
cp lib/.libs/libcurl.dll ../libcurl.dll

cd ../libogg-1.3.5
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

cd ../opusfile-0.12
DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian10/root/win32/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian10/root/win32/libogg-1.3.5/src/.libs/" DEPS_CFLAGS="-I/home/deen/isos/ddnet/debian10/root/win32/opus-1.3.1/include -I/home/deen/isos/ddnet/debian10/root/win32/libogg-1.3.5/include" ./configure --host=i686-w64-mingw32 --disable-http
make -j4 V=1
rm .libs/libopusfile-0.dll
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libopusfile.dll -l ../opusfile.lib src/*.o
cp .libs/libopusfile.dll ../libopusfile.dll

cd ../freetype-2.13.2
./configure --host=i686-w64-mingw32 --prefix=/usr/i686-w64-mingw32 CPPFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" PKG_CONFIG_LIBDIR=/usr/i686-w64-mingw32/lib/pkgconfig --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4 V=1
# Long command from make with fixed dll name
i686-w64-mingw32-dlltool -v --export-all-symbols -D libfreetype.dll -l ../freetype.lib -d objs/.libs/libfreetype-6.dll.def
cp objs/.libs/libfreetype.dll ../libfreetype.dll

cd ../sqlite-autoconf-3460000
./configure --host=i686-w64-mingw32 CFLAGS=-DSQLITE_OMIT_LOAD_EXTENSION
make -j4
cp .libs/libsqlite3-0.dll ..
i686-w64-mingw32-dlltool -v --export-all-symbols  -D sqlite3.dll -l ../sqlite3.lib .libs/*.o

cd ../x264-master
AS=nasm CFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=i686-mingw32 --prefix=/usr/i686-w64-mingw32 --cross-prefix=i686-w64-mingw32-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian10/root/win32/x264-master PKG_CONFIG_LIBDIR=/usr/i686-w64-mingw32/lib/pkgconfig ./configure --disable-all --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-I/home/deen/isos/ddnet/debian10/root/win32/x264-master" --extra-cxxflags="-I/home/deen/isos/ddnet/debian10/root/win32/x264-master" --extra-ldflags="-L/home/deen/isos/ddnet/debian10/root/win32/x264-master" --arch=i686 --target_os=mingw32 --cross-prefix=i686-w64-mingw32- --disable-static --enable-shared --pkg-config-flags="--static --with-path=/home/deen/isos/ddnet/debian10/root/win32/x264-master"
make -j4
cp libavcodec/avcodec-61.dll libavformat/avformat-61.dll libavutil/avutil-59.dll libswresample/swresample-5.dll libswscale/swscale-8.dll libavcodec/avcodec.lib libavformat/avformat.lib libavutil/avutil.lib libswresample/swresample.lib libswscale/swscale.lib ..

cd ../libwebsockets-4.3-stable
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-w32.cmake -DLWS_IPV6=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp bin/libwebsockets.dll ..

cd ../libpng-1.6.43
CFLAGS="-I/usr/i686-w64-mingw32/include" LDFLAGS="-L/usr/i686-w64-mingw32/lib" ./configure --host=i686-w64-mingw32
make -j4
cp .libs/libpng16-16.dll ..
i686-w64-mingw32-dlltool -v --export-all-symbols -D libpng16-16.dll -l ../libpng16-16.lib **/*.o

cd ..
for i in *.dll; do i686-w64-mingw32-strip -s $i; done

cd ../..

mkdir mac64
cd mac64
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL2-2.30.5.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz

export PATH=/home/deen/git/osxcross/target/bin/:$PATH
export CC=o64-clang
export CXX=o64-clang++
eval `osxcross-conf`
# If build fails, it's probably due to LLVM upgrade, rebuild osxcross:
# cd ~/git/osxcross
# rm -rf build
# ./build.sh
# ./build_compiler_rt.sh

cd curl-8.8.0
# Set cross_compiling=yes in configure
CFLAGS="-mmacosx-version-min=10.9" ./configure --host=x86_64-apple-darwin20.1 --with-secure-transport --enable-static --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.5
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin20.1
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin20.1
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
PKG_CONFIG=/usr/sbin/pkg-config DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian10/root/mac64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian10/root/mac64/libogg-1.3.5/src/.libs/" ./configure CFLAGS="-mmacosx-version-min=10.9 -I/home/deen/isos/ddnet/debian10/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian10/root/mac64/libogg-1.3.5/include" CPPFLAGS="-I/home/deen/isos/ddnet/debian10/root/mac64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian10/root/mac64/libogg-1.3.5/include" --host=x86_64-apple-darwin20.1 --disable-http
make -j4
cp .libs/libopusfile.a ..

cd ../SDL2-2.30.5
./configure --enable-ime CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin20.1
CFLAGS="-mmacosx-version-min=10.9" make -j4
cp build/.libs/libSDL2-2.0.0.dylib ../SDL2

cd ../freetype-2.13.2
./configure CFLAGS="-mmacosx-version-min=10.9" --host=x86_64-apple-darwin20.1 --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4
cp objs/.libs/libfreetype.6.dylib ..

cd ../x264-master
AS=nasm CFLAGS="-mmacosx-version-min=10.9 -I/usr/x86_64-apple-darwin20.1/include" LDFLAGS="-L/usr/x86_64-apple-darwin20.1/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=x86_64-apple-darwin20.1 --prefix=/usr/x86_64-apple-darwin20.1 --cross-prefix=x86_64-apple-darwin20.1-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian10/root/mac64/x264-master ./configure --disable-all --disable-appkit --disable-bzlib --disable-avfoundation --disable-coreimage --disable-securetransport --disable-audiotoolbox --disable-cuda-llvm --disable-videotoolbox --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-cxxflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-ldflags="-L../x264-master" --arch=x86_64 --target_os=darwin --cross-prefix=x86_64-apple-darwin20.1- --disable-static --enable-shared --cc=$CC --cxx=$CXX
make -j4
cp libavcodec/libavcodec.61.dylib libavformat/libavformat.61.dylib libavutil/libavutil.59.dylib libswresample/libswresample.5.dylib libswscale/libswscale.8.dylib ..

cd ../libwebsockets-4.3-stable
# own contrib/cross-macos-x86_64.cmake
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-macos-x86_64.cmake -DLWS_IPV6=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.19.dylib ..

cd ../libpng-1.6.43
./configure --host=x86_64-apple-darwin20.1
make -j4
cp .libs/libpng16.16.dylib ..

# Requires osxcross with SDK >= 12.0 for oa64-clang
mkdir macarm64
cd macarm64
tar xvf ../curl-8.8.0.tar.gz
tar xvf ../libogg-1.3.5.tar.gz
tar xvf ../opus-1.3.1.tar.gz
tar xvf ../opusfile-0.12.tar.gz
tar xvf ../SDL2-2.30.5.tar.gz
tar xvf ../freetype-2.13.2.tar.gz
tar xvf ../x264-master.tar.bz2
tar xvf ../ffmpeg-7.0.1.tar.gz
tar xvf ../v4.3-stable.tar.gz
tar xvf ../libpng-1.6.43.tar.gz

export PATH=/home/deen/git/osxcross/target/bin/:$PATH
export CC=oa64-clang
export CXX=oa64-clang++
eval `osxcross-conf`

cd curl-8.8.0
# Set cross_compiling=yes in configure
CFLAGS="-mmacosx-version-min=10.9" ./configure --host=aarch64-apple-darwin20.1 --with-secure-transport --enable-static --enable-shared --disable-dict --disable-gopher --disable-imap --disable-pop3 --disable-rtsp --disable-smtp --disable-telnet --disable-tftp --disable-smb --disable-ldap --enable-file
make -j4
cp lib/.libs/libcurl.a ..

cd ../libogg-1.3.5
./configure CFLAGS="-mmacosx-version-min=10.9" --host=aarch64-apple-darwin20.1
make -j4
cp src/.libs/libogg.a ..

cd ../opus-1.3.1
./configure CFLAGS="-mmacosx-version-min=10.9" --host=aarch64-apple-darwin20.1
make -j4
cp .libs/libopus.a ..

cd ../opusfile-0.12
PKG_CONFIG=/usr/sbin/pkg-config DEPS_LIBS="-lopus -logg -L/home/deen/isos/ddnet/debian10/root/macarm64/opus-1.3.1/.libs/ -L/home/deen/isos/ddnet/debian10/root/macarm64/libogg-1.3.5/src/.libs/" ./configure CFLAGS="-mmacosx-version-min=10.9 -I/home/deen/isos/ddnet/debian10/root/macarm64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian10/root/macarm64/libogg-1.3.5/include" CPPFLAGS="-I/home/deen/isos/ddnet/debian10/root/macarm64/opus-1.3.1/include -I/home/deen/isos/ddnet/debian10/root/macarm64/libogg-1.3.5/include" --host=aarch64-apple-darwin20.1 --disable-http
make -j4
cp .libs/libopusfile.a ..

cd ../SDL2-2.30.5
./configure --enable-ime CFLAGS="-mmacosx-version-min=10.9" --host=aarch64-apple-darwin20.1
CFLAGS="-mmacosx-version-min=10.9" make -j4
cp build/.libs/libSDL2-2.0.0.dylib ../SDL2

cd ../freetype-2.13.2
./configure CFLAGS="-mmacosx-version-min=10.9" --host=aarch64-apple-darwin20.1 --with-png=no --with-bzip2=no --with-zlib=no --with-harfbuzz=no
make -j4
cp objs/.libs/libfreetype.6.dylib ..

cd ../x264-master
CFLAGS="-mmacosx-version-min=10.9 -I/usr/aarch64-apple-darwin20.1/include" LDFLAGS="-L/usr/aarch64-apple-darwin20.1/lib" ./configure --enable-static --disable-cli --disable-gpl --disable-avs --disable-swscale --disable-lavf --disable-ffms --disable-gpac --disable-lsmash --disable-interlaced --host=aarch64-apple-darwin20.1 --prefix=/usr/aarch64-apple-darwin20.1 --cross-prefix=aarch64-apple-darwin20.1-
make -j4

cd ../ffmpeg-7.0.1
# Need to switch configure to use pkg-config instead of $pkg_config
PKG_CONFIG_PATH=/home/deen/isos/ddnet/debian10/root/macarm64/x264-master ./configure --disable-all --disable-appkit --disable-bzlib --disable-avfoundation --disable-coreimage --disable-securetransport --disable-audiotoolbox --disable-cuda-llvm --disable-videotoolbox --disable-alsa --disable-iconv --disable-libxcb --disable-libxcb-shape --disable-libxcb-xfixes --disable-sdl2 --disable-xlib --disable-zlib --enable-avcodec --enable-avformat --enable-encoder=libx264,aac --enable-muxer=mp4,mov --enable-protocol=file --enable-libx264 --enable-swresample --enable-swscale --enable-gpl --extra-cflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-cxxflags="-mmacosx-version-min=10.9 -I../x264-master" --extra-ldflags="-L../x264-master" --arch=aarch64 --target_os=darwin --cross-prefix=aarch64-apple-darwin20.1- --disable-static --enable-shared --cc=$CC --cxx=$CXX
make -j4
cp libavcodec/libavcodec.61.dylib libavformat/libavformat.61.dylib libavutil/libavutil.59.dylib libswresample/libswresample.5.dylib libswscale/libswscale.8.dylib ..

cd ../libwebsockets-4.3-stable
# own contrib/cross-macos-arm64.cmake
cmake -DCMAKE_TOOLCHAIN_FILE=contrib/cross-macos-arm64.cmake -DLWS_IPV6=ON -DLWS_WITH_SSL=OFF -DLWS_UNIX_SOCK=OFF -DLWS_WITHOUT_EXTENSIONS=ON -DLWS_WITH_SYS_SMD=OFF .
make -j4
cp lib/libwebsockets.19.dylib ..

cd ../libpng-1.6.43
./configure --host=aarch64-apple-darwin20.1
make -j4
cp .libs/libpng16.16.dylib ..

# fix output paths in shared libs on macOS:
otool -L $i
install_name_tool -id @rpath/SDL2.framework/Versions/A/SDL2 lib64/SDL2.framework/Versions/A/SDL2
install_name_tool -id @rpath/libpng16.16.dylib libpng16.16.dylib
install_name_tool -id @rpath/libfreetype.6.dylib libfreetype.6.dylib
install_name_tool -id @rpath/libswscale.8.dylib libswscale.8.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libswscale.8.dylib
install_name_tool -id @rpath/libswresample.5.dylib libswresample.5.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libswresample.5.dylib
install_name_tool -id @rpath/libavutil.59.dylib libavutil.59.dylib
install_name_tool -id @rpath/libavformat.61.dylib libavformat.61.dylib
install_name_tool -change /usr/local/lib/libavcodec.61.dylib @rpath/libavcodec.61.dylib libavformat.61.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libavformat.61.dylib
install_name_tool -id @rpath/libavcodec.61.dylib libavcodec.61.dylib
install_name_tool -change /usr/local/lib/libavutil.59.dylib @rpath/libavutil.59.dylib libavcodec.61.dylib
# TODO: Can this be done automatically by setting --prefix=@rpath?

# create fat binaries for mac
rm -rf libfat; mkdir libfat; for i in lib64/*.dylib; do lipo -create $i libarm64/${i:t} -output libfat/${i:t}; done
mkdir libfat; for i in lib64/*.a; do lipo -create $i libarm64/${i:t} -output libfat/${i:t}; done
cd sdl/mac; rm libfat/SDL2.framework/Versions/A/SDL2; lipo -create lib64/SDL2.framework/Versions/A/SDL2 libarm64/SDL2.framework/Versions/A/SDL2 -output libfat/SDL2.framework/Versions/A/SDL2

# sign all arm64 and fat dylibs using codesign on macOS (until https://github.com/thefloweringash/sigtool/issues/8 is fixed, then we can automate it on Linux)
for i in **/libarm64/*.dylib **/libfat/*.dylib sdl/mac/libarm64/SDL2.framework sdl/mac/libfat/SDL2.framework; do codesign -s - $i; done
