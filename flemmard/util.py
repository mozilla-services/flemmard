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
