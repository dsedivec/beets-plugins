import tempfile
import os
import subprocess
import re
import sys
import codecs
import locale
import shlex

from beets import plugins, ui, library


KEEP = "<Keep>"
# Fields that probably really shouldn't be changed by the user.
READ_ONLY_FIELDS = set(["id", "path"])

def _get_fields(only_writable):
    # I have seen it suggested that this is currently the thing to do.
    # Notably you cannot use library.MediaFile.fields(), which returns
    # fields that don't exist on Items such as "date", or so I've
    # decided based on experimental evidence.
    return [field for field in library.Item._fields.keys()
            if not only_writable or field not in READ_ONLY_FIELDS]


def _do_query(lib, args):
    items = list(lib.items(ui.decargs(args)))
    if not items:
        raise ui.UserError('No matching items found.')
    return items


def _write_analysis(items, output_file, for_edit):
    # It seems like some keys get None and others get empty string?
    # We'll just output empty strings for None, and translate
    # everything back to None when we read it back in.
    fields = _get_fields(for_edit)
    shared_values = {key: getattr(items[0], key, "") or "" for key in fields}
    differing_values = {}
    for item in items[1:]:
        for key in fields:
            value = getattr(item, key, "") or ""
            if key not in differing_values:
                shared_value = shared_values[key]
                if value != shared_value:
                    del shared_values[key]
                    differing_values[key] = set((shared_value, value))
            else:
                differing_values[key].add(value)
    for key in fields:
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
    _write_analysis(items, sys.stdout, False)
dump_edit_cmd.func = dump_edit


edit_cmd = ui.Subcommand("edit", help="edit tags")
# edit_cmd.parser.add_option('-a', '--album', action='store_true',
#                            help='modify whole albums instead of tracks')
edit_cmd.parser.add_option("-n", "--dry-run", default=False,
                           action="store_true",
                           help="don't actually modify the database or files")
def edit(lib, opts, args):
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
    _write_analysis(items, StreamWriter(temp_file), True)
    temp_file.flush()
    editor_command.append(temp_file.name)
    subprocess.check_call(editor_command)
    temp_file.seek(0)
    all_fields = _get_fields(True)
    new_values = {}
    for line in codecs.iterdecode(temp_file, encoding):
        line = line.strip()
        if line.startswith("#"):
            continue
        parts = re.split(r"\s*:\s*", line, 1)
        if len(parts) != 2:
            raise Exception("can't understand %r" % (line,))
        key, new_value_str = parts
        if key not in all_fields:
            raise Exception("unknown field %r in %r" % (key, line))
        elif not new_value_str:
            # We use None instead of an empty string everywhere
            # because some fields (e.g. the "date" field, a DateField)
            # chokes on "".
            new_values[key] = None
        elif new_value_str.lower() != KEEP.lower():
            new_values[key] = library.Item._parse(key, new_value_str)
    with lib.transaction():
        for item in items:
            for key, value in new_values.iteritems():
                item[key] = value
            changed = ui.show_model_changes(item)
            if changed and not opts.dry_run:
                item.store()
    if not opts.dry_run:
        print "writing tags"
        for item in items:
            item.try_write()
edit_cmd.func = edit


class Plugin(plugins.BeetsPlugin):
    def commands(self):
        return [dump_edit_cmd, edit_cmd]
