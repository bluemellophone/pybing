#################################
echo 'Removing old build'
rm -rf build
rm -rf CMakeFiles
rm -rf CMakeCache.txt
rm -rf cmake_install.cmake
#################################
echo 'Creating new build'
mkdir build
cd build
#################################
echo 'Configuring with cmake'
if [[ '$OSTYPE' == 'darwin'* ]]; then
    export CONFIG="-DCMAKE_OSX_ARCHITECTURES=x86_64 -DCMAKE_C_COMPILER=clang2 -DCMAKE_CXX_COMPILER=clang2++"
else
    export CONFIG="-DCMAKE_BUILD_TYPE='Release'"
fi
cmake $CONFIG -G 'Unix Makefiles' ..
#################################
echo 'Building with make'
if [[ "$OSTYPE" == "msys"* ]]; then
    make || { echo "FAILED MAKE" ; exit 1; }
else
    export NCPUS=$(grep -c ^processor /proc/cpuinfo)
    export NCPUS=1
    make -j$NCPUS || { echo "FAILED MAKE" ; exit 1; }
fi
#################################
echo 'Moving the shared library'
cp -v lib* ../pybing
# cp -v bing ../
cd ..
