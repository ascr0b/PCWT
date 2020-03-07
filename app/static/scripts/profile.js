function changePass() {
    oldpwd = document.getElementById("oldpwd").value
    pwd = document.getElementById("pwd").value
    pwdconfirm = document.getElementById("pwdconfirm").value
	var xhttp = new XMLHttpRequest();

	xhttp.onreadystatechange = function() {
        if (xhttp.readyState == 4 && xhttp.status == 200) {
            var response = JSON.parse(this.responseText);
            if (response.status == "success") {
                document.getElementById("error").setAttribute("style", "display: none;")
                document.getElementById("success").setAttribute("style", "display: block;")
                document.getElementById("success").innerHTML = "SUCCESS: " + response.msg;
            }
            if (response.status == "error") {
                document.getElementById("success").setAttribute("style", "display: none;")
                document.getElementById("error").setAttribute("style", "display: block;")
                document.getElementById("error").innerHTML = "ERROR: " + response.msg;
            } 

        }
    }

    xhttp.open("POST", "/api/changepass", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"oldpwd" : oldpwd, "pwd" : pwd, "pwdconfirm" : pwdconfirm }));
}

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
                window.location.href = "/auth/signin";
            } 

        }
    }

    xhttp.open("POST", "/api/deleteuser", true);
    xhttp.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
    xhttp.send(JSON.stringify({"id" : id }));
}