#!/usr/bin/make
PROGNAME=xkcd
PREFIX=/usr/local
INSTALL=$(PREFIX)/bin/$(PROGNAME)
FILEDIR=$(PREFIX)/share/$(PROGNAME)

search:
	mkdir -p $(FILEDIR)
	unzip search.zip -d $(FILEDIR)

install:
	install xkcd.py $(INSTALL)

all: search install

clean:
	-rm -r $(INSTALL) $(FILEDIR)
