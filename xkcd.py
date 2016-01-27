#!/usr/bin/env python3

# A command line xkcd client
# Requires python
# simplejson is recommended (from pip), but standard json will do
# readline is recommended, but not required
# Note: settings are configured for linux, on Windows you might have to change
# some settings (lines 48-51)

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
import urllib.request
import random  # those are standard
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

version = "v0.1"
prompt = "xkcd [%s]> "  # the %s is current comic number
display_cmd = "display %s"  # command used to display images, %s is file path
html_renderer = "w3m -dump -T text/html -O ascii"  # html to text renderer
tmpimg_location = "/tmp/xkcd/"  # remember trailing slash
save_location = os.getenv("HOME") + "/Pictures/"  # Default save location
# Disable if you are using windows / don't know what is the program "less"
use_less = True

# URLs

base_url = "http://c.xkcd.com"  # That weird API-like website (try browsing it!)
random_url = base_url + "/random/comic"  # Random page URL
api_url = base_url + "/api-0/jsonp/comic/%s"  # Comic metadata URL
explainxkcd_url = "http://www.explainxkcd.com/%s"

# runtime variables (DO NOT TOUCH)

isrunning = True
seen_comics = []
with urllib.request.urlopen(api_url % "") as response_:
    cur_max_comic = json.loads(response_.read())['num']
sel_comic = cur_max_comic


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
        avail = list(range(1, cur_max_comic))  # List [1, 2, 3, ... last_comic]
        for x in seen_comics:
            avail.remove(x)
        avail.remove(404)  # So much trouble...
        sel = random.choice(avail)  # Magic!
        seen_comics.append(sel)
    else:
        sel = random.randint(1, cur_max_comic)
    sel_comic = sel
    if display_comic:
        command_display()
    if display_comic_image:
        command_display('img')


def command_display(*arguments):
    if len(arguments) > 0:
        try:
            comic = int(arguments[0])
        except ValueError:
            comic = sel_comic
    else:
        comic = sel_comic
    if "img" in arguments:
        if not os.path.exists(tmpimg_location + "%s.png" % sel_comic):
            # If we don't already have the image:
            with urllib.request.urlopen(api_url % comic) as response:
                comic_data = json.loads(response.read())
            img_source = comic_data['img']  # get image path
            with urllib.request.urlopen(img_source) as response:
                if response.getcode() == 404:
                    return "No image for comic found (maybe it's interactive?)"
                else:
                    img_data = response.read()
                    # Does our temp dir exist?
                    if not os.path.isdir(tmpimg_location):
                        os.mkdir(tmpimg_location)  # If not, we create it
                    # We open it for writing
                    fd = open(tmpimg_location + "%s.png" % sel_comic, 'wb')
                    fd.write(img_data)  # We write it
                    fd.close()  # And we close it, just in case
        # Then we display the image
        os.system(display_cmd % (tmpimg_location + "%s.png" % sel_comic))
    else:
        with urllib.request.urlopen(api_url % comic) as response:
            content = response.read()
            if content == "something went wrong":
                return "Error"
            data = json.loads(response.read())
        release_date = (data['year'], data['month'], data['day'])
        transcript = data['transcript']
        if len(transcript) == 0:
            transcript = "No transcript avaliable yet.\n\nTitle text: \"" + \
                         data['alt'] + "\""
        output = data['title'] + "\nRelease date: %s-%s-%s" % release_date + \
            "\n" + transcript
        if use_less:
            proc = Popen("less", shell=True, stdin=PIPE)
            proc.communicate(output.encode())
        else:
            return output


def command_explain(*arguments):
    if len(arguments) < 1:
        comic = sel_comic
    else:
        comic = arguments[0]
    location = explainxkcd_url % comic
    req = urllib.request.Request(location)
    req.add_header("User-Agent", "xkcd/0.1 (by randomdude999 <just.so.you.can."
                                 "email.me@gmail.com>)")
    with urllib.request.urlopen(req) as response:
        content = response.read()
    proc = Popen(html_renderer, shell=True, stdin=PIPE, stdout=PIPE)
    content = proc.communicate(content)[0]
    # *WARNING: ABOMINATION INCOMING* #
    content = "".join(content.decode().split("[edit] ")[1:-1])
    if use_less:
        proc = Popen("less", shell=True, stdin=PIPE)
        proc.communicate(content.encode())
    else:
        return content


def command_save(*arguments):
    if len(arguments) < 1:
        location = save_location + str(sel_comic) + ".png"
    else:
        location = arguments[0]
    output = "Saving comic %s to location %s" % (sel_comic, location) + "\n"
    # If we don't have a cached version, get one
    if not os.path.exists(tmpimg_location + "%s.png" % sel_comic):
        # See previous (display-img) function
        with urllib.request.urlopen(api_url % sel_comic) as response:
            comic_data = json.loads(response.read())
        img_source = comic_data['img']  # get image path
        with urllib.request.urlopen(img_source) as response:
            if response.getcode() == 404:
                return "No image for comic found (maybe it's interactive?)"
            else:
                img_data = response.read()
                # Does our temp dir exist?
                if not os.path.isdir(tmpimg_location):
                    os.mkdir(tmpimg_location)  # If not, we create it
                # We open it for writing
                fd = open(tmpimg_location + "%s.png" % sel_comic, 'wb')
                fd.write(img_data)  # We write it
                fd.close()  # And we close it, just in case
    try:
        # Try to copy the image to the given file
        shutil.copy(tmpimg_location + "%s.png" % sel_comic, location)
    except PermissionError as err:  # We're not allowed to?
        return err  # Tell the user
    return output


def command_next(*arguments):
    global sel_comic
    if len(arguments) < 1:
        amount = 1
    else:
        amount = int(arguments[0])
    sel_comic += amount
    if sel_comic > cur_max_comic:  # That comic does not exist
        sel_comic = cur_max_comic  # But let's give them the last one
    elif sel_comic == 404:  # That one also does not exist
        sel_comic = 405  # So we skip it


def command_prev(*arguments):
    global sel_comic
    if len(arguments) < 1:
        amount = 1
    else:
        amount = int(arguments[0])
    sel_comic -= amount
    if sel_comic < 1:  # We don't have negative comics (yet)
        sel_comic = 1  # Give 'em the first one
    elif sel_comic == 404:  # And the 404 again
        sel_comic = 403  # Skip it


def command_first(*arguments):
    global sel_comic
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command does not accept arguments"
    sel_comic = 1  # What part of this do you not understand?
    return output


def command_last(*arguments):
    global sel_comic
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command does not accept arguments"
    sel_comic = cur_max_comic  # This is kind of like the previous one
    return output


def command_goto(*arguments):
    global sel_comic
    if len(arguments) < 1:
        comic = cur_max_comic
    else:
        comic = int(arguments[0])
    if comic < 1:  # no negative comics!
        comic = 1  # so they get the 1st one
    elif comic > cur_max_comic:  # That comic does not exist
        comic = cur_max_comic  # but the last one does
    elif comic == 404:  # Why does this easter egg cause so much trouble?
        return "404 Not Found"
    sel_comic = comic


def command_update(*arguments):
    global sel_comic, cur_max_comic
    output = ""
    if len(arguments) > 0:
        output += "Warning: Command does not accept arguments\n"
    with urllib.request.urlopen(api_url % "") as response:
        new_max_comic = json.loads(response.read())['num']
    if new_max_comic > cur_max_comic:
        # The current comic is newer than the one we think is the latest one
        if cur_max_comic + 1 == new_max_comic:  # there is exactly 1 new comic
            output += "1 new comic!\n"
        else:  # There is more than 1 comic
            output += "%s new comics!\n" % (new_max_comic - cur_max_comic)
        cur_max_comic = new_max_comic  # Update the latest comic
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


commands = {  # Dict to store commands
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
    "license": command_license
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

commands["help"] = command_help


#  #############################
#  # Main code                 #
#  #############################
sys.stdout.write("\x1b]0;xkcd\x07")
print("A command line xkcd client (%s)" % version)
print("By randomdude999")
print("Type `help' or `license' for more info")

while isrunning:
    try:
        inp = input(prompt % sel_comic)  # what do you want to do?
    except (KeyboardInterrupt, EOFError):
        # Apparently you don't like the program's built-in exit commands
        print()
        break
    cmds = inp.split(";")  # Much simpler than a regex
    for cmd in cmds:
        cmd = cmd.strip()  # Whitespace can mess things up
        args = cmd.split(" ")
        cmd = args.pop(0)  # Arguments != Command name
        if cmd in commands:  # Hey, we found a matching command!
            print(commands[cmd](*args))
        else:  # We did not find a match
            print("Unknown command")

if os.path.exists(tmpimg_location):
    # Don't forget to clean the temporaries, kids!
    shutil.rmtree(tmpimg_location)
