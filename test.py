import user
from user import User

request = dict()
request["User[name]"] = "osallou"
request["User[email]"] = "test@nomail.com"
request["User[age]"] = "39"
request["User[admin]"] = "nimportequoi"
request["User[options][categories]"] = "cat2"


user = User()

user.bind_form(request)

print '''
<!DOCTYPE html>  
<html>
<head>
	
  <meta charset="utf-8">
  <title>Ming Form</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link rel="shortcut icon" href="/static/img/favicon.ico">
  <link rel="stylesheet" href="static/css/mf.css">
  <link rel="stylesheet" href="static/css/bootstrap.min.css" media="screen">
  <link rel="stylesheet" href="static/css/bootstrap-responsive.min.css">
</head>

<body>


  <div id="page"><form class="form-horizontal">'''
    
print user.html( ['_id','name', 'email', 'age', 'admin', 'options', 'mongo'])

print '''</form></div>
  <script src="/static/bootstrap/js/bootstrap.min.js"></script>  
</body>
</html>'''



