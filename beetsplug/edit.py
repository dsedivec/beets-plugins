import tempfile
import os
import subprocess
import re
import sys
import codecs
import locale
import shlex

from beets import plugins, ui, library
from beets.ui import commands


KEEP = "<Keep>"
FIELDS = [field for field in library.ITEM_KEYS_WRITABLE
          # https://github.com/sampsyo/beets/issues/248
          if not re.search(r"^rg_(track|album)_(gain|peak)$", field)]


def _do_query(lib, args):
    return commands._do_query(lib, ui.decargs(args), False)[0]


def _write_analysis(items, output_file):
    # It seems like some keys get None and others get empty string?
    # Empty string seems to be much more prevalent, so we'll
    # standardize on that.
    shared_values = {key: getattr(items[0], key, "") or "" for key in FIELDS}
    differing_values = {}
    for item in items[1:]:
        for key in FIELDS:
            value = getattr(item, key, "") or ""
            if key not in differing_values:
                shared_value = shared_values[key]
                if value != shared_value:
                    del shared_values[key]
                    differing_values[key] = set((shared_value, value))
            else:
                differing_values[key].add(value)
    for key in FIELDS:
        values = differing_values.get(key, ())
        for value in values:
            output_file.write("# %s\n" % (value,))
        output_file.write("%s: %s\n" % (key, shared_values.get(key, KEEP)))


dump_edit_cmd = ui.Subcommand("dump_edit", help=("dump the file you would edit"
                                                 " with the edit command"))
def dump_edit(lib, _opts, args):
    items = _do_query(lib, args)
    if len(items) < 1:
        raise Exception("query didn't match any items")
    _write_analysis(items, sys.stdout)
dump_edit_cmd.func = dump_edit


edit_cmd = ui.Subcommand("edit", help="edit tags")
# edit_cmd.parser.add_option('-a', '--album', action='store_true',
#                            help='modify whole albums instead of tracks')
def edit(lib, _opts, args):
    editor = os.environ.get("EDITOR")
    if not editor:
        raise Exception("you must set EDITOR in your environment")
    editor_command = shlex.split(editor)
    items = _do_query(lib, args)
    if len(items) < 1:
        raise Exception("query didn't match any items")
    temp_file = tempfile.NamedTemporaryFile()
    encoding = locale.getpreferredencoding()
    StreamWriter = codecs.getwriter(encoding)
    _write_analysis(items, StreamWriter(temp_file))
    temp_file.flush()
    editor_command.append(temp_file.name)
    subprocess.check_call(editor_command)
    temp_file.seek(0)
    new_values = {}
    print "=== new values for fields ==="
    for line in codecs.iterdecode(temp_file, encoding):
        line = line.strip()
        if line and not line.startswith("#"):
            parts = re.split(r"\s*:\s*", line, 1)
            if len(parts) != 2:
                raise Exception("can't understand %r" % (line,))
            key, new_value = parts
            if key not in FIELDS:
                raise Exception("unknown field %r in %r" % (key, line))
            elif new_value.lower() != KEEP.lower():
                new_values[key] = new_value
                print "%s: %s" % (key, new_value)
    if not new_values:
        print "nothing to write"
    else:
        with lib.transaction():
            for item in items:
                for key, value in new_values.iteritems():
                    setattr(item, key, value)
                lib.store(item)
        for item in items:
            print "writing tags to %s" % (item.path,)
            item.write()
edit_cmd.func = edit


class Plugin (plugins.BeetsPlugin):
    def commands(self):
        return [dump_edit_cmd, edit_cmd]
