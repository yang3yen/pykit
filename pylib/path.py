#! -*- coding: utf-8 -*-


import os
import re


__all__ = ['splitext', 'joinext', 'list_dir']


def splitext(path):
    """Get the extension from a path"""
    root, ext = os.path.splitext(path)
    return (root, ext) if not ext else (root, ext[1:])


def joinext(name, ext, sep='.'):
    """
    >>> joinext('a', 'txt')
    'a.txt'
    """
    return sep.join([name, ext])


def list_dir(root, file_type='f', pattern=None, path=True, recursive=True):
    """
    @root: root dir
    @file_type: file type,
        'f' --> general file,
        'd' --> dir,
        'a' --> file and dir
    @pattern: search pattern
    @path: if True, return path else name
    @recursive: if recursive is True, list files or subdirs recursively
    Return a generator of subdirs or files
    """
    for dirpath, subdirs, filenames in os.walk(root):
        subs = []
        if file_type == 'f':
            subs = filenames
        elif file_type == 'd':
            subs = subdirs
        elif file_type == 'a':
            subs.extend(subdirs)
            subs.extend(filenames)
        else:
            break
        # dirname or filename filter
        for sub in subs:
            _sub = os.path.join(dirpath, sub)
            if pattern is not None:
                if re.search(pattern, _sub) is None:
                    continue
            if path:
                # abspath
                yield os.path.abspath(_sub)
            else:
                # name
                yield sub
        # recursive
        if not recursive:
            break


if __name__ == '__main__':
    pass
