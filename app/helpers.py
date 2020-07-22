### Classes for hosts dashboard
class projectClass:
	name = ""
	description = ""
	hosts = []

class hostClass:
	id = ""
	ip = ""
	note = ""
	style = ""
	ports = []
	hostnames = []

class hostnameClass:
	hostnameID = ""
	hostname = ""	
		
class portClass:
	id = ""
	port = ""
	state = ""
	service = ""
	version = ""
	note = ""
	

### Classes for ports dashboard
class portDashboardClass:
	name = ""
	description = ""
	ports = []

class portMiniClass:
	port = ""
	amount = 0
	hosts = []


### Classes for domain dashboard
class domainsDashboardClass:
	id = ""
	name = ""
	domains = []

class domainClass:
	id = ""
	domain = ""
	ip = ""
	note = ""
	style = ""
	ports = []


### Classess for crontab
class taskClass:
	id = ""
	domain = ""
	project = ""	