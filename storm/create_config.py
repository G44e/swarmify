#!/usr/bin/env python3

import socket
import time
import yaml
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

def config_values(get, zookeeper_ips, nimbus_ips):
    return {
        'storm.local.dir': get('STORM_DATA_DIR'),
        'storm.log.dir': get('STORM_DATA_LOG_DIR'),
        'storm.zookeeper.servers': zookeeper_ips,
        'nimbus.seeds': nimbus_ips
    }

def write_storm_config(file_path, **kwargs):
    with open(file_path, 'w') as f:
        yaml.dump(kwargs, stream = f)
    print('%s written.' % (file_path))

def get_from_env(name):
    def complain():
        raise Exception("Need %s in environment" % (name,))
    return os.getenv(name) or complain()

def create_config():
    zookeeper_name = get_from_env('STORM_ZOOKEEPER_NAME')
    zookeeper_ips = wait_for_ips(['tasks.' + zookeeper_name, zookeeper_name], int(os.getenv("STORM_ZOOKEEPER_COUNT","1")))
    if zookeeper_ips == None:
        print('Give up.')
        exit(1)

    nimbus_name = get_from_env('STORM_NIMBUS_NAME')
    nimbus_ips = wait_for_ips(['tasks.' + nimbus_name, nimbus_name], int(os.getenv("STORM_NIMBUS_COUNT","1")))
    if nimbus_ips == None:
        print('Give up.')
        exit(1)

    write_storm_config(get_from_env('STORM_CONF_DIR') + '/storm.yaml', **config_values(os.getenv, zookeeper_ips, nimbus_ips))

if __name__ == '__main__':
    create_config()
