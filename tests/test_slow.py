#!/usr/bin/env python3
import unittest

import shutil
import os
import sys
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import xkcd


comic_1000_transcript = """\
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


class TestInternetRequiringCommands(unittest.TestCase):

    def test_command_display(self):
        xkcd.use_less = False
        result = xkcd.command_display(1)
        expected_result = """\
Barrel - Part 1
Release date: 2006-1-1
[[A boy sits in a barrel which is floating in an ocean.]]
Boy: I wonder where I'll float next?
[[The barrel drifts into the distance. Nothing else can be seen.]]
{{Alt: Don't we all.}}\
"""
        self.assertEqual(result, expected_result)

    @unittest.skipUnless(os.path.exists(xkcd.html_renderer[0]),
                         "Renderer not found")
    def test_command_explain(self):
        xkcd.use_less = False
        xkcd.sel_comic = 1000
        result = xkcd.command_explain()
        expected_result = comic_1000_transcript
        self.assertEqual(result, expected_result)

    @unittest.skipUnless(os.path.exists(xkcd.html_renderer[0]),
                         "Renderer not found")
    def test_command_explain_with_arg(self):
        xkcd.use_less = False
        result = xkcd.command_explain(1000)
        expected_result = comic_1000_transcript
        self.assertEqual(result, expected_result)

    def test_command_explain_invalidRenderer(self):
        xkcd.sel_comic = 1
        renderer = xkcd.html_renderer
        xkcd.html_renderer = "this_is_a_fake_command"
        output = xkcd.command_explain()
        expected_output = "HTML renderer not found"
        xkcd.html_renderer = renderer
        self.assertEqual(output, expected_output)

    def test_command_save(self):
        xkcd.sel_comic = 1000
        xkcd.command_save("1000.png")
        with open("1000.png", 'rb') as saved_image:
            content = saved_image.read()
        try:
            with open("1000_correct.png", 'rb') as correct_image:
                correct_content = correct_image.read()
        except IOError:
            with open("tests/1000_correct.png", 'rb') as correct_image:
                correct_content = correct_image.read()
        self.assertEqual(content, correct_content)
        shutil.rmtree(xkcd.tmpimg_location)
        os.remove("1000.png")

    @unittest.skipIf(sys.version_info[0] < 3, "Py3 random != Py2 random")
    def test_command_random_display_py3(self):
        xkcd.use_less = False
        random.seed(1000)
        xkcd.cur_max_comic = 1000
        xkcd.sel_comic = 1
        output = xkcd.command_random("-f", "-d")
        expected_output = """\
debian-main
Release date: 2010-9-24
<<AAAAAAAA>>
[[A swarm of insects cover a computer and a person.  The person is leaning \
back on their chair, flailing to get away.]]

My package made it into Debian-main because it looked innocuous enough; no \
one noticed "locusts" in the dependency list.

{{Title text: dpkg: error processing package (--purge): subprocess \
pre-removal script returned error exit 163: \
OH_GOD_THEYRE_INSIDE_MY_CLOTHES}}"""
        self.assertEqual(output, expected_output)

    @unittest.skipIf(sys.version_info[0] > 2, "Py3 random != Py2 random")
    def test_command_random_display_py2(self):
        xkcd.use_less = False
        random.seed(666)
        xkcd.cur_max_comic = 1000
        xkcd.sel_comic = 1
        output = xkcd.command_random("-f", "-d")
        expected_output = """\
Frustration
Release date: 2008-8-1
[[Bra with rubik's cube closure.]]
{{title text: 'Don't worry, I can do it in under a minute.' \
'Yes, I've noticed.'}}"""
        self.assertEqual(output, expected_output)

    def test_command_update(self):
        xkcd.cur_max_comic = 1000
        output = xkcd.command_update()
        generic_output = " new comics!"
        self.assertEqual(output[-12:], generic_output)

if __name__ == '__main__':
    unittest.main()
