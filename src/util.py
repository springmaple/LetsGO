import os


def get_self_dir():
    this_file = os.path.abspath(__file__)
    return os.path.dirname(this_file)


def find_file(file: str):
    abs_dir = self_dir = get_self_dir()
    intended_file = os.path.join(self_dir, file)
    while not os.path.exists(intended_file):
        tmp_dir = os.path.dirname(abs_dir)
        if tmp_dir == abs_dir:
            raise Exception('failed to find file ' + file)
        abs_dir = tmp_dir
        intended_file = os.path.join(abs_dir, file)

    return os.path.abspath(intended_file)


def esc_key(key: str):
    return key.replace('/', '_')
