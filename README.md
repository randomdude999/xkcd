# xkcd
[![Travis](https://img.shields.io/travis/randomdude999/xkcd/master.svg)](https://travis-ci.org/randomdude999/xkcd) [![GitHub release](https://img.shields.io/github/release/randomdude999/xkcd.svg)](https://github.com/randomdude999/xkcd/releases/latest)

A command line xkcd client.

## Installation

### Which Python?

If you see a green "build | passing" near the top, that means the program is fully working in Python 2.7, 3.3, 3.4 and 3.5. If it's a red "build | failing", click it for more information. (Sometimes, it's unittest's mistake, so check which jobs fail)

### Platform-independent

Download / `git clone` the repository. If you are not a developer, you can delete all files except `xkcd.py`.

### Linux

(Should work in OSX too)

Open a terminal. Then make sure you are in the directory you downloaded.  
Type:  
`sudo cp xkcd.py /usr/local/bin/xkcd`  
This will copy `xkcd.py` to `/usr/local/bin` under the name `xkcd`.

Now type `xkcd` to test if it worked.

### Windows

If you know how to install a python script to the path of a Windows machine, please [raise an issue](https://github.com/randomdude999/xkcd/issues/new)!

## Tests

This script uses the standard `unittest`. To test, `cd tests` and run `test.py`. There is also a `test_slow.py` that contains actions requiring an Internet connection.