#!/usr/bin/env python3

import socket
import time
import re
import string
import os


def find_ips(name):
    return [ai[4][0] for ai in
        socket.getaddrinfo(name, None, family = socket.AddressFamily.AF_INET, type = socket.SocketKind.SOCK_STREAM)]

def wait_for_ips(service_names, instance_count = 1):
    for i in range(10):
        wait_seconds = 3
        for name in service_names:
            try:
                ips = find_ips(name)
                break
            except socket.gaierror as e:
                print('Lookup %s: %s.' % (name, e))
                ips = None
        else:
            print('Wait %s seconds.' % (wait_seconds,))
            time.sleep(wait_seconds)
            continue
        if len(ips) == instance_count:
            break
        else:
            print('Expected %s IPs, but got %s. Wait %s seconds.' % (instance_count, len(ips), wait_seconds))
            time.sleep(wait_seconds)
    else:
        print('Could not find %s IPs after 10 attempts.' % (instance_count,))
        return None
    return ips

def split_ip(ip):
    """
    >>> split_ip('127.0.0.1')
    [127, 0, 0, 1]
    """
    return [int(p) for p in re.match(r"(\d+)\.(\d+)\.(\d+)\.(\d+)$", ip).groups()]

def sort_ips(ips):
    """
    >>> sort_ips(['127.0.0.10','127.0.0.9','128.0.0.0'])
    ['127.0.0.9', '127.0.0.10', '128.0.0.0']
    """
    sips = [(ip, split_ip(ip)) for ip in ips]
    sips.sort(key = lambda x: x[1])
    return [p[0] for p in sips]

def config_values(get, ips):
    """
    >>> config_values(lambda x: x + '_VALUE', ['hello', 'world'])
    {'clientPort': 'ZOO_PORT_VALUE', 'dataDir': 'ZOO_DATA_DIR_VALUE', 'dataLogDir': 'ZOO_DATA_LOG_DIR_VALUE', 'tickTime': 'ZOO_TICK_TIME_VALUE', 'initLimit': 'ZOO_INIT_LIMIT_VALUE', 'syncLimit': 'ZOO_SYNC_LIMIT_VALUE', 'server.1': 'hello:2888:3888', 'server.2': 'world:2888:3888'}
    """
    config_items = [
        ("clientPort", "ZOO_PORT"),
        ("dataDir", "ZOO_DATA_DIR"),
        ("dataLogDir", "ZOO_DATA_LOG_DIR"),
        ("tickTime", "ZOO_TICK_TIME"),
        ("initLimit", "ZOO_INIT_LIMIT"),
        ("syncLimit", "ZOO_SYNC_LIMIT")]
    m = dict((k, get(v)) for k, v in config_items)
    m.update(("server.%s" % (n + 1,), "%s:2888:3888" % (ip,)) for n, ip in enumerate(ips))
    return m

def write_zk_config(file_path, **kwargs):
    with open(file_path, 'w') as f:
        for kv in kwargs.items():
            f.write("%s=%s\n" % kv)
    print('%s written.' % (file_path))

def write_my_id(file_path, id):
    with open(file_path, 'w') as f:
        f.write(str(id))
    print('%s written.' % (file_path))

def create_config():
    lookup_name = os.getenv('ZOO_SERVER_NAME')

    ips = wait_for_ips(['tasks.' + lookup_name, lookup_name], int(os.getenv('ZOO_SERVER_COUNT')))

    if ips == None:
        print('Give up.')
        exit(1)

    ips = sort_ips(ips)
    print('Found IPs: %s' % (ips,))

    my_ip = find_ips(socket.gethostname())[0]
    my_index = ips.index(my_ip) + 1
    print('My IP: %s, index: %s' % (my_ip, my_index))

    names = [socket.gethostbyaddr(ip)[0] for ip in ips]
    print('Found names: %s' % (names,))

    write_zk_config(os.getenv('ZOO_CONF_DIR') + '/zoo.cfg', **config_values(os.getenv, ips))
    write_my_id(os.getenv('ZOO_DATA_DIR') + '/myid', my_index)

if __name__ == '__main__':
    create_config()
