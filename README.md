# Introduction

A crummy double dummy solver with some cool features!
Running ehas.py uses redeal and the Double Dummy Analyzer library to generate
hands where a squeeze is **required** in order to make 3NT.

# Usage

## Prerequisites

* [Boost](https://github.com/boostorg/boost) - to compile libdda.so
* Python3 - to run ehas.py

## Building

```
make -C src
cd redeal/dds/src && make -f Makefiles/Makefile_Mac_clang_shared && cp libdds.so ../../
```

## Running

```
python3 -u -m redeal.redeal ehas.py | tee output.pbn
```

# Credits

* Bo Haglund and Sorein Hein's [Double Dummy Solver](https://github.com/dds-bridge/dds)
* James Dow Allen's [Double Dummy Solver](https://fabpedigree.com/james/dbldum.htm)
* Sumit - for the most important idea
