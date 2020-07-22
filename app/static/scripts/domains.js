function openDomainUpdateForm(domainid) {
	var xhttp = new XMLHttpRequest()
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var domainNote = JSON.parse(str);
			document.getElementById("domainUpdateNote").value = domainNote.note;
			document.getElementById("domainUpdateID").setAttribute("value", domainid);
			document.getElementById("domainUpdateForm").style.display = "block";
		}
	}
	xhttp.open("POST", "/api/getDomainNote");
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"domainid" : domainid}));

	
}

function closeDomainUpdateForm() {
	document.getElementById("domainUpdateForm").style.display = "none";
}

function updateDomainNote() {
	var domainid = document.getElementById("domainUpdateID").getAttribute("value");
	var note = document.getElementById("domainUpdateNote").value;
	if (note == null || note == "") {
		return;
	} else {
		var xhttp = new XMLHttpRequest();

		xhttp.onreadystatechange = function() {
			if (xhttp.readyState == 4 && xhttp.status == 200) {
				var str = this.responseText;
				var note = JSON.parse(str);
				document.getElementById(domainid + "_note").innerHTML = note.note;
				
			}
		}
		xhttp.open("POST", "/api/updateDomainNote", true);
		xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
		xhttp.send(JSON.stringify({"domainid" : domainid, "note" : note}));
		closeDomainUpdateForm();
	}
}


function markAs(domainid, type) {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var style = JSON.parse(str);
			var id = domainid + "_style"
			if (style.style == 'Default') {
				document.getElementById(id).getElementsByTagName('span')[0].remove();
				return;
			}
			if (document.getElementById(id).getElementsByTagName('span').length == 0) {
				document.getElementById(id).innerHTML += "	<span></span>"
			}
			document.getElementById(id).getElementsByTagName('span')[0].innerHTML = style.style;
			if (style.style == 'Checked') {
				document.getElementById(id).getElementsByTagName('span')[0].setAttribute("class", "badge badge-pill badge-secondary")
			}
			if (style.style == 'Hacked') {
				document.getElementById(id).getElementsByTagName('span')[0].setAttribute("class", "badge badge-pill badge-danger")
			}
			if (style.style == 'Suspicious') {
				document.getElementById(id).getElementsByTagName('span')[0].setAttribute("class", "badge badge-pill badge-warning")
			}
			
		}
	}

	xhttp.open("POST", "/api/updateDomainStyle", true);
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"domainid" : domainid, "type" : type}));

}

function deleteDomain(domainid) {
	var bool = confirm("Are you sure?");
	if (bool === false) {
		return "";
	}
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var result = JSON.parse(str);
			if (result.status == 'success') {
				document.getElementById(domainid).remove();
			}
		}
	}
	xhttp.open("POST", "/api/deleteDomain");
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"domainid" : domainid }));

}


function markAs2(domainid, type) {
	var id = domainid + "_style";
	if (!document.getElementById(id).getElementsByTagName('span')[0].innerHTML.includes("New")) {
		return "";
	}

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var style = JSON.parse(str);
			var id = domainid + "_style"
			if (style.style == 'Default') {
				document.getElementById(id).getElementsByTagName('span')[0].remove();
				return;
			}
		}
	}

	xhttp.open("POST", "/api/updateDomainStyle", true);
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"domainid" : domainid, "type" : type}));

}

function submitSubdomains(project, domain) { 
    var bool = confirm("Are you sure?");
    if (bool === false) {
        return "";
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
            	document.getElementById('info').setAttribute("class", "text-success")
                document.getElementById('info').innerHTML = "SUCCESS: Task was created.";
                window.setTimeout(function() {
                    document.getElementById('info').innerHTML = "";
                }, 2000);
            } else {
            	document.getElementById('info').setAttribute("class", "text-danger")
                document.getElementById('info').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('info').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/subdomains", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : project, "domain" : domain, "period" : "1"}));

}


function runMasscan(project, host) {
	var bool = confirm("Are you sure?");
    if (bool === false) {
        return "";
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
            	document.getElementById('info').setAttribute("class", "text-success")
                document.getElementById('info').innerHTML = "SUCCESS: Task was created.";
                window.setTimeout(function() {
                    document.getElementById('info').innerHTML = "";
                }, 2000);
            } else {
            	document.getElementById('info').setAttribute("class", "text-danger")
                document.getElementById('info').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('info').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/masscan", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : project, "ips" : host, "type" : "3"}));

}


function runNmap(project, host) {
	var bool = confirm("Are you sure?");
    if (bool === false) {
        return "";
    }

    var xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
            	document.getElementById('info').setAttribute("class", "text-success")
                document.getElementById('info').innerHTML = "SUCCESS: Task was created.";
                window.setTimeout(function() {
                    document.getElementById('info').innerHTML = "";
                }, 2000);
            } else {
            	document.getElementById('info').setAttribute("class", "text-danger")
                document.getElementById('info').innerHTML = "ERROR: " + response.status;
                window.setTimeout(function() {
                    document.getElementById('info').innerHTML = "";
                }, 2000);
            }

        }
    }

    xhttp.open("POST", "/api/nmap", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : project, "ips" : host, "type" : "3"}));

}