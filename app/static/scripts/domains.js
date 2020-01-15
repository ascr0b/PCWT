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
			if (type == 'Default') {
				document.getElementById(id).getElementsByTagName('span')[0].remove();
				return;
			}
			if (document.getElementById(id).getElementsByTagName('span').length == 0) {
				document.getElementById(id).innerHTML += "	<span></span>"
			}
			document.getElementById(id).getElementsByTagName('span')[0].innerHTML = style.style;
			if (type == 'Checked') {
				document.getElementById(id).getElementsByTagName('span')[0].setAttribute("class", "badge badge-pill badge-secondary")
			}
			if (type == 'Hacked') {
				document.getElementById(id).getElementsByTagName('span')[0].setAttribute("class", "badge badge-pill badge-danger")
			}
			if (type == 'Suspicious') {
				document.getElementById(id).getElementsByTagName('span')[0].setAttribute("class", "badge badge-pill badge-warning")
			}
			
		}
	}

	xhttp.open("POST", "/api/updateDomainStyle", true);
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"domainid" : domainid, "type" : type}));

}

function deleteDomain(domainid) {
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