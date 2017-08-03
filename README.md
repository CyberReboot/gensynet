# cybersynthesis


A JSONic way to interactively create a quick network spec and synthesize network host descriptions. THese host 
JSON objects are then written to a timestamped file.

## usage

        python3 synthjson.py -h
        usage: synthjson.py [-h] [-v]

        optional arguments:
          -h, --help     show this help message and exit
          -v, --verbose  Provide program feedback


##  useful functions

The Python library can be imported as `import synthjson` with the following (hopefully helpful) internal functions:

### generate_ip(prefix)

Takes in a partial IP string and returns a random IP string.

        >>> synthjson.generate_ip('10.0')
        '10.0.128.53'


### generate_fqdn(domain=None, subdomains=0)

Takes in a domain (or randomly generates a gibberish one if none is provided), and builds a FQDN with the specified
number of subdomains.

	>>> synthjson.generate_fqdn(subdomains=1)
	'awf.9c24by18nc.local'
	>>> synthjson.generate_fqdn()
	'nm3li.local'
	>>> synthjson.generate_fqdn(domain='a.internal', subdomains=2)
	'dltyf.7jwmi.a.internal'


### calculate_subnets(total, breakdown)

Given a total number of hosts and the desired breakdown in 2-tuples (with the first number being the percentage 
of the total number of hosts, and the second number being the percentage of occupied Class C address space), calculate
how many subnets are needed to put every host in a subnet. This function returns -1 if the percentages or breakdowns
don't make sense. Obviously, there will be some networks with sparser-than-specified occupancies, in the event that there
still remains a surplus of hosts after dividing them up into the designated Class C space.


### build_configs(total, net_div, dev_div, domain)

Takes the total number of hosts, the breakdown of the network as specified in 2-tuples, the breakdown of network devices
(provided as a dictionary of `'device': integer(count)`), and a domain (if any), and builds JSON profiles of each subnet
space that makes up the rest of the network. 
	>>> j = synthjson.build_configs(total=100, net_div=[(50, 50), (15, 10), (35,15)], dev_div={'Developer workstation': 
	35, 'Business workstation': 50, 'Smartphone': 5, 'Printer': 1, 'File server': 5, 'SSH server': 4}, domain=None)

	Initialized subnet 2 with 50 hosts starting at 10.0.2.1
	Initialized subnet 1 with 15 hosts starting at 10.0.1.1
	Initialized subnet 0 with 35 hosts starting at 10.0.0.1
	>>> for i in j:
	...     print(json.dumps(i.get(), indent=2))
	... 
	{
	  "roles": {
	    "File server": 1,
	    "Business workstation": 23,
	    "Developer workstation": 19,
	    "SSH server": 3,
	    "Smartphone": 3,
	    "Printer": 1
	  },
	  "start_ip": "10.0.2.1",
	  "hosts": 50
	}
	{
	  "roles": {
	    "File server": 2,
	    "Business workstation": 13,
	    "Developer workstation": 0,
	    "SSH server": 0,
	    "Smartphone": 0,
	    "Printer": 0
	  },
	  "start_ip": "10.0.1.1",
	  "hosts": 15
	}
	{
	  "roles": {
	    "File server": 2,
	    "Business workstation": 14,
	    "Developer workstation": 16,
	    "SSH server": 1,
	    "Smartphone": 2,
	    "Printer": 0
	  },
	  "start_ip": "10.0.0.1",
	  "hosts": 35
	}



## bugs and other questions

Please report bugs and issues by opening a ticket on https://va-vsrv-github.a.internal/achang/cybersynthesis
A JSONic way to interactively create a quick network spec and synthesize network host descriptions.
