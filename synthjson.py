#!/usr/bin/env python3
#
# An interactive script that generates a JSON file profiling synthetic
# enterprise networks.
#
# INTERNAL USE ONLY; i.e., user input validation is nearly non-existent.
#       - achang@iqt.org

import argparse
import ipaddress
import json
import math
import random
import string
import time
import uuid

import netjson



VERBOSE = False

def randstring(size):
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                    for _ in range(size))


def divide(dividend, divisor):
    quotient = math.floor(dividend/divisor)
    remainder = dividend % divisor
    return (quotient, remainder)

# you'll want to make sure that prefix is some string that
# is prefixed by some number.
def generate_ip(prefix):
    if prefix[len(prefix)-1] is not '.':
        prefix = prefix + '.'
    subn = 4 - prefix.count('.')
    if (subn > 0):
        ip = prefix + '.'.join(str(random.randint(1,254)) for _ in range(subn))
    return ip


def generate_uuid():
    return str(uuid.uuid4())


def generate_fqdn(domain=None, subdomains=0):
    if domain is None:
        domain = randstring(random.randint(5,10)) + '.local'
    if subdomains == 0:
        return domain
    else:
        hostname = domain

    while (subdomains > 0):
        hostname = randstring(random.randint(3,5)) + '.' + hostname
        subdomains -= 1
    return hostname


def generate_os_type(ostypes=None):
    if ostypes is None:
        ostypes = [ 'Unknown',
                    'Windows',
                    'Linux',
                    'Mac OS X',
                    'iOS',
                    'Android',
                    'BSD',
                    'Cisco IOS' ]

    return random.choice(ostypes)


def generate_mac():
    mac = ':'.join(str(hex(random.randint(0,15))) + str(hex(random.randint(0,15)))
                   for _ in range(6))
    return mac.replace('0x', '')


def record(records=None):
    records = [ 'p0f',
                'nmap',
                'BCF']
    return random.choice(records)


def calculate_subnets(total, breakdown):
    """Returns number of subnets, given the breakdown; or -1 if breakdown doesn't work."""
    sanity_percent = 0 # if this isn't 100% by the end, we got issues.
    subnets = 0
    for nodep, netp in breakdown:
        sanity_percent += nodep
        if (sanity_percent > 100):
            return -1
        subtotal = int(total * .01 * nodep)
        groupby = int(254 * .01 *netp)
        subnets += math.ceil(subtotal/groupby)
    if (sanity_percent < 100):
        return -1
    return subnets


def get_default_dev_distro(nodect, printout=True):
    """Prints device type breakdowns using default ratios and returns a count of each device."""
    print("Default Device Role Distribution for {} nodes".format(nodect))
    dev_breakdown = {
        'Business workstations': int(math.floor(nodect*.35)),
        'Developer workstations': int(math.floor(nodect*.15)),
        'Smartphones': int(math.floor(nodect*.28)),
        'Printers': int(math.floor(nodect*.03)),
        'Mail servers': int(math.floor(nodect*.01)),
        'File servers': int(math.floor(nodect*.02)),
        'Internal web servers': int(math.floor(nodect*.06)),
        'Database servers': int(math.floor(nodect*.01)),
        'Code repositories': int(math.floor(nodect*.01)),
        'DNS servers': int(math.floor(nodect*.01)),
        'DHCP servers': int(math.floor(nodect*.01)),
        'Active Directory controllers': int(math.floor(nodect*.01)),
        'SSH servers': int(math.floor(nodect*.01)),
        'VOIP phones': 0,
        'PBXes': 0,
        'Unknown': int(math.floor(nodect*.04))
    }
                            # any nodes left over gets put into Unknown
    total = 0
    for key, ct in sorted(dev_breakdown.items()):
        if (printout and key != 'Unknown'):
            print("  {:>30} : {}".format(key, ct))
        total += ct
    if (nodect > total):
        dev_breakdown['Unknown'] += (nodect - total)
    if (printout):
        print("  {:>30} : {}".format('Unknown', dev_breakdown['Unknown']))

    return dev_breakdown


def build_configs(total, net_div, dev_div, domain):
    """Returns a json object of subnet specifications, or None upon error"""
    global VERBOSE
    total_subnets = calculate_subnets(total, net_div)
    i = total_subnets
    if total_subnets < 1:
        if VERBOSE:
            print("WARNING: Could not break down nodes into the requested subnets.")
        return None

    jsons = []
    host_counter = []
    roles = dict.fromkeys(dev_div.keys(), 0)

    for n in net_div:
        nodes = int(total * .01 * n[0])
        grouped_nodes = int(254 * .01 * n[1])
        q,r = divide(nodes, grouped_nodes)
        while q > 0:
            i -= 1
            start_ip = '10.0.{}.1'.format(i)
            jsons.append(netjson.netJson(start_ip=start_ip, hosts=grouped_nodes, roles=roles.copy()))
            host_counter.append(grouped_nodes)
            if VERBOSE:
                print("Initialized subnet {} with {} hosts starting at {}".format(i, grouped_nodes, start_ip))
            q -= 1
        if r > 0:
            i -= 1
            start_ip = '10.0.{}.1'.format(i)
            jsons.append(netjson.netJson(start_ip=start_ip, hosts=r, roles=roles.copy()))
            host_counter.append(r)
            if VERBOSE:
                print("Initialized subnet {} with {} hosts starting at {}".format(i, r, start_ip))

    for dev in dev_div:
        ct = dev_div[dev]
        while ct > 0:
            randomnet = random.randrange(0, total_subnets)
            if host_counter[randomnet] > 0:
                jsons[randomnet].roles[dev] += 1
                host_counter[randomnet] -= 1
                ct -= 1


    return jsons


def main():
    global VERBOSE
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Provide program feedback', action="store_true")
    args = parser.parse_args()
    if args.verbose:
        VERBOSE = True
        print('Turned VERBOSE on')

    outname = '{}.json'.format(time.strftime("%Y%m%d-%H%M%S"))
    outfile = open(outname, 'w')

    print('\n\n\tSYNTHETIC NETWORK NODE GENERATOR\n')
    cont = 'No'
    net_breakdown = [(30,70), (45,20), (25,90)]
    while cont.lower() != 'yes' and cont.lower() != 'y':
        nodect = int(input("How many network nodes? [500]: ") or "500")

                                #  setting subnet breakdown ----------------
        if (nodect > 50):
            print('Default Node distribution of {} nodes across Class C subnets: '.format(nodect))
            print('  30% of the nodes will occupy subnets that are 70% populated')
            print('  45% of the nodes will occupy subnets that are 20% populated')
            print('  25% of the nodes will occupy subnets that are 90% populated')
            print('Total subnets: {}'.format(calculate_subnets(nodect, net_breakdown)))
            set_net = input("Manually set network node distribution? [No]: ") or "No"
        else:
            set_net = "No"
            net_breakdown = [(100, 100)]
            print('Total subnets: 1')

        if (set_net.lower() != 'no' and set_net.lower() != 'n'):
            net_breakdown = []
            percent = 100
            print("Please enter what percentage of the {} nodes would consume what percentage".format(nodect))
            print("of the Class C address space...")
            while percent > 0:
                nodes = int(input("   Percent of nodes (MAX={}): ".format(percent)) or "100")
                density = int(input("   Percent of class C space occupied: ") or "100")
                if (nodes < 100 and nodes > 1):
                    percent = percent - nodes
                else:
                    print("Illegal node percentage value ({})".format(nodes))
                    continue
                if (density > 100 or density < 1):
                    print("Illegal density percentage value ({})".format(density))
                    continue
                net_breakdown.append((nodes, density))
            subnets = calculate_subnets(nodect, net_breakdown)
            print('Total subnets: {}'.format(subnets))

                                #  setting device breakdown ----------------
        dev_breakdown = get_default_dev_distro(nodect)
        dev_distr = input("Manually reset the above Device Role Distribution? [No]: ") or "No"
        if (dev_distr.lower() != 'no' and dev_distr.lower() != 'n'):
            remainder = nodect
            for category in sorted(dev_breakdown.keys()):
                if (remainder == 0):
                    dev_breakdown[category] = 0
                    continue
                category_count = dev_breakdown[category]
                if (remainder < category_count):
                    category_count = remainder
                while (remainder > 0):
                    if (category == 'Unknown'):
                        continue
                    category_count = int(input("{} (MAX={}) [{}]: ".format(category, remainder, dev_breakdown[category])) or category_count)
                    remainder -= category_count
                    if (remainder < 0 or category_count < 0):
                        print("Illegal value {}".format(category_count))
                        remainder += category_count

                    else:
                        dev_breakdown[category] = category_count
                        break;
            if (remainder > 0):
                dev_breakdown['Unknown'] += remainder

        domain = input("Domain name to use (press ENTER to auto-generate): ") or generate_fqdn()
        cont = input("Ready to generate json (No to start over)? [Yes]: ") or "Yes"

    net_configs = build_configs(nodect, net_breakdown, dev_breakdown, domain)
    if VERBOSE:
        print("\nSaving network profile to {}, based on the following config:".format(outname))
        for i in net_configs:
            print(json.dumps(i.get(), indent=4))
    else:
        print("\n Saving network profile to {}".format(outname))





if __name__ == "__main__":
    main()
