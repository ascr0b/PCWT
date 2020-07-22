function deleteCron(cronid) {
	var bool = confirm("Are you sure?");
	if (bool === false) {
		return "";
	}
	var xhttp = new XMLHttpRequest()
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			var result = JSON.parse(str);
			if (result.status == 'success') {
				document.getElementById(cronid).remove();
			}
			
		}
	}
	xhttp.open("POST", "/api/deleteCron");
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"cronid" : cronid}));
	
}

function statusCron(cronid) {
	select = document.getElementById(cronid);
	var s = select.getElementsByTagName('input')[0].checked;
	if (s === true) {
		status = "1";
	}
	else {
		status = "0";
	}

	var xhttp = new XMLHttpRequest()
	xhttp.onreadystatechange = function() {
		if (xhttp.readyState == 4 && xhttp.status == 200) {
			var str = this.responseText;
			
			
		}
	}
	xhttp.open("POST", "/api/statusCron");
	xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
	xhttp.send(JSON.stringify({"cronid" : cronid, "status" : status }));
	
}