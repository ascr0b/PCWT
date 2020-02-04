function del(id) {
	var bool = confirm("Are you sure?");
	if (bool === false) {
		return "";
	}
	var xhttp = new XMLHttpRequest();

	xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById(id).remove();
            } 

        }
    }

    xhttp.open("POST", "/api/delete", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : id }));
}