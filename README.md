# indirect-instance-count
Ansible callback plugin to count events that we care about.

# Quickstart

```
pip install jq
./run.sh
cat hosts/*
Queries for module foo.bar.baz:
        foo.bar.baz = {'query': '[.my_children | .[] | select(.changed == true)] | length', 'category': 'children'}
        Result: 1
```


```
.
├── callback
│   ├── indirect_instance_count.py           <--- query discovered and executed here
├── collections
│   └── ansible_collections
│       └── foo
│           └── bar
│               ├── docs
│               ├── galaxy.yml
│               ├── meta
│               │   ├── event_counting.yml   <--- query lives here
│               │   └── runtime.yml
│               ├── plugins
│               │   ├── action
│               │   │   ├── baz.py
│               │   │   └── __pycache__
│               │   │       └── baz.cpython-312.pyc
│               │   └── README.md
│               ├── README.md
│               └── roles
├── hosts
│   └── cmeyers-thinkpadt14sgen2i.durham.csb <--- query result lives here
├── main.yml
├── README.md
└── run.sh

```
