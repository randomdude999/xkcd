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
# Disable if you are using windows / don't know what is the program "less"
use_less = True

# URLs

base_url = "http://c.xkcd.com"  # That weird API-like website (try browsing it!)
random_url = base_url + "/random/comic"  # Random page URL
api_url = base_url + "/api-0/jsonp/comic/%s"  # Comic metadata URL
explainxkcd_url = "http://www.explainxkcd.com/%s"


#  #############################
#  # Command definitions       #
#  #############################

def command_random(*arguments):
    if len(arguments) > 0:
        if "-d" in arguments or "--display" in arguments:
            display_comic = True
        else:
            display_comic = False
        if "-i" in arguments or "--display-img" in arguments:
            display_comic_image = True
        else:
            display_comic_image = False
        if "-f" in arguments or "--fast" in arguments:
            uniques = False
        else:
            uniques = True
    else:
        display_comic = False
        display_comic_image = False
        uniques = True
    global sel_comic
    if uniques:
        avail = list(range(1, cur_max_comic))
        for x in seen_comics:
            avail.remove(x)
        avail.remove(404)
        sel = random.choice(avail)
        seen_comics.append(sel)
    else:
        sel = random.randint(1, cur_max_comic)
    sel_comic = sel
    if display_comic:
        return command_display()
    if display_comic_image:
        return command_display('img')


def command_display(*arguments):
    if len(arguments) > 0:
        try:
            comic = int(arguments[0])
        except ValueError:
            comic = sel_comic
        if "NO_USE_LESS" in arguments:
            use_less_override = True
        else:
            use_less_override = False
    else:
        comic = sel_comic
        use_less_override = False
    if "img" in arguments:
        if not os.path.exists(tmpimg_location + "%s.png" % sel_comic):
            # If we don't already have the image:
            response = urllib.urlopen(api_url % comic)
            comic_data = json.loads(response.read())
            response.close()
            img_source = comic_data['img']
            response = urllib.urlopen(img_source)
            if response.getcode() == 404:
                return "No image for comic found (maybe it's interactive?)"
            else:
                img_data = response.read()
                if not os.path.isdir(tmpimg_location):
                    os.mkdir(tmpimg_location)
                fd = open(tmpimg_location + "%s.png" % sel_comic, 'wb')
                fd.write(img_data)
                fd.close()
            response.close()
        os.system(display_cmd % (tmpimg_location + "%s.png" % sel_comic))
    else:
        response = urllib.urlopen(api_url % comic)
        if response.getcode() != 200:
            return "Something might've gone wrong (response code: %s)" % \
                   response.getcode()
        content = response.read()
        response.close()
        data = json.loads(content.decode())
        release_date = (data['year'], data['month'], data['day'])
        transcript = data['transcript']
        if len(transcript) == 0:
            transcript = "No transcript avaliable yet.\n\nTitle text: \"" + \
                         data['alt'] + "\""
        output = data['title'] + "\nRelease date: %s-%s-%s" % release_date + \
            "\n" + transcript
        if use_less and not use_less_override:
            proc = Popen("less", shell=True, stdin=PIPE)
            proc.communicate(output.encode())
        else:
            return output
    return ""


def command_explain(*arguments):
    if len(arguments) < 1:
        comic = sel_comic
        use_less_override = False
    else:
        comic = arguments[0]
        if "NO_USE_LESS" in arguments:
            use_less_override = True
        else:
            use_less_override = False
    location = explainxkcd_url % comic
    req = urllib.Request(location)
    req.add_header("User-Agent", "xkcd/0.1 (by randomdude999 <just.so.you.can."
                                 "email.me@gmail.com>)")
    response = urllib.urlopen(req)
    content = response.read()
    response.close()
    proc = Popen(html_renderer, shell=True, stdin=PIPE, stdout=PIPE)
    content = proc.communicate(content)[0]
    # *WARNING: ABOMINATION INCOMING* #
    content = "".join(content.decode().split("[edit] ")[1:-1])
    if use_less and not use_less_override:
        proc = Popen("less", shell=True, stdin=PIPE)
        proc.communicate(content.encode())
    else:
        return content
    return ""


def command_save(*arguments):
    if len(arguments) < 1:
        comic = sel_comic
        location = save_location + str(comic) + ".png"
    else:
        comic = int(arguments[0])
        if len(arguments) > 1:
            location = " ".join(arguments[1:])
        else:
            location = save_location + str(comic) + ".png"
    output = "Saving comic %s to location %s" % (comic, location) + "\n"
    if not os.path.exists(tmpimg_location + "%s.png" % comic):
        response = urllib.urlopen(api_url % comic)
        comic_data = json.loads(response.read().decode())
        response.close()
        img_source = comic_data['img']
        response = urllib.urlopen(img_source)
        if response.getcode() == 404:
            return "No image for comic found (maybe it's interactive?)"
        else:
            img_data = response.read()
            if not os.path.isdir(tmpimg_location):
                os.mkdir(tmpimg_location)
            fd = open(tmpimg_location + "%s.png" % comic, 'wb')
            fd.write(img_data)
            fd.close()
        response.close()
    try:
        shutil.copy(tmpimg_location + "%s.png" % comic, location)
    except PermissionError as err:
        return err
    return output


def command_next(*arguments):
    global sel_comic
    if len(arguments) < 1:
        amount = 1
    else:
        amount = int(arguments[0])
    sel_comic += amount
    if sel_comic > cur_max_comic:
        sel_comic = cur_max_comic
    elif sel_comic == 404:
        sel_comic = 405
    return ""


def command_prev(*arguments):
    global sel_comic
    if len(arguments) < 1:
        amount = 1
    else:
        amount = int(arguments[0])
    sel_comic -= amount
    if sel_comic < 1:
        sel_comic = 1
    elif sel_comic == 404:
        sel_comic = 403
    return ""


def command_first(*arguments):
    global sel_comic
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command does not accept arguments"
    sel_comic = 1
    return output


def command_last(*arguments):
    global sel_comic
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command does not accept arguments"
    sel_comic = cur_max_comic
    return output


def command_goto(*arguments):
    global sel_comic
    if len(arguments) < 1:
        comic = cur_max_comic
    else:
        comic = int(arguments[0])
    if comic < 1:
        comic = 1
    elif comic > cur_max_comic:
        comic = cur_max_comic
    elif comic == 404:
        return "404 Not Found"
    sel_comic = comic
    return ""


def command_update(*arguments):
    global sel_comic, cur_max_comic
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command does not accept arguments\n"
    response = urllib.urlopen(api_url % "")
    new_max_comic = json.loads(response.read())['num']
    response.close()
    if new_max_comic > cur_max_comic:
        if cur_max_comic + 1 == new_max_comic:
            output += "1 new comic!\n"
        else:
            output += "%s new comics!\n" % (new_max_comic - cur_max_comic)
        cur_max_comic = new_max_comic
    else:
        output += "No new comics."
    return output


def command_exit(*arguments):
    global isrunning
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command does not accept arguments"
    isrunning = False
    return output


def command_license(*arguments):
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command takes no arguments\n"
    program_license = """
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
    output += program_license
    return output


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
Use `quit' or exit to exit.
Use `help [command]' to get help."""
    else:
        command = arguments[0]
        if command in commands_help:
            return commands_help[command]
        elif command in commands:
            return "Command exists, but has no documentation."
        else:
            return "Unknown command."

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
    "quit": command_exit,
    "exit": command_exit,
    "license": command_license,
    "help": command_help
}

commands_help = {
    "random": "Selects a random comic. When -d or --display is passed, also "
              "displays the comic's title, release date and transcription. "
              "When -i or --display-img is passed, also display image.",
    "display": "Displays selected comic's transcription or image. When called "
               "without arguments, will display text representation of "
               "selected comic. When called with 'img' as an argument, "
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
    "previous": "Selects previous comic. When called with an argument, moves "
                "[argument] number of comics backward.",
    "first": "Selects the first comic. Takes no arguments.",
    "last": "Selects the last comic. Takes no arguments.",
    "goto": "Moves to comic number [argument]. Without arguments, goes to last "
            "comic",
    "update": "Updates latest comic. Takes no arguments.",
    "save": "Saves selected comic to disk, with file name [argument]. Without "
            "arguments, saves to [comic number].png.",
    "quit": "Closes the program. Takes no arguments.",
    "exit": "Closes the program. Takes no arguments.",
    "help": "Shows help. With an argument, shows help for command [argument].",
    "license": "Shows license."
}


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
        cmds = inp.split(";")
        for cmd in cmds:
            cmd = cmd.strip()
            args = cmd.split(" ")
            cmd = args.pop(0)
            if cmd in commands:
                print(commands[cmd](*args))
            else:
                print("Unknown command")

    if os.path.exists(tmpimg_location):
        shutil.rmtree(tmpimg_location)

if __name__ == "__main__":
    version = "v0.1"
    isrunning = True
    seen_comics = []
    response_ = urllib.urlopen(api_url % "")
    cur_max_comic = json.loads(response_.read())['num']
    response_.close()
    sel_comic = cur_max_comic
    main()
