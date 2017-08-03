#!/usr/bin/env python3


class netJson:
    """A JSON object that keeps track of the subnet IP space, number of hosts,
       and breakdown of roles"""

    def __init__(self, start_ip=None, netmask=None, hosts=0, roles=None, domain=None):
        self.start_ip = start_ip
        self.netmask = netmask
        self.host_count = hosts
        self.roles = roles
        self.domain = domain

    def get(self):
        a = {
            'start_ip': self.start_ip,
            'netmask': self.netmask,
            'hosts': self.host_count,
            'roles': self.roles
        }
        if self.domain is not None:
            a['domain'] = self.domain

        return a
