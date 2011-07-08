# Utilities #

This repository is a dumping ground of one-off utilities I develop that
might be useful to others.  Technically, each should have its own
repository, but they are so unimportant that I can't justify the overhead
of creating a new repository.

## clatex ##

This is just a command line latex interpreter that produces a graphical
latex-ified version of the input.

    usage: ./clatex.py [-s FONTSIZE] "<mathmode commands>"

This will produce a PNG called "clatex.png" (overwriting previous
versions).  It assumes `latex` and `dvipng` are in your `PATH`.

## woot ##

Scrape the Woot! page and display the current product and some information
about it.  Leave it running and it checks every hour for a new product.
During a Woot!-off the polling period is reduces to 5 seconds.  They
probably have an API that does this much more nicely, but I wrote this a
while ago.

    usage: ./woot.py

## cpuinfo-viz ##

This reads and processes `/proc/cpuinfo` on Linux systems and displays how
every processor id is assigned to physical cores and processors.  If you
have symmetric multithreading it identifies the threads on each core.

    usage: ./cpuinfo-viz.py --viz /proc/cpuinfo
