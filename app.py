from socketclusterclient import Socketcluster
import os
from dataclasses import dataclass
from jinja2 import Template
from typing import List


@dataclass
class Test:
    action: str
    prev_state: str
    next_state: str


@dataclass
class TestGen:
    tests: List[Test]


def remove_files_from(dir_path: str):
    try:
        for file in os.listdir(dir_path):
            if file.endswith(".swift"):
                os.remove(dir_path + file)
    except:
        pass


def render_template(name: str, **kwargs):
    swift_template_file = open("templates/" + name)
    swift_template_text = "".join(swift_template_file.readlines())
    swift_template_file.close()
    swift_source = Template(swift_template_text)
    return swift_source.render(kwargs)


def on_connect(s):
    print("on_connect")
    s.subscribe("log")
    s.onchannel("log", handle_messages)


def on_disconnect(s):
    print("on_disconnect")


def on_connect_error(s, error):
    print("on_connect_error {}", error)


def dispatch_message(key, message):
    if message['type'] == "DISPATCH":
        action = message['action']['type']
        if action == 'COMMIT':
            dir_path = "code_gen"
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            remove_files_from(dir_path)
            test_gen = render_template('tests_template.swift', test_gen=TestGen(tests_data))
            swift_file = open(dir_path + "/ReduxTest.swift", "w")
            swift_file.write(test_gen)
            swift_file.close()
            print("test generated")


def handle_messages(key, message):
    client_id = message['id']
    if len(client_id) > 0:
        channel_id = 'sc-' + client_id
        socket.subscribe(channel_id)
        socket.onchannel(channel_id, dispatch_message)

    if message['type'] == 'ACTION':
        global tests_data

        action = message['action']['payload'].replace('"', '\\"')
        next_state = message['payload'].replace('"', '\\"')
        prev_state = ""

        if len(tests_data) > 0:
            prev_state = tests_data[-1].next_state

        tests_data.append(Test(action, prev_state, next_state))


tests_data = []
socket = Socketcluster.socket("ws://localhost:8000/socketcluster/")
socket.setBasicListener(on_connect, on_disconnect, on_connect_error)
socket.connect()
