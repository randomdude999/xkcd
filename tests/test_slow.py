#!/usr/bin/env python
import unittest

import shutil
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import xkcd


class TestInternetRequiringCommands(unittest.TestCase):

    def test_command_display(self):
        result = xkcd.command_display(1, "NO_USE_LESS")
        expected_result = """\
Barrel - Part 1
Release date: 2006-1-1
[[A boy sits in a barrel which is floating in an ocean.]]
Boy: I wonder where I'll float next?
[[The barrel drifts into the distance. Nothing else can be seen.]]
{{Alt: Don't we all.}}\
"""
        self.assertEqual(result, expected_result)

    def test_command_explain(self):
        result = xkcd.command_explain(1000, "NO_USE_LESS")
        expected_result = """\
Explanation

This comic is the 1000th comic shown on xkcd, including 404: Not Found,
containing 1000 characters from previous comics arranged in the shape of the
number "1000". Megan is clearly excited as she screams "Woooo!", but Cueball,
in true nerd fashion, thinks in base 2, saying that there are "just 24 to go
until a big round-number milestone". The joke is that during programming, base
two is used more often than base 10, making milestones be powers of two rather
than powers of 10. Where 1000 is a round number in base 10 (10^3), 1024 is a
round number in base 2 (2^10).

Connect the Dots

There is a connect the dots puzzle hidden within the comic. However, rather
than using the conventional decimal system numbering which would start with 1
and count up, 2, 3, 4, 5, ... This connect the dots puzzle starts with 0 as a
programmer would do and counts up in binary numerical order -
0,1,10,11,100,101,110,111,1000,1001 and back to 0. The revealed image forms the
shape of a heart. This fits well with the title text where feeling less alone
can equate to feeling loved.

1000 comics binary.png

"""
        self.assertEqual(result, expected_result)

    def test_command_save(self):
        xkcd.command_save(1000, "1000.png")
        with open("1000.png", 'rb') as saved_image:
            content = saved_image.read()
        with open("1000_correct.png", 'rb') as correct_image:
            correct_content = correct_image.read()
        self.assertEqual(content, correct_content)
        shutil.rmtree(xkcd.tmpimg_location)
        os.remove("1000.png")

if __name__ == '__main__':
    unittest.main()
