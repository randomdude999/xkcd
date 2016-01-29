#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# A command line xkcd client
# Requires python
# simplejson is recommended (from pip), but standard json will do
# readline is recommended, but not required
# Note: settings are configured for linux, on Windows you might have to change
# some settings (lines 53-59)

# Copyright © 2016 randomdude999
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


#  #############################
#  # Imports                   #
#  #############################

import os
import sys
import shutil
from subprocess import Popen, PIPE
import random  # those are standard
if sys.version_info[0] < 3:
    import urllib2 as urllib
else:
    import urllib.request as urllib
try:
    import simplejson as json
except ImportError:
    import json
try:
    import readline
except ImportError:
    # Well, you don't *have* to have readline, but it definitely helps!
    readline = None


#  #############################
#  # Configuration             #
#  #############################

# Main config

prompt = "xkcd [%s]> "  # the %s is current comic number
display_cmd = "display %s"  # command used to display images, %s is file path
html_renderer = "w3m -dump -T text/html -O utf-8"  # html to text renderer
tmpimg_location = "/tmp/xkcd/"  # remember trailing (back)slash
save_location = os.getenv("HOME") + "/Pictures/"  # Default save location
titles_location = "/usr/share/xkcd/titles.txt"  # Location to store comic titles
transcripts_location = "/usr/share/xkcd/transcripts.txt"  # ^ for transcripts
alt_texts_location = "/usr/share/xkcd/alt_texts.txt"  # ^^ for title texts
# Disable if you are using windows / don't know what is the program "less"
use_less = True

# URLs

api_url = "http://xkcd.com/%s/info.0.json"  # Comic metadata URL (%s = comic #)
explainxkcd_url = "http://www.explainxkcd.com/%s"


#  #############################
#  # Function definitions      #
#  #############################

def print_long_text(text):
    if use_less:
        try:
            proc = Popen("less", shell=True, stdin=PIPE)
        except OSError:
            return text
        proc.communicate(text.encode())
        return ""
    else:
        return text


def get_url(url, return_how_much=0):
    req = urllib.Request(url)
    req.add_header("User-Agent", "xkcd/0.1 (by randomdude999 <just.so.you.can."
                                 "email.me@gmail.com>)")
    try:
        response = urllib.urlopen(req)
    except (IOError, urllib.URLError) as err:
        return err
    content = response.read()
    response.close()
    if return_how_much == 0:
        return content
    elif return_how_much == 1:
        return content, response.getcode()
    elif return_how_much > 1:
        return content, response


def get_img(num):
    data = get_url(api_url % num)
    try:
        comic_data = json.loads(data.decode('utf-8'))
        img_source = comic_data['img']
    except (KeyError, ValueError):
        return "Something went wrong when decoding JSON\nraw text:\n%s" % data
    result = get_url(img_source, return_how_much=1)
    if result[1] == 404:
        return "No image for comic found (maybe it's interactive?)"
    else:
        img_data = result[0]
        if not os.path.isdir(tmpimg_location):
            os.mkdir(tmpimg_location)
        fd = open(tmpimg_location + "%s.png" % sel_comic, 'wb')
        fd.write(img_data)
        fd.close()


def get_offline_metadata():
    try:
        with open(titles_location) as titles:
            titles_str = titles.read()
        with open(transcripts_location) as transcripts:
            transcripts_str = transcripts.read()
    except OSError as err:
        return err
    titles_list = titles_str.split("\n")
    transcripts_list = transcripts_str.split("\n")
    return titles_list, transcripts_list


def search_titles(titles_list, query):
    matches = []
    for x in titles_list:
        if query.lower() in ":".join(x.split(":")[1:]).lower():
            matches.append(x)
    return matches


def search_transcripts(transcripts_list, query, titles_list):
    matches = []
    for x in transcripts_list:
        try:
            if query.lower() in eval(":".join(x.split(":")[1:])).lower():
                matches.append(titles_list[transcripts_list.index(x)])
        except SyntaxError:
            pass
    return matches


def parse_input(inp):
    cmds = inp.split(";")
    for cmd in cmds:
        cmd = cmd.strip()
        args = cmd.split(" ")
        cmd = args.pop(0)
        if cmd in commands:
            try:
                print(commands[cmd](*args))
            except Exception as err:
                print(err)
        elif len(cmd) == 0:
            pass
        else:
            print("Unknown command")


def get_printable_data(api_data):
    try:
        data = json.loads(api_data.decode('utf-8'))
        release_date = (data['year'], data['month'], data['day'])
        transcript = data['transcript']
    except (ValueError, KeyError):
        return "Something went wrong when decoding JSON\nraw text:\n%s" % \
            api_data
    if len(transcript) == 0:
        transcript = "No transcript avaliable yet.\n\nTitle text: \"" + \
            data['alt'] + "\""
    output = data['title'] + "\nRelease date: %s-%s-%s" % release_date + \
        "\n" + transcript
    return output


def display_img(comic):
    create_tmpfile_if_not_exist(comic)
    os.system(display_cmd % (tmpimg_location + "%s.png" % comic))
    return ""


def display_text(comic):
    response = get_url(api_url % comic, return_how_much=1)
    if response[1] != 200:
        return "Something might've gone wrong (response code: %s)" % response[1]
    content = response[0]
    output = get_printable_data(content)
    return print_long_text(output)


def random_unique():
    global seen_comics
    avail = list(range(1, cur_max_comic))
    for x in seen_comics:
        avail.remove(x)
    avail.remove(404)
    output = random.choice(avail)
    seen_comics.append(sel_comic)
    return output


def update_search_db():
    title_file = open(titles_location, 'r')
    title_file_contents = title_file.read()
    title_file.close()
    last_line = title_file_contents.split("\n")[-2]
    last_comic = int(last_line.split(":")[0])
    output = "%s comics not in title database found." % \
             (cur_max_comic - last_comic)
    if cur_max_comic > last_comic:
        title_file = open(titles_location, 'a')
        transcripts_file = open(transcripts_location, 'a')
        alt_texts_file = open(alt_texts_location, 'a')
        for x in range(last_comic + 1, cur_max_comic + 1):
            with urllib.urlopen(api_url % x) as response:
                resp_json = json.loads(response.read())
                title = repr(resp_json['title'])
                number = resp_json['num']
                transcript = repr(resp_json['transcript'])
                alt_text = repr(resp_json['alt'])
                title_file.write("%s:%s\n" % (number, title))
                transcripts_file.write("%s:%s\n" % (number, transcript))
                alt_texts_file.write("%s:%s\n" % (number, alt_text))
        title_file.close()
        transcripts_file.close()
        alt_texts_file.close()
    return output


def create_tmpfile_if_not_exist(comic):
    if not os.path.exists(tmpimg_location + "%s.png" % comic):
        get_img(comic)


def get_amount_from_args(*arguments):
    if len(arguments[0]) == 0:
        amount = 1
    else:
        try:
            amount = int(arguments[0][0])
        except ValueError:
            amount = 1
    return amount


#  #############################
#  # Command definitions       #
#  #############################

def command_random(*arguments):
    global sel_comic
    if "-f" in arguments:
        sel_comic = random.randint(1, cur_max_comic)
    else:
        sel_comic = random_unique()
    if "-d" in arguments:
        return command_display()
    if "-i" in arguments:
        return command_display('img')
    return ""


def command_display(*arguments):
    if len(arguments) > 0:
        try:
            comic = int(arguments[0])
        except ValueError:
            comic = sel_comic
    else:
        comic = sel_comic
    if "img" in arguments:
        return display_img(comic)
    else:
        return display_text(comic)


def command_explain(*arguments):
    if len(arguments) < 1:
        comic = sel_comic
    else:
        comic = arguments[0]
    location = explainxkcd_url % comic
    content = get_url(location)
    try:
        proc = Popen(html_renderer, shell=True, stdin=PIPE, stdout=PIPE)
    except OSError as err:
        return err
    content = proc.communicate(content)[0]
    content = "".join(content.decode('utf-8').split("[edit] ")[1:-1])
    return print_long_text(content)


def command_save(*arguments):
    if len(arguments) < 1:
        location = save_location + str(sel_comic) + ".png"
    else:
        location = " ".join(arguments)
    output = "Saving comic %s to location %s" % (sel_comic, location) + "\n"
    create_tmpfile_if_not_exist(sel_comic)
    try:
        shutil.copy(tmpimg_location + "%s.png" % sel_comic, location)
    except OSError as err:
        return err
    return output


def command_next(*arguments):
    global sel_comic
    amount = get_amount_from_args(arguments)
    sel_comic += amount
    if sel_comic > cur_max_comic:
        sel_comic = cur_max_comic
    elif sel_comic == 404:
        sel_comic = 405
    return ""


def command_prev(*arguments):
    global sel_comic
    amount = get_amount_from_args(arguments)
    sel_comic -= amount
    if sel_comic < 1:
        sel_comic = 1
    elif sel_comic == 404:
        sel_comic = 403
    return ""


def command_first(*arguments):
    if len(arguments) > 0:
        return "Command does not take arguments"
    global sel_comic
    sel_comic = 1
    return ""


def command_last(*arguments):
    if len(arguments) > 0:
        return "Command does not take arguments"
    global sel_comic
    sel_comic = cur_max_comic
    return ""


def command_goto(*arguments):
    global sel_comic
    if len(arguments) < 1:
        comic = cur_max_comic
    else:
        try:
            comic = int(arguments[0])
        except ValueError:
            comic = cur_max_comic
    if comic < 1:
        comic = 1
    elif comic > cur_max_comic:
        comic = cur_max_comic
    sel_comic = comic
    return ""


def command_update(*arguments):
    global sel_comic, cur_max_comic
    output = ""
    response = get_url(api_url % "")
    new_max_comic = json.loads(response)['num']
    if new_max_comic > cur_max_comic:
        if cur_max_comic + 1 == new_max_comic:
            output += "1 new comic!\n"
        else:
            output += "%s new comics!\n" % (new_max_comic - cur_max_comic)
        cur_max_comic = new_max_comic
    else:
        output += "No new comics.\n"
    if "search_db" in arguments:
        output += update_search_db()
    return output


def command_exit(*arguments):
    global isrunning
    if len(arguments) > 0:
        return "Command does not take arguments"
    isrunning = False
    return ""


def command_license(*arguments):
    if len(arguments) > 0:
        return "Command does not take arguments"
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
    return program_license


def command_help(*arguments):
    if len(arguments) == 0:
        return """
Use `next', `prev', `first', `last', `goto' and `random' to select comics.
Use `display' to show comics' transcriptions.
Use `display img' to display images (requires imagemagick and a running X
server).
Use `explain' to open the explain xkcd page for that comic.
Use `update' to check for new comics.
Use `save' to save comics to disk.
Use `quit' or `exit' to exit.
Use `help [command]' to get help."""
    else:
        command = arguments[0]
        if command in commands_help:
            return commands_help[command]
        elif command in commands:
            return "Command exists, but has no documentation."
        else:
            return "Unknown command."


def command_search(*arguments):
    if not os.path.exists(titles_location):
        return "This function needs a dictionary of comic titles. Please see " \
               "the documentation of the program for more info."
    elif len(arguments) < 1:
        return "Missing argument: query"
    else:
        query = " ".join(arguments)
        titles_list, transcripts_list = get_offline_metadata()
        matches = []
        matches += search_titles(titles_list, query)
        matches += search_transcripts(transcripts_list, query, titles_list)
        output = "Matches:\n"
        for x in matches:
            result = (x.split(":")[0], ":".join(x.split(":")[1:]))
            output += "(#%s) %s\n" % result
        return output

#  #############################
#  # Commands index & help     #
#  #############################

commands = {
    "random": command_random,
    "display": command_display,
    "explain": command_explain,
    "next": command_next,
    "prev": command_prev,
    "previous": command_prev,
    "first": command_first,
    "last": command_last,
    "goto": command_goto,
    "update": command_update,
    "save": command_save,
    "search": command_search,
    "quit": command_exit,
    "exit": command_exit,
    "license": command_license,
    "help": command_help
}

commands_help = {
    "random": "Selects a random comic. When -d is passed, also "
              "displays the comic's title, release date and transcription. "
              "When -i is passed, also display image.",
    "display": "Displays selected comic's transcription or image. When called "
               "without arguments, will display text representation of "
               "selected comic. When called with `img' as an argument, "
               "displays image (using your selected method of displaying "
               "images). When first argument is number, displays comic with "
               "that ID.",
    "explain": "Opens selected comic's explainxkcd page with your chosen "
               "browser. If an argument is provided, open that comic's page. "
               "Great if you missed the point of a comic.",
    "next": "Selects next comic. When called with an argument, moves "
            "[argument] number of comics forward.",
    "prev": "Selects previous comic. When called with an argument, moves "
            "[argument] number of comics backward.",
    "first": "Selects the first comic. Takes no arguments.",
    "last": "Selects the last comic. Takes no arguments.",
    "goto": "Moves to comic number [argument]. Without arguments, goes to last "
            "comic.",
    "update": "Updates latest comic. Takes no arguments.",
    "save": "Saves selected comic to disk, with file name [arguments]. Without "
            "arguments, saves to `[comic number].png'.",
    "search": "Searches a database of comic titles for a specified query.",
    "quit": "Closes the program. Takes no arguments.",
    "help": "Shows help. With an argument, shows help for command [argument].",
    "license": "Shows license."
}

commands_help['previous'] = commands_help['prev']
commands_help['exit'] = commands_help['quit']


#  #############################
#  # Main code                 #
#  #############################

def main():
    sys.stdout.write("\x1b]0;xkcd\x07")
    print("A command line xkcd client (%s)" % version)
    print("By randomdude999")
    print("Type `help' or `license' for more info")

    while isrunning:
        try:
            inp = input(prompt % sel_comic)
        except (KeyboardInterrupt, EOFError):
            print()
            break
        parse_input(inp)

    if os.path.exists(tmpimg_location):
        shutil.rmtree(tmpimg_location)

if __name__ == "__main__":
    version = "v0.2"
    isrunning = True
    seen_comics = []
    try:
        response_ = urllib.urlopen(api_url % "")
    except urllib.URLError as urllib_error:
        print(urllib_error)
        sys.exit(1)
    cur_max_comic = json.loads(response_.read())['num']
    response_.close()
    sel_comic = cur_max_comic
    main()
