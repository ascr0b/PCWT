function updatePortNote(portid) {
	var portid = document.getElementById("portUpdateID").getAttribute("value");
	var note = document.getElementById("portUpdateNote").value;
	if (note == null || note == "") {
		return;
	} else {
		var xhttp = new XMLHttpRequest();

		xhttp.onreadystatechange = function() {
			if (xhttp.readyState == 4 && xhttp.status == 200) {
				var str = this.responseText;
				var portNote = JSON.parse(str);
				document.getElementById(portid).innerHTML = portNote.note;
				
			}
		}

		xhttp.open("POST", "/api/updatePortNote", true);
		xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
		xhttp.send(JSON.stringify({"portid" : portid, "note" : note}));
		closePortUpdateForm();
	}
}

function updateHostNote() {
	var hostid = document.getElementById("hostUpdateID").getAttribute("value");
	var note = document.getElementById("hostUpdateNote").value;
	if (note == null || note == "") {
		return;
	} else {
		var xhttp = new XMLHttpRequest();

		xhttp.onreadystatechange = function() {
			if (xhttp.readyState == 4 && xhttp.status == 200) {
				var str = this.responseText;
				var hostNote = JSON.parse(str);
				document.getElementById(hostid + "_hostNote").innerHTML = hostNote.note;
				
			}
		}

		xhttp.open("POST", "/api/updateHostNote", true);
		xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
		xhttp.send(JSON.stringify({"hostid" : hostid, "note" : note}));
		closeHostUpdateForm();
	}
}


function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
 }

function markAs(hostid, type) {
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var hostStyle = JSON.parse(str);
			var id = hostid + "_hostStyle"
			if (type == 'Default') {
				document.getElementById(id).getElementsByTagName('span')[0].remove();
				return;
			}
			if (document.getElementById(id).getElementsByTagName('span').length == 0) {
				document.getElementById(id).innerHTML += "	<span></span>"
			}
			document.getElementById(id).getElementsByTagName('span')[0].innerHTML = hostStyle.style;
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

	xhttp.open("POST", "/api/updateHostStyle", true);
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"hostid" : hostid, "type" : type}));

}

function openHostUpdateForm(hostid) {
	var xhttp = new XMLHttpRequest()
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var hostNote = JSON.parse(str);
			document.getElementById("hostUpdateNote").value = hostNote.note;
			document.getElementById("hostUpdateID").setAttribute("value", hostid);
			document.getElementById("hostUpdateForm").style.display = "block";
		}
	}
	xhttp.open("POST", "/api/getHostNote");
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"hostid" : hostid}));
	
}

function closeHostUpdateForm() {
	document.getElementById("hostUpdateForm").style.display = "none";
}

function openPortUpdateForm(portid) {
	var xhttp = new XMLHttpRequest()
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var portNote = JSON.parse(str);
			document.getElementById("portUpdateNote").value = portNote.note;
			document.getElementById("portUpdateID").setAttribute("value", portid);
			document.getElementById("portUpdateForm").style.display = "block";
		}
	}
	xhttp.open("POST", "/api/getPortNote");
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"portid" : portid}));

	
}

function closePortUpdateForm() {
	document.getElementById("portUpdateForm").style.display = "none";
}


function deleteHost(hostid) {
	var bool = confirm("Are you sure?");
	if (bool === false) {
		return "";
	}
	var xhttp = new XMLHttpRequest()
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var result = JSON.parse(this.responseText);
			if (result.status == 'success') {
				document.getElementById(hostid).remove();
			}
		}
	}
	xhttp.open("POST", "/api/deleteHost");
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"hostid" : hostid }));

	
}