import argparse
import inspect
import json
import types

from constants import ACTIVITY_LOGS_DIR
from server import *


def open_logs():
    os.system(f'explorer.exe "{ACTIVITY_LOGS_DIR}"')
    return {'status': 'ok'}


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
        "delete_photo": delete_photo,
        "sync_sql_acc": sync_sql_acc,
        "open_logs": open_logs
    }

    fn = COMMANDS[_command]
    fn_args = [getattr(args, arg_key).lower() for arg_key in inspect.getfullargspec(fn).args]

    result = fn(*fn_args)
    if isinstance(result, types.GeneratorType):
        for r in result:
            print(json.dumps(r))
    else:
        print(json.dumps(result))
