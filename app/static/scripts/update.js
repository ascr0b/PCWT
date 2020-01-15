class Host {
    constructor(project, ip, ports) {
        this.project = project;
        this.ip = ip;
        this.ports = ports;
    }
}

class Port {
    constructor(port, service, product) {
        this.port = port;
        this.service = service;
        this.product = product;
    } 
}

class Domain {
    constructor(project, domain, ip) {
        this.project = project;
        this.domain = domain;
        this.ip = ip;
    } 
}

function addBlock() {
    port = '<div class="port"><div class="form-group"><input type="text" class="form-control" placeholder="Port" name="port" required></div><div class="form-group"><input type="text" class="form-control" placeholder="Protocol" name="protocol" required></div><div class="form-group"><input type="text" class="form-control" placeholder="Service" name="service"></div></div>';
    document.getElementById("addHost").insertAdjacentHTML('beforeend', port);

}

function deleteBlock() {
  select = document.getElementById('addHost');
  select.removeChild(select.lastChild);
}

function submitHost() { 
    select = document.getElementById('formHost');
    project = select.getElementsByTagName('input')[0].value;
    ip = select.getElementsByTagName('input')[1].value;
    k = select.getElementsByTagName('input').length;
    ports = [];
    for (var i = 2; i < k; i += 3) {
        port = select.getElementsByTagName('input')[i].value;
        service = select.getElementsByTagName('input')[i + 1].value;
        product = select.getElementsByTagName('input')[i + 2].value;
        ports.push(new Port(port, service, product))
    }

    host = new Host(project, ip, ports);

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById('successh').innerHTML = "SUCCESS: The record was add/updated.";
            } else {
                document.getElementById('errorh').innerHTML = "ERROR: Check that the form is filled out correctly.";
            }

        }
    }

    xhttp.open("POST", "/api/addHost", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify(host));

}

function submitDomain() { 
    select = document.getElementById('formDomain');
    project = select.getElementsByTagName('input')[0].value;
    domain = select.getElementsByTagName('input')[1].value;
    ip = select.getElementsByTagName('input')[2].value;

    domain = new Domain(project, domain, ip);

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById('successd').innerHTML = "SUCCESS: The record was add/updated.";
            } else {
                document.getElementById('errord').innerHTML = "ERROR: " + response.status;
            }

        }
    }

    xhttp.open("POST", "/api/addDomain", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify(domain));

}