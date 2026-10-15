%undefine _debugsource_packages

Name:		python-torchvision
Version:	0.28.0
Release:	2
Summary:	Datasets, transforms and models for computer vision (PyTorch)
License:	BSD-3-Clause
Group:		Development/Python
URL:		https://github.com/pytorch/vision
Source0:	https://github.com/pytorch/vision/archive/refs/tags/v%{version}.tar.gz#/vision-%{version}.tar.gz

BuildSystem:	python
BuildRequires:	python
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	pkgconfig(libwebp)

BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(wheel)
BuildRequires:	python%{pyver}dist(torch)
# setup.py compiles the HIP ops with hipcc. Device bitcode comes
# from rocm-device-libs. Arch list is the same one python-torch used.
# Torch's complex.h includes thrust/complex.h. That header is
# rocthrust, and it is not pulled in by hipcc.
BuildRequires:	hipcc
BuildRequires:	/usr/bin/clang-offload-bundler
BuildRequires:	rocm-device-libs
BuildRequires:	cmake(rocthrust)
# Same imported HIP targets as torchcodec. torchvision's CMake finds
# Torch before those packages exist.
BuildRequires:	cmake(hip)
BuildRequires:	cmake(hiprtc)
BuildRequires:	cmake(rocblas)
BuildRequires:	cmake(hipblas)
BuildRequires:	cmake(hipfft)
BuildRequires:	cmake(hiprand)
BuildRequires:	cmake(hipsparse)
BuildRequires:	cmake(rocsolver)
BuildRequires:	cmake(hipsolver)
BuildRequires:	cmake(hipblaslt)
BuildRequires:	cmake(miopen)
BuildRequires:	python%{pyver}dist(numpy)
BuildRequires:	python%{pyver}dist(pillow)
Requires:	python%{pyver}dist(torch)
Requires:	python%{pyver}dist(numpy)
Requires:	python%{pyver}dist(pillow)

# Do not emit an exact torch== pin if setup.py ever grows one.
%global __requires_exclude ^python[0-9.]+dist\\(torch\\)

%description
The torchvision package consists of popular datasets, model
architectures, and common image transformations for computer vision.
Matches python-torch 2.13. Image codecs are system libpng / libjpeg /
libwebp. Native ffmpeg video I/O was removed upstream in 0.22+ in
favour of TorchCodec; there is nothing here to link against libav.

%prep -a
# setup.py writes torchvision/version.py from version.txt + BUILD_VERSION.
# c10_hip / torch_hip reference hip::host and the roc* targets. Finding
# Torch first fails configure on the ROCm build.
python - <<'PY'
from pathlib import Path
p = Path("CMakeLists.txt")
text = p.read_text()
old = "find_package(Torch REQUIRED)\n"
new = """# OM python-torch is the ROCm build. Import its HIP dependencies first.
find_package(hip CONFIG REQUIRED)
find_package(hiprtc CONFIG REQUIRED)
find_package(rocblas CONFIG REQUIRED)
find_package(hipblas CONFIG REQUIRED)
find_package(hipfft CONFIG REQUIRED)
find_package(hiprand CONFIG REQUIRED)
find_package(hipsparse CONFIG REQUIRED)
find_package(rocsolver CONFIG REQUIRED)
find_package(hipsolver CONFIG REQUIRED)
find_package(hipblaslt CONFIG REQUIRED)
find_package(miopen CONFIG REQUIRED)
find_package(Torch REQUIRED)
"""
if text.count(old) != 1:
    raise SystemExit(f"expected one Torch find_package, found {text.count(old)}")
p.write_text(text.replace(old, new, 1))
PY

%build -p
export BUILD_VERSION=%{version}
# Headless chroot: torch.cuda.is_available() is false, so IS_ROCM
# hipifies vision.cpp beside the original and the CPU extension
# compiles both (duplicate vision::cuda_version). FORCE_CUDA selects
# CUDAExtension, which keeps only the hipified file.
# https://github.com/pytorch/vision/issues/9298
export FORCE_CUDA=1
export PYTORCH_ROCM_ARCH='gfx906;gfx908;gfx90a;gfx942;gfx1030;gfx1100;gfx1101;gfx1102;gfx1200;gfx1201'
export ROCM_PATH=%{_prefix}
export ROCM_HOME=%{_prefix}
export HIP_CLANG_PATH=%{_bindir}
export HIP_DEVICE_LIB_PATH=%{_libdir}/amdgcn/bitcode
export MAX_JOBS=4
# nvJPEG is CUDA-only; setup.py still defaults it on.
export TORCHVISION_USE_NVJPEG=0
export TORCHVISION_USE_PNG=1
export TORCHVISION_USE_JPEG=1
export TORCHVISION_USE_WEBP=1
export TORCH_CUDA_ARCH_LIST=
# torch.utils.cpp_extension injects -std=c++20 into every compile,
# including bundled giflib *.c. Strip that flag for the C compiler.
cat > c-no-cxxstd <<'EOF'
#!/bin/bash
args=()
for a in "$@"; do
	case "$a" in
	-std=c++*) ;;
	*) args+=("$a") ;;
	esac
done
exec /usr/bin/clang "${args[@]}"
EOF
chmod +x c-no-cxxstd
export CC="$PWD/c-no-cxxstd"
export CXX=clang++

%files
%doc README.md
%license LICENSE
%{python_sitearch}/torchvision
%{python_sitearch}/torchvision-*.*-info
