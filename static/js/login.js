function save() {
    var user = document.getElementById("user");
    var pass = document.getElementById('pass');
	//document.cookie = 'user=daiki';
	//document.cookie = 'pass=miyagawa';
    sessionStorage.setItem('user', user.value);
    sessionStorage.setItem('pass', pass.value);
}
