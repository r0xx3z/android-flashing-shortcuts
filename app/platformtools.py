import os
import sys
import shutil

# Names of the tools we ever call. Kept here so callers don't hardcode them.
TOOLS = ("adb", "fastboot")


def platform_tools_dir(curdir):
    return os.path.join(curdir, "assets", "platform-tools")


def resolve_tool(curdir, name):
    """
    Figures out the actual path to use for `name` (e.g. "adb").

    Order of preference:
    1. The binary bundled in assets/platform-tools for the current OS
       (adb.exe on Windows, adb with no extension elsewhere).
    2. Whatever is on the user's PATH (handy on Linux distros that ship
       android-tools via their package manager).
    3. The bare name, so Qt still tries and the user gets a normal
       "not found" error instead of a silent crash.
    """
    bundled_name = name + ".exe" if sys.platform.startswith("win") else name
    bundled = os.path.join(platform_tools_dir(curdir), bundled_name)

    if os.path.isfile(bundled):
        if not sys.platform.startswith("win") and not os.access(bundled, os.X_OK):
            # zip/git extraction on Linux often drops the executable bit
            try:
                os.chmod(bundled, 0o755)
            except OSError:
                pass
        return bundled

    on_path = shutil.which(name)
    if on_path:
        return on_path

    return name


def resolve_command(curdir, command):
    """
    Takes a command string like 'adb shell cmd package list packages -3'
    and swaps the leading tool name for its resolved path, quoting it in
    case it contains spaces (common on Linux home directories).
    """
    tool, _, rest = command.partition(" ")
    resolved = resolve_tool(curdir, tool)
    return f'"{resolved}" {rest}' if rest else f'"{resolved}"'
