# libblackwood
EternityII solver

This is a reimplementation of Joshua Blackwood's algorithm to solve EternityII
(See https://github.com/jblackwood345/)

It is written in Python3 and generates a C external library.

## How to use

* Configure **go.sh** and run
  ```./go.sh```

* or directly
  * ```./main.py```
  * ```DEBUG=1 ./main.py```
  * ```TARGET=469 ./main.py```
  * ```CORES=2 TARGET=469 DEBUG=2 ./main.py```

* run just the library as one thread
  * ```python3 libblackwood.py```

    ![Demo libblackwood](https://raw.githubusercontent.com/jfbucas/libblackwood/main/img/libblackwood.gif)
