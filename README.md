# A couple Beets plug-ins

These are a couple of plug-ins I wrote for [Beets][], written
primarily for my own use but shared in case anyone else finds them
useful.

[Beets]: http://beets.radbox.org/

## Warning!

These plug-ins have been only lightly tested, by me, in my personal
use.  The `edit` plug-in will probably let you screw things up real
good.  I can't guarantee that these plug-ins will not mess up your
music, or eat music files, or eat every file on your hard drive, or
crash your computer entirely.  Use at your own risk!  (Bug reports
welcome!)

## Installation

`python setup.py` should do the trick.  Note that, as of this writing,
this package requires Beets 1.2.2 (currently unreleased) or later.
I'm running Beets from Git right now.

Once you've installed this package, to use one or both of these
plug-ins you'll need to [configure them in Beets][enable-plugins].

[enable-plugins]: http://beets.readthedocs.org/en/v1.2.1/plugins/index.html#using-plugins

## Plugin: edit

This plug-in lets you edit the Beets fields for one or more MP3 files
at the same time in a text editor of your choice.  This is inspired by
the way you can edit tags for multiple files simultaneously in
[Mp3tag][].

[Mp3tag]: http://www.mp3tag.de/en/

The plug-in adds a `edit` subcommand to Beets:

```
$ beet edit --help
Usage: beet edit [options]

Options:
  -h, --help  show this help message and exit
```

The plug-in's only mandatory argument is a query such as the query you
would supply to the `beet ls` command.  Invoking `beet edit` with such
a pattern dumps the fields (mostly "tags") for the matched file(s)
into a text file, and you are then sent into the editor specified by
your `EDITOR` environment variable to edit that text file.  You can
make your changes to the fields' values, save this text file back out,
exit your editor, and then `edit` apply your changes.

For example, if I invoke `beet edit "./weeknd, the - house of
balloons"`, `edit` invokes Vim (my `EDITOR`) on a file with the
combined fields from every song on this album:

```
# Loft Music
# The Knowing
# House of Balloons / Glass Table Girls
# Coming Down
# The Morning
# The Party & The After Party
# Wicked Games
# What You Need
# High for This
title: <Keep>
artist: The Weeknd
artist_sort: Weeknd, The
artist_credit: The Weeknd
album: House of Balloons
albumartist: The Weeknd
albumartist_sort: Weeknd, The
albumartist_credit: The Weeknd
# ... and so on ...
```

Lines that begin with `#` are comments and will be ignored by `edit`.
All other non-blank lines are the name of a field, followed by a
colon, optional space, and the value for that field.

If you specify the special value `<Keep>` for a field, that field's
value will remain unchanged.

If you edit multiple files, and the files have different values for
the same field, the default value for that field will be the special
value `<Keep>`.  If you leave the value as `<Keep>` then each file
will retain its existing, individual value for this field.  For your
convenience, `edit` also fills in all the different values for this
field across every file you're editing as comments above the field, as
you can see for the `title` field in the above example.

If you are editing multiple files, and you change the value for a
field from `<Keep>` to something else, that new value will be applied
to _every_ file you're editing.  Every file will then have the same
value for that field.

This plug-in also adds a `dump_edit` command.  This command produces
the same text file that `edit` would have you edit, but it just writes
that file's contents to standard output.

## Plugin: moveall

If you activate this plug-in, any time you move every music file out
of one directory and into another with `beet mv`, any files in the old
directory that are not known to Beets will be moved to the new
directory as well.  This is useful when you have files like EAC log
files or README.TXT files for an album that should get moved along
with that album.

If you move files from a single directory into multiple other
directories, this plug-in will take no action; non-Beets files in the
source directory will be left where they are.

If this plug-in moves all of the files out of your old directory, it
will automatically try to remove the old directory as well.  Again,
this is useful when you're moving a complete album in its own
directory, which also contains additional non-music files.

## License

This software is provided under the same license as Beets itself:

The MIT License

Copyright (c) 2013 Dale Sedivec

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
