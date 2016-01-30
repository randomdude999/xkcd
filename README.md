# xkcd
[![Build Status](https://travis-ci.org/randomdude999/xkcd.svg?branch=master)](https://travis-ci.org/randomdude999/xkcd) [![Coverage Status](https://coveralls.io/repos/github/randomdude999/xkcd/badge.svg?branch=master)](https://coveralls.io/github/randomdude999/xkcd?branch=master) [![Code Climate](https://codeclimate.com/github/randomdude999/xkcd/badges/gpa.svg?branch=master)](https://codeclimate.com/github/randomdude999/xkcd)

A command line xkcd client.

## Installation

### Which Python?

If you see a green "build | passing" near the top, that means the program is fully working in Python 2.7, 3.3, 3.4 and 3.5. If it's a red "build | failing", click it for more information.

### Platform-independent

Download / `git clone` the repository. If you are not a developer, you can delete all files except `xkcd.py` and `search.zip`.

### Linux

(Should work in OSX too)

Open a terminal. Then make sure you are in the directory you downloaded.  
Type:

    sudo cp xkcd.py /usr/local/bin/xkcd

This will copy `xkcd.py` to `/usr/local/bin` under the name `xkcd`.

If you also want searching:

    unzip search.zip
    sudo mkdir -p /usr/share/xkcd
    sudo cp titles.txt transcripts.txt /usr/share/xkcd

Now type `xkcd` to test if it worked.

## Tests

This script uses the standard `unittest`. To test, `cd tests` and run `test.py`. Note: testing search functions requires that the `search.zip` file be unpacked to the tests directory.