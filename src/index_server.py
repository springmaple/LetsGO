import argparse
import inspect
import json

from server import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='quarto', add_help=False)
    parser.add_argument('command', type=str, help='Command to run')
    parser.add_argument('-code', type=str, required=False, default='', help='Company profile code')
    parser.add_argument('-item_code', type=str, required=False, default='', help='Item code')
    parser.add_argument('-file', type=str, required=False, default='', help='File path')
    args = parser.parse_args()

    _command = args.command.lower()

    COMMANDS = {
        "get_profiles": get_profiles,
        "get_items": get_items,
        "get_photo": get_photo,
        "set_photo": set_photo,
    }

    fn = COMMANDS[_command]
    fn_args = [getattr(args, arg_key).lower() for arg_key in inspect.getfullargspec(fn).args]
    result = fn(*fn_args)
    print(json.dumps(result))
