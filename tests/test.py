#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest

import random
import os
import sys
import shutil
import json

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

comic_1_transcript = """\
Barrel - Part 1
Release date: 2006-1-1
[[A boy sits in a barrel which is floating in an ocean.]]
Boy: I wonder where I'll float next?
[[The barrel drifts into the distance. Nothing else can be seen.]]
{{Alt: Don't we all.}}\
"""

program_license = """\
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


class TestInternetRequiringCommands(unittest.TestCase):

    def test_command_display(self):
        xkcd.use_less = False
        result = xkcd.command_display(1)
        excepted_result = comic_1_transcript
        self.assertEqual(result, excepted_result)

    def test_command_display_invalid_arg(self):
        xkcd.use_less = False
        xkcd.sel_comic = 1
        result = xkcd.command_display("test")
        expected_result = comic_1_transcript
        self.assertEqual(result, expected_result)

    @unittest.skipUnless(os.path.exists(xkcd.html_renderer[0]),
                         "Renderer not found")
    def test_command_explain(self):
        xkcd.use_less = False
        xkcd.sel_comic = 1000
        result = xkcd.command_explain()
        excepted_result = comic_1000_transcript
        self.assertEqual(result, excepted_result)

    @unittest.skipUnless(os.path.exists(xkcd.html_renderer[0]),
                         "Renderer not found")
    def test_command_explain_with_arg(self):
        xkcd.use_less = False
        result = xkcd.command_explain(1000)
        excepted_result = comic_1000_transcript
        self.assertEqual(result, excepted_result)

    def test_command_explain_invalidRenderer(self):
        xkcd.sel_comic = 1
        renderer = xkcd.html_renderer
        xkcd.html_renderer = "this_is_a_fake_command"
        output = xkcd.command_explain()
        excepted_output = "HTML renderer not found"
        xkcd.html_renderer = renderer
        self.assertEqual(output, excepted_output)

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

    def test_command_save_404(self):
        xkcd.sel_comic = 1608
        output = xkcd.command_save()
        excepted_output = "No image for comic found (maybe it's interactive?)"
        self.assertEqual(output, excepted_output)

    def test_command_random_display(self):
        if sys.version_info[0] == 3:
            random_seed = 1000
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
        else:
            random_seed = 666
            expected_output = """\
Frustration
Release date: 2008-8-1
[[Bra with rubik's cube closure.]]
{{title text: 'Don't worry, I can do it in under a minute.' \
'Yes, I've noticed.'}}"""
        xkcd.use_less = False
        random.seed(random_seed)
        xkcd.cur_max_comic = 1000
        xkcd.sel_comic = 1
        output = xkcd.command_random("-f", "-d")
        self.assertEqual(output, expected_output)

    def test_command_update(self):
        xkcd.cur_max_comic = 1000
        output = xkcd.command_update()
        generic_output = " new comics!\n"
        self.assertEqual(output[-13:], generic_output)

    def test_command_update_1_comic(self):
        response = xkcd.get_url(xkcd.api_url % "")
        new_max_comic = json.loads(response.decode('utf-8'))['num'] - 1
        xkcd.cur_max_comic = new_max_comic
        output = xkcd.command_update()
        expected_output = "1 new comic!\n"
        self.assertEqual(output, expected_output)

    def test_command_update_no_new_comics(self):
        response = xkcd.get_url(xkcd.api_url % "")
        max_comic = json.loads(response.decode('utf-8'))['num']
        xkcd.cur_max_comic = max_comic
        output = xkcd.command_update()
        expected_output = "No new comics.\n"
        self.assertEqual(output, expected_output)


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

    def test_command_first_arg(self):
        output = xkcd.command_first("test")
        self.assertEqual(output, "Command does not take arguments")

    def test_command_last(self):
        xkcd.sel_comic = 1
        xkcd.cur_max_comic = 1000
        xkcd.command_last()
        self.assertEqual(xkcd.sel_comic, xkcd.cur_max_comic)

    def test_command_last_arg(self):
        output = xkcd.command_last("test")
        self.assertEqual(output, "Command does not take arguments")


class TestCommandGoto(unittest.TestCase):

    def test_command_goto(self):
        xkcd.sel_comic = 1000
        xkcd.cur_max_comic = 1000
        xkcd.command_goto(666)
        self.assertEqual(xkcd.sel_comic, 666)

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

    def test_command_goto_invalid_arg(self):
        xkcd.sel_comic = 666
        xkcd.cur_max_comic = 1000
        xkcd.command_goto("test")
        self.assertEqual(xkcd.sel_comic, xkcd.cur_max_comic)

    def test_command_goto_noargs(self):
        xkcd.sel_comic = 666
        xkcd.cur_max_comic = 1000
        xkcd.command_goto()
        self.assertEqual(xkcd.sel_comic, xkcd.cur_max_comic)


class TestCommandsExitLicense(unittest.TestCase):

    def test_command_exit(self):
        xkcd.isrunning = True
        xkcd.command_exit()
        self.assertEqual(xkcd.isrunning, False)

    def test_command_exit_arg(self):
        output = xkcd.command_exit("test")
        self.assertEqual(output, "Command does not take arguments")

    def test_command_license(self):
        excepted_output = program_license
        output = xkcd.command_license()
        self.assertEqual(output, excepted_output)

    def test_command_license_arg(self):
        output = xkcd.command_license("test")
        self.assertEqual(output, "Command does not take arguments")


class TestCommandHelp(unittest.TestCase):

    def test_command_help_noargs(self):
        excepted_output = """
Use `next', `prev', `first', `last', `goto' and `random' to select comics.
Use `display' to show comics' transcriptions.
Use `display img' to display images (requires imagemagick and a running X
server).
Use `explain' to open the explain xkcd page for that comic.
Use `update' to check for new comics.
Use `save' to save comics to disk.
Use `quit' or `exit' to exit.
Use `help [command]' to get help."""
        output = xkcd.command_help()
        self.assertEqual(output, excepted_output)

    def test_command_help_progs(self):
        for command in xkcd.commands_help:
            excepted_output = xkcd.commands_help[command]
            output = xkcd.command_help(command)
            self.assertEqual(output, excepted_output)

    def test_command_help_uknowncommand(self):
        excepted_output = "Unknown command."
        output = xkcd.command_help("thisisnotarealcommand")
        self.assertEqual(output, excepted_output)

    def test_command_help_nodoc(self):
        xkcd.commands['test'] = "Test!"
        output = xkcd.command_help("test")
        expected_output = "Command exists, but has no documentation."
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

    def test_command_random_unique(self):
        xkcd.seen_comics = list(range(1, 1000))
        xkcd.cur_max_comic = 1000
        xkcd.seen_comics.remove(404)
        xkcd.sel_comic = 1
        xkcd.command_random()
        self.assertEqual(xkcd.sel_comic, 1000)


class TestCommandSearch(unittest.TestCase):

    def setUp(self):
        xkcd.titles_location = "titles.txt"
        xkcd.transcripts_location = "transcripts.txt"

    def test_command_search(self):
        output = xkcd.command_search("barrel")
        expected_outputs = ["Matches:", "(#1) Barrel - Part 1",
                            "(#11) Barrel - Part 2", "(#374) Journal",
                            "(#25) Barrel - Part 4", "(#960) Subliminal",
                            "(#728) iPad", "(#22) Barrel - Part 3",
                            "(#1455) Trolley Problem", "(#31) Barrel - Part 5",
                            "(#746) Birth"]

        for x in expected_outputs:
            self.assertTrue(x in output)

    def test_command_search_title(self):
        output = xkcd.command_search_titles("barrel")
        excepted_outputs = ["Matches:", "(#31) Barrel - Part 5",
                            "(#11) Barrel - Part 2", "(#1) Barrel - Part 1",
                            "(#22) Barrel - Part 3", "(#25) Barrel - Part 4"]
        for x in excepted_outputs:
            self.assertTrue(x in output)

    def test_command_search_transcripts(self):
        output = xkcd.command_search_transcripts("asdf")
        excepted_output = "Matches:\n(#1296) Git Commit\n"
        self.assertEqual(output, excepted_output)

    def test_command_search_noargs(self):
        output = xkcd.command_search()
        excepted_output = "Missing argument: query"
        self.assertEqual(output, excepted_output)

    def test_command_search_titles_noargs(self):
        excepted_output = "Missing argument: query"
        output = xkcd.command_search_titles()
        self.assertEqual(output, excepted_output)

    def test_command_search_transcripts_noargs(self):
        excepted_output = "Missing argument: query"
        output = xkcd.command_search_transcripts()
        self.assertEqual(output, excepted_output)

    def test_command_search_no_titles(self):
        excepted_output = "This function needs a dictionary of comic titles." \
                          " Please see the documentation of the program for" \
                          " more info."
        old_titles = xkcd.titles_location
        xkcd.titles_location = "AAA"
        output = xkcd.command_search()
        xkcd.titles_location = old_titles
        self.assertEqual(output, excepted_output)

    def test_command_search_titles_no_titles(self):
        excepted_output = "This function needs a dictionary of comic titles." \
                          " Please see the documentation of the program for" \
                          " more info."
        old_titles = xkcd.titles_location
        xkcd.titles_location = "AAA"
        output = xkcd.command_search_titles()
        xkcd.titles_location = old_titles
        self.assertEqual(output, excepted_output)

    def test_command_search_transcripts_no_titles(self):
        excepted_output = "This function needs a dictionary of comic titles." \
                          " Please see the documentation of the program for" \
                          " more info."
        old_titles = xkcd.titles_location
        xkcd.titles_location = "AAA"
        output = xkcd.command_search_transcripts()
        xkcd.titles_location = old_titles
        self.assertEqual(output, excepted_output)

    def test_update_search_db(self):
        xkcd.cur_max_comic = 1
        xkcd.command_update()
        old_titles_loc = xkcd.titles_location
        old_transcripts_loc = xkcd.transcripts_location
        xkcd.titles_location = "test.txt"
        xkcd.transcripts_location = "test2.txt"
        fd = open("test.txt", 'w')
        fd.write(str(xkcd.cur_max_comic - 1))
        fd.write(":'Test'\n")
        fd.close()
        fd = open("test2.txt", 'w')
        fd.write(str(xkcd.cur_max_comic - 1))
        fd.write(":'Test'\n")
        fd.close()
        output = xkcd.command_update("search_db")
        expected_output = "No new comics.\n1 comics not in title database " \
                          "found."
        xkcd.titles_location = old_titles_loc
        xkcd.transcripts_location = old_transcripts_loc
        os.remove("test.txt")
        os.remove("test2.txt")
        self.assertEqual(output, expected_output)


class TestMiscFunctions(unittest.TestCase):

    def test_func_parse_input(self):
        cmd = "license"
        output = xkcd.parse_input(cmd)
        excepted_output = program_license + "\n"
        self.assertEqual(output, excepted_output)

    def test_func_parse_input_unknown_cmd(self):
        cmd = "nosuchcommand"
        output = xkcd.parse_input(cmd)
        excepted_output = "Unknown command\n"
        self.assertEqual(output, excepted_output)

    def test_get_img_invalid_comic(self):
        output = xkcd.get_img("test")
        expected_output = "Something went wrong when decoding JSON\nraw text:" \
                          "\n"
        self.assertIn(expected_output, output)

    def test_parse_input_no_cmd(self):
        output = xkcd.parse_input("")
        expected_output = ""
        self.assertEqual(output, expected_output)

    def test_get_printable_data_invalid_data(self):
        output = xkcd.get_printable_data("qwerty".encode())
        expected_output = "Something went wrong when decoding JSON\nraw " \
                          "text:\nqwerty"
        self.assertEqual(output, expected_output)

    def test_get_printable_data_no_transcript(self):
        inp = {
            'year': 2016,
            'month': 1,
            'day': 1,
            'transcript': "",
            'alt': "Test",
            'title': "Test"
        }
        output = xkcd.get_printable_data(json.dumps(inp).encode())
        expected_output = u"Test\nRelease date: 2016-1-1\nNo transcript " \
                          "available yet.\n\nTitle text: \"Test\""
        self.assertEqual(output, expected_output)

    def test_display_text_404(self):
        output = xkcd.display_text("test")
        expected_output = "Something might've gone wrong (response code: 404)"
        self.assertEqual(output, expected_output)

    def test_get_amout_from_args_invalid_arg(self):
        output = xkcd.get_amount_from_args("test")
        expected_output = 1
        self.assertEqual(output, expected_output)

    def test_less_missing(self):
        xkcd.use_less = True
        xkcd.less_cmd = "thisisafakecmd"
        output = xkcd.print_long_text("Test")
        expected_output = "Test"
        self.assertEqual(output, expected_output)
        xkcd.use_less = False


if __name__ == '__main__':
    unittest.main()
