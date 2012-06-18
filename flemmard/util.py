import sys
import signal
import subprocess


class TimeoutError(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutError("The call has taken too long")


def with_timer(duration, cleanup=None):
    def _timer(func):
        def __timer(*args, **kw):
            previous_sig = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(duration)
            try:
                return func(*args, **kw)
            except TimeoutError:
                if cleanup is not None:
                    cleanup()
                raise
            finally:
                # replace the previous sig
                signal.signal(signal.SIGALRM, previous_sig)
        return __timer
    return _timer


def run(command, timeout=300, verbose=False, allow_exit=False):
    err_output = []
    out_output = []

    def _output():
        out = 'Output:\n:%s' % '\n'.join(out_output)
        err = '\n\nErrors:\n:%s' % '\n'.join(err_output)
        return out + err

    @with_timer(timeout)
    def _run():
        if verbose:
            print('\n' + command)

        sb = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE)

        stdout, stderr = sb.communicate()
        code = sb.returncode

        if code != 0:
            if not allow_exit or verbose:
                print("%r failed with code %d" % (command, code))
                print(stdout)
                print(stderr)
            if not allow_exit:
                sys.exit(code)
        elif verbose:
            print(stdout)
            print(stderr)

        return code, stdout, stderr

    try:
        return  _run()
    except TimeoutError:
        print(command)
        print("Timed out!")
        sys.exit(0)


def resolve_name(name):
    """Resolve a name like ``module.object`` to an object and return it.

    This functions supports packages and attributes without depth limitation:
    ``package.package.module.class.class.function.attr`` is valid input.
    However, looking up builtins is not directly supported: use
    ``__builtin__.name``.

    Raises ImportError if importing the module fails or if one requested
    attribute is not found.
    """
    if '.' not in name:
        # shortcut
        __import__(name)
        return sys.modules[name]

    # FIXME clean up this code!
    parts = name.split('.')
    cursor = len(parts)
    module_name = parts[:cursor]
    ret = ''

    while cursor > 0:
        try:
            ret = __import__('.'.join(module_name))
            break
        except ImportError:
            cursor -= 1
            module_name = parts[:cursor]

    if ret == '':
        raise ImportError(parts[0])

    for part in parts[1:]:
        try:
            ret = getattr(ret, part)
        except AttributeError, exc:
            raise ImportError(exc)

    return ret
