import argparse
import inspect
import json
import types

from activity_logs import ActivityLog, ActivityLogMock
from constants import ACTIVITY_LOGS_DIR
from server import *


def open_logs():
    os.system(f'explorer.exe "{ACTIVITY_LOGS_DIR}"')
    return {'status': 'ok'}


def start(log: ActivityLog):
    log = log or ActivityLogMock()

    parser = argparse.ArgumentParser(prog='quarto', add_help=False)
    parser.add_argument('command', type=str, help='Command to run')
    parser.add_argument('-code', type=str, required=False, default='', help='Company profile code')
    parser.add_argument('-item_code', type=str, required=False, default='', help='Item code')
    parser.add_argument('-file', type=str, required=False, default='', help='File path')
    parser.add_argument('-uom_suffix', type=str, required=False, default='', help='UOM suffix for regional UOM')
    parser.add_argument('-uom_areas', type=str, required=False, default='',
                        help='Comma separated area codes for regional UOM')
    args = parser.parse_args()

    _command = args.command.lower()

    COMMANDS = {
        "get_profiles": get_profiles,
        "get_items": get_items,
        "get_photo": get_photo,
        "set_photo": set_photo,
        "delete_photo": delete_photo,
        "sync_sql_acc": sync_sql_acc,
        "get_last_sync_sql_timestamp": get_last_sync_sql_timestamp,
        "get_area_codes": get_area_codes,
        "set_settings_east_malaysia_uom": set_settings_east_malaysia_uom,
        "get_settings_east_malaysia_uom": get_settings_east_malaysia_uom,
        "open_logs": open_logs
    }

    fn = COMMANDS[_command]
    fn_args = [log if arg_key == 'log' else getattr(args, arg_key).lower()
               for arg_key
               in inspect.getfullargspec(fn).args]

    log.i(fn.__name__, fn_args)

    result = fn(*fn_args)
    if isinstance(result, types.GeneratorType):
        for r in result:
            print(json.dumps(r))
    else:
        print(json.dumps(result))


if __name__ == '__main__':
    with ActivityLog() as al:
        try:
            start(al)
        except Exception as ex:
            al.e(ex)
            raise
