import os.path
import os
import shutil
import logging

from beets import plugins, library, util


log = logging.getLogger("beets")


class MoveAllPlugin (plugins.BeetsPlugin):
    pass


MULTIPLE_DESTS = object()
directories_moved = {}


@MoveAllPlugin.listen("item_moved")
def handle_item_moved(source, destination, **_kwargs):
    global directories_moved
    src_dir = os.path.dirname(source)
    existing_dst_dir = directories_moved.get(src_dir)
    if existing_dst_dir is MULTIPLE_DESTS:
        return
    dst_dir = os.path.dirname(destination)
    if existing_dst_dir:
        if not os.path.samefile(dst_dir, existing_dst_dir):
            directories_moved[src_dir] = MULTIPLE_DESTS
    elif not os.path.samefile(src_dir, dst_dir):
        directories_moved[src_dir] = dst_dir


@MoveAllPlugin.listen("cli_exit")
def handle_cli_exit(lib, **_kwargs):
    for src_dir, dst_dir in directories_moved.iteritems():
        if dst_dir is MULTIPLE_DESTS:
            print ("moves out of %s have multiple dests, will not moveall" %
                   (src_dir,))
            continue
        remaining_items = lib.items(library.PathQuery(src_dir))
        if next(iter(remaining_items), None):
            print "some Beets items left in %s, will not moveall" % (src_dir,)
        else:
            print "moving all leftovers in %s to %s" % (src_dir, dst_dir)
            for dirent in os.listdir(src_dir):
                dirent_path = os.path.join(src_dir, dirent)
                try:
                    shutil.move(dirent_path, dst_dir)
                except shutil.Error, ex:
                    # Log it but move on.
                    log.critical("failed to move %r to %r: %s", dirent_path,
                                 dst_dir, ex)
            util.prune_dirs(src_dir)
