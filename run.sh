#!/usr/bin/env bash

export ANSIBLE_CALLBACKS_ENABLED=indirect_instance_count
export ANSIBLE_LOAD_CALLBACK_PLUGINS=True
export ANSIBLE_CALLBACK_PLUGINS=`pwd`/callback/
ansible-playbook main.yml -vvvv
