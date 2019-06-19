import subprocess
import os


class SqlScript:
    def __init__(self, script_name):
        self._script_name = script_name

    def _get_script_path(self):
        script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        return os.path.join(script_dir, self._script_name + '.vbs')

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        return

    def __iter__(self):
        self._proc = subprocess.Popen(['cscript', self._get_script_path()], stdout=subprocess.PIPE)
        return self

    def __next__(self):
        line = self._proc.stdout.readline()
        if line:
            return line
        raise StopIteration
