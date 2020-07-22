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
                window.setTimeout(function() {
                    document.getElementById('successh').innerHTML = "";
                }, 2000);
            } else {
                document.getElementById('errorh').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('errorh').innerHTML = "";
                }, 2000);
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
                window.setTimeout(function() {
                    document.getElementById('successd').innerHTML = "";
                }, 2000);
            } else {
                document.getElementById('errord').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('errord').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/addDomain", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify(domain));

}


function submitName() { 
    select = document.getElementById('formName');
    project = select.getElementsByTagName('input')[0].value;
    name = select.getElementsByTagName('input')[1].value;

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById('successn').innerHTML = "SUCCESS: Projects's name was updated.";
                window.setTimeout(function() {
                    document.getElementById('successn').innerHTML = "";
                }, 2000);
            } else {
                document.getElementById('errorn').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('errorn').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/editName", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : project, "name" : name}));

}


function submitSubdomains() { 
    var bool = confirm("Are you sure?");
    if (bool === false) {
        return "";
    }
    select = document.getElementById('formSubdomains');
    project = select.getElementsByTagName('input')[0].value;
    domain = select.getElementsByTagName('input')[1].value;
    period = select.getElementsByTagName('select')[0].value;

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById('successc').innerHTML = "SUCCESS: Task was created.";
                window.setTimeout(function() {
                    document.getElementById('successc').innerHTML = "";
                }, 2000);
            } else {
                document.getElementById('errorc').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('errorc').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/subdomains", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : project, "domain" : domain, "period" : period}));

}

function nmapHandler() {
    t = document.getElementById('sel3').value;
    if (t === "1" || t === "2") {
        document.getElementById('nmap').setAttribute("style", "display: none");
    } else {
        document.getElementById('nmap').setAttribute("style", "display: block");
    }
}

function masscanHandler() {
    t = document.getElementById('sel2').value;
    if (t === "1" || t === "2") {
        document.getElementById('masscan').setAttribute("style", "display: none");
    } else {
        document.getElementById('masscan').setAttribute("style", "display: block");
    }
}



function submitMasscan() { 
    var bool = confirm("Are you sure?");
    if (bool === false) {
        return "";
    }
    select = document.getElementById('formMasscan');
    project = select.getElementsByTagName('input')[0].value;
    type = select.getElementsByTagName('select')[0].value;
    ips = select.getElementsByTagName('input')[1].value;

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById('successm').innerHTML = "SUCCESS: Task was created.";
                window.setTimeout(function() {
                    document.getElementById('successm').innerHTML = "";
                }, 2000);
            } else {
                document.getElementById('errorm').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('errorm').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/masscan", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : project, "ips" : ips, "type" : type}));

}

function submitNmap() { 
    var bool = confirm("Are you sure?");
    if (bool === false) {
        return "";
    }
    select = document.getElementById('formNmap');
    project = select.getElementsByTagName('input')[0].value;
    type = select.getElementsByTagName('select')[0].value;
    ips = select.getElementsByTagName('input')[1].value;

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById('successnm').innerHTML = "SUCCESS: Task was created.";
                window.setTimeout(function() {
                    document.getElementById('successnm').innerHTML = "";
                }, 2000);
            } else {
                document.getElementById('errornm').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('errornm').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/nmap", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : project, "ips" : ips, "type" : type}));

}