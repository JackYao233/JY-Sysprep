"""Windowless worker entry: never initialize the GUI or a console wizard."""
import sys


def power_action(action):
    from sysprep.executor import complete_power_action
    complete_power_action(action)


def run():
    if sys.argv[1:] != ["--admin-deployment-worker"]:
        return 2
    sys._jy_windowless_worker = True
    from sysprep.admin_job import worker_main
    return worker_main(power_action=power_action)


if __name__ == "__main__":
    sys.exit(run())
