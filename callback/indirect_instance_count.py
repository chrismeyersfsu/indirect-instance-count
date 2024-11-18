# (C) 2012, Michael DeHaan, <michael.dehaan@gmail.com>
# (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import yaml
import jq

DOCUMENTATION = '''
    callback: log_plays
    type: notification
    short_description: write playbook output to log file
    version_added: historical
    description:
      - This callback writes playbook output to a file per host in the `/var/log/ansible/hosts` directory
      - "TODO: make this configurable"
    requirements:
     - Whitelist in configuration
     - A writeable /var/log/ansible/hosts directory by the user executing Ansible on the controller
'''

import os
import time
import json
from collections.abc import MutableMapping

from ansible.module_utils._text import to_bytes
from ansible.plugins.callback import CallbackBase


# NOTE: in Ansible 1.2 or later general logging is available without
# this plugin, just set ANSIBLE_LOG_PATH as an environment variable
# or log_path in the DEFAULTS section of your ansible configuration
# file.  This callback is an example of per hosts logging for those
# that want it.


# Taken from https://github.com/ansible/ansible/blob/devel/lib/ansible/cli/galaxy.py#L1624

from ansible.cli.galaxy import with_collection_artifacts_manager

from ansible.galaxy.collection import (
    find_existing_collections,
)
from ansible.utils.collection_loader import AnsibleCollectionConfig
import ansible.constants as C



@with_collection_artifacts_manager
def list_collections(namespace, collection, artifacts_manager=None):
    artifacts_manager.require_build_metadata = False

    default_collections_path = set(C.COLLECTIONS_PATHS)
    collections_search_paths = (
        default_collections_path | set(AnsibleCollectionConfig.collection_paths)
    )
    collections = list(find_existing_collections(
        list(collections_search_paths),
        artifacts_manager,
        namespace_filter=namespace,
        collection_filter=collection,
        dedupe=False
    ))
    return collections


class CallbackModule(CallbackBase):
    """
    logs playbook results, per host, in /var/log/ansible/hosts
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'indirect_instance_count'
    CALLBACK_NEEDS_WHITELIST = True

    TIME_FORMAT = "%b %d %Y %H:%M:%S"
    MSG_FORMAT = "%(now)s - %(category)s - %(data)s\n\n"

    def __init__(self):

        super(CallbackModule, self).__init__()

        if not os.path.exists("/home/cmeyers/Scratch/indirect-instance-count/hosts"):
            os.makedirs("/home/cmeyers/Scratch/indirect-instance-count/hosts")

    def log(self, host, category, data):
        if isinstance(data, MutableMapping):
            if '_ansible_verbose_override' in data:
                # avoid logging extraneous data
                data = 'omitted'
            else:
                data = data.copy()
                invocation = data.pop('invocation', None)
                data = json.dumps(data)
                if invocation is not None:
                    data = json.dumps(invocation) + " => %s " % data

        path = os.path.join("/home/cmeyers/Scratch/indirect-instance-count/hosts", host)
        now = time.strftime(self.TIME_FORMAT, time.localtime())

        namespace, collection, module = self.task.resolved_action.split('.')
        collection_path = list_collections(namespace, collection)[0][2].decode('utf-8')

        with open(f"{collection_path}/meta/event_counting.yml") as f:
            queries = yaml.safe_load(f)

        d_dict = json.loads(data)
        msg = f"Queries for module {namespace}.{collection}.{module}:\n"
        for k, v in queries.items():
            msg += f"\t{k} = {v}\n"

            v_str = v['query']
            result = jq.compile(v_str).input(d_dict).first()
            msg += f"\tResult: {result}\n"

        msg = to_bytes(msg)
        with open(path, "ab") as fd:
            fd.write(msg)

    def runner_on_failed(self, host, res, ignore_errors=False):
        self.log(host, 'FAILED', res)

    def runner_on_ok(self, host, res):
        self.log(host, 'OK', res)

    def runner_on_skipped(self, host, item=None):
        self.log(host, 'SKIPPED', '...')

    def runner_on_unreachable(self, host, res):
        self.log(host, 'UNREACHABLE', res)

    def runner_on_async_failed(self, host, res, jid):
        self.log(host, 'ASYNC_FAILED', res)

    def playbook_on_import_for_host(self, host, imported_file):
        self.log(host, 'IMPORTED', imported_file)

    def playbook_on_not_import_for_host(self, host, missing_file):
        self.log(host, 'NOTIMPORTED', missing_file)

    def v2_playbook_on_play_start(self, play):
        self.play = play

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.task = task
