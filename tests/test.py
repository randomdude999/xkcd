#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

import random
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import xkcd


class TestCommandNext(unittest.TestCase):

    def test_command_next_1(self):
        xkcd.sel_comic = 665
        xkcd.cur_max_comic = 1000
        xkcd.command_next()
        self.assertEqual(xkcd.sel_comic, 666)

    def test_command_next_many(self):
        xkcd.sel_comic = 656
        xkcd.cur_max_comic = 1000
        xkcd.command_next(10)
        self.assertEqual(xkcd.sel_comic, 666)

    def test_command_next_404(self):
        xkcd.sel_comic = 403
        xkcd.cur_max_comic = 1000
        xkcd.command_next()
        self.assertEqual(xkcd.sel_comic, 405)

    def test_command_next_max(self):
        xkcd.sel_comic = 1000
        xkcd.cur_max_comic = 1000
        xkcd.command_next()
        self.assertEqual(xkcd.sel_comic, 1000)


class TestCommandPrev(unittest.TestCase):

    def test_command_prev_1(self):
        xkcd.sel_comic = 667
        xkcd.command_prev()
        self.assertEqual(xkcd.sel_comic, 666)

    def test_command_prev_many(self):
        xkcd.sel_comic = 676
        xkcd.command_prev(10)
        self.assertEqual(xkcd.sel_comic, 666)

    def test_command_prev_404(self):
        xkcd.sel_comic = 405
        xkcd.command_prev()
        self.assertEqual(xkcd.sel_comic, 403)

    def test_command_prev_min(self):
        xkcd.sel_comic = 1
        xkcd.command_prev()
        self.assertEqual(xkcd.sel_comic, 1)


class TestCommandFirstLast(unittest.TestCase):

    def test_command_first(self):
        xkcd.sel_comic = 666
        xkcd.command_first()
        self.assertEqual(xkcd.sel_comic, 1)

    def test_command_last(self):
        xkcd.sel_comic = 1
        xkcd.cur_max_comic = 1000
        xkcd.command_last()
        self.assertEqual(xkcd.sel_comic, xkcd.cur_max_comic)


class TestCommandGoto(unittest.TestCase):

    def test_command_goto(self):
        xkcd.sel_comic = 1000
        xkcd.cur_max_comic = 1000
        xkcd.command_goto(666)
        self.assertEqual(xkcd.sel_comic, 666)

    def test_command_goto_404(self):
        xkcd.sel_comic = 666
        xkcd.cur_max_comic = 1000
        response = xkcd.command_goto(404)
        self.assertEqual(response, "404 Not Found")

    def test_command_goto_first(self):
        xkcd.sel_comic = 666
        xkcd.cur_max_comic = 1000
        xkcd.command_goto(0)
        self.assertEqual(xkcd.sel_comic, 1)

    def test_command_goto_last(self):
        xkcd.sel_comic = 666
        xkcd.cur_max_comic = 1000
        xkcd.command_goto(9001)
        self.assertEqual(xkcd.sel_comic, xkcd.cur_max_comic)


class TestCommandsExitLicense(unittest.TestCase):

    def test_command_exit(self):
        xkcd.isrunning = True
        xkcd.command_exit()
        self.assertEqual(xkcd.isrunning, False)

    def test_command_license(self):
        expected_output = """
Copyright © 2016 randomdude999
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>."""
        output = xkcd.command_license()
        self.assertEqual(output, expected_output)


class TestCommandHelp(unittest.TestCase):

    def test_command_help_noargs(self):
        expected_output = """
Use `next', `prev', `first', `last', `goto' and `random' to select comics.
Use `display' to show comics' transcriptions.
Use `display img' to display images (requires imagemagick and a running X
server).
Use `explain' to open the explain xkcd page for that comic.
Use `update' to check for new comics.
Use `save' to save comics to disk.
Use `quit' or exit to exit.
Use `help [command]' to get help."""
        output = xkcd.command_help()
        self.assertEqual(output, expected_output)

    def test_command_help_progs(self):
        for command in xkcd.commands_help:
            expected_output = xkcd.commands_help[command]
            output = xkcd.command_help(command)
            self.assertEqual(output, expected_output)

    def test_command_help_uknowncommand(self):
        expected_output = "Unknown command."
        output = xkcd.command_help("thisisnotarealcommand")
        self.assertEqual(output, expected_output)


class TestCommandRandom(unittest.TestCase):

    def test_command_random_fast(self):
        random.seed(666)
        xkcd.cur_max_comic = 1000
        xkcd.sel_comic = 1
        randint = random.randint(1, xkcd.cur_max_comic)
        random.seed(666)
        xkcd.command_random("-f")
        self.assertEqual(xkcd.sel_comic, randint)

if __name__ == '__main__':
    sel_comic = 0
    unittest.main()
