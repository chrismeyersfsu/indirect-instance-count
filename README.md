# indirect-instance-count
Ansible callback plugin to count events that we care about.

# Quickstart

```
./run.sh
cat hosts/*
Queries for module foo.bar.baz:
        foo.bar.baz = {'query': '[.my_children | .[] | select(.changed == true)] | length', 'category': 'children'}
        Result: 1
```
