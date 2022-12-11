import os
import sys

if sys.platform == "win32":
    from ctypes import WinDLL, c_bool
else:
    WinDLL = None
    c_bool = None


def load_file_contents(path: str, strip: bool = True) -> str:
    path = convert_path(path)
    with open(path, "rb") as handle:
        to_return = handle.read().decode("utf-8")

    if strip:
        to_return = to_return.strip()

    return to_return


def convert_path(path: str) -> str:
    """Convert a path which might be >260 characters long, to one
    that will be writable/readable on Windows.
    On other platforms, this is a no-op.
    """
    # some parts of python seem to append '\*.*' to strings, better safe than
    # sorry.
    if len(path) < 250:
        return path
    if _supports_long_paths():
        return path

    prefix = "\\\\?\\"
    # Nothing to do
    if path.startswith(prefix):
        return path

    path = _win_prepare_path(path)

    # add the prefix. The check is just in case os.getcwd() does something
    # unexpected - I believe this if-state should always be True though!
    if not path.startswith(prefix):
        path = prefix + path
    return path


def _supports_long_paths() -> bool:
    if sys.platform != "win32":
        return True
    # Eryk Sun says to use `WinDLL('ntdll')` instead of `windll.ntdll` because
    # of pointer caching in a comment here:
    # https://stackoverflow.com/a/35097999/11262881
    # I don't know exaclty what he means, but I am inclined to believe him as
    # he's pretty active on Python windows bugs!
    else:
        try:
            dll = WinDLL("ntdll")
        except OSError:  # I don't think this happens? you need ntdll to run python
            return False
        # not all windows versions have it at all
        if not hasattr(dll, "RtlAreLongPathsEnabled"):
            return False
        # tell windows we want to get back a single unsigned byte (a bool).
        dll.RtlAreLongPathsEnabled.restype = c_bool
        return dll.RtlAreLongPathsEnabled()


def _win_prepare_path(path: str) -> str:
    """Given a windows path, prepare it for use by making sure it is absolute
    and normalized.
    """
    path = os.path.normpath(path)

    # if a path starts with '\', splitdrive() on it will return '' for the
    # drive, but the prefix requires a drive letter. So let's add the drive
    # letter back in.
    # Unless it starts with '\\'. In that case, the path is a UNC mount point
    # and splitdrive will be fine.
    if not path.startswith("\\\\") and path.startswith("\\"):
        curdrive = os.path.splitdrive(os.getcwd())[0]
        path = curdrive + path

    # now our path is either an absolute UNC path or relative to the current
    # directory. If it's relative, we need to make it absolute or the prefix
    # won't work. `ntpath.abspath` allegedly doesn't always play nice with long
    # paths, so do this instead.
    if not os.path.splitdrive(path)[0]:
        path = os.path.join(os.getcwd(), path)

    return path
