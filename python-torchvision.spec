%undefine _debugsource_packages

Name:		python-torchvision
Version:	0.28.0
Release:	1
Summary:	Datasets, transforms and models for computer vision (PyTorch)
License:	BSD-3-Clause
Group:		Development/Python
URL:		https://github.com/pytorch/vision
Source0:	https://github.com/pytorch/vision/archive/refs/tags/v%{version}.tar.gz#/vision-%{version}.tar.gz

BuildSystem:	python
BuildRequires:	python
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(libjpeg)
BuildRequires:	pkgconfig(libwebp)

BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(wheel)
BuildRequires:	python%{pyver}dist(torch)
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

%build -p
export BUILD_VERSION=%{version}
export FORCE_CUDA=0
# nvJPEG is CUDA-only; setup.py still defaults it on.
export TORCHVISION_USE_NVJPEG=0
export TORCHVISION_USE_PNG=1
export TORCHVISION_USE_JPEG=1
export TORCHVISION_USE_WEBP=1
export TORCH_CUDA_ARCH_LIST=

%files
%doc README.md
%license LICENSE
%{python_sitearch}/torchvision
%{python_sitearch}/torchvision-*.*-info
