#!/usr/bin/make
PROGNAME=xkcd
PREFIX=/usr/local
INSTALL=$(PREFIX)/bin/$(PROGNAME)
FILEDIR=$(PREFIX)/share/$(PROGNAME)

search:
	mkdir -p $(FILEDIR)
	unzip -q search.zip -d $(FILEDIR)

install:
	install -D xkcd.py $(INSTALL)

all: search install

clean:
	-rm -r $(INSTALL) $(FILEDIR)
