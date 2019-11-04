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


def is_last_modified_not_empty(last_modified):
    return last_modified is not None and last_modified > 0


def resize_image(width, height, max_size=800):
    x, y, is_swap = (width, height, False) if width > height else (height, width, True)
    if x > max_size:
        ratio = max_size // width
        x = max_size
        y = int(y * ratio)
        width, height = (x, y) if not is_swap else (y, x)
    return width, height
