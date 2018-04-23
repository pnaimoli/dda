# Project Title

Double Dummy Analyzer - a crummy double dummy solver with some cool features!

## Getting Started

### Prerequisites

* [Boost](https://github.com/boostorg/boost) - to compile libdda.so
* Python3 - to run ehas.py

### Building

```
make -C src
cd redeal/dds/src && make -f Makefiles/Makefile_Mac_clang_shared && cp libdds.so ../../
```

### Running

```
python3 -u -m redeal.redeal ehas.py | tee output.pbn
```
