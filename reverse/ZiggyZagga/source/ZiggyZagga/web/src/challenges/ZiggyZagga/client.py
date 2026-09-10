"""
You can use https://github.com/TCP1P/Mobile-POC-Tester to simulate server behaviour
"""
from time import sleep
from type import Status, Queue

from utils import *

import uuid

MAIN_PACKAGE_NAME ="com.cybreak.ziggyzagga"
PROCESS_TIMEOUT = 5*60

FLAG = "flag.png"

def callback(package_name: str, q: Queue):
    q.status = Status.RUNNING_PROOF_OF_CONCEPT

    out, _ = run_adb(['shell', 'dumpsys', 'package', MAIN_PACKAGE_NAME])
    app_uid = re.search(r"userId=(.+)", out).group(1)

    run_adb(['shell', 'mkdir', '-p', f'/data/data/{MAIN_PACKAGE_NAME}/files/'])
    run_adb(['shell', 'chmod', '770', f'/data/data/{MAIN_PACKAGE_NAME}/files/'])

    run_adb(['push', 'challenges/ZiggyZagga/flag/flag.png', f'/data/data/{MAIN_PACKAGE_NAME}/files/{FLAG}'])
    run_adb(['shell', 'chmod', '770', f'/data/data/{MAIN_PACKAGE_NAME}/files/{FLAG}'])
    run_adb(['shell', 'mkdir', '-p', f'/data/data/{MAIN_PACKAGE_NAME}/databases/'])
    run_adb(['push', 'challenges/ZiggyZagga/db/ziggydb.db', f'/data/data/{MAIN_PACKAGE_NAME}/databases/ziggydb.db'])
    run_adb(['shell', 'chmod', '770', f'/data/data/{MAIN_PACKAGE_NAME}/databases/ziggydb.db'])

    run_adb(['shell', 'chown', '-R', f'{app_uid}:{app_uid}', f'/data/data/{MAIN_PACKAGE_NAME}/files'])  
    run_adb(['shell', 'chown', '-R', f'{app_uid}:{app_uid}', f'/data/data/{MAIN_PACKAGE_NAME}/databases'])  

    sleep(2)

    start_app(package_name)

    sleep(10)