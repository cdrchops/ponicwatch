<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Ponicwatch</title>
</head>
<body>
% include('header.html')
<h1>Dashboard for PonicWatch</h1>

% if session_valid:
Click <a href="/stop">here</a> to stop the application.
% end

</body>
</html>