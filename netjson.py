#!/usr/bin/env python3


class netJson:
    """A JSON object that keeps track of the subnet IP space, number of hosts,
       and breakdown of roles"""

    def __init__(self, start_ip=None, hosts=0, roles=None):
        self.start_ip = start_ip
        self.host_count = hosts
        self.roles = roles

    def get(self):
        return {
            'start_ip': self.start_ip,
            'hosts': self.host_count,
            'roles': self.roles
        }
