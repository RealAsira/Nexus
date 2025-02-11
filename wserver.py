import os
import socket


# GLOBAL VARIABLES
request_headers = {}    #client's request headers
response_headers = {}   # custom response headers
response_content = """
<!DOCTYPE html>
<html>
  <head>
    <title>W-Lang</title>
  </head>
  <body>
    <h2>W-Lang Website</h2>
  </body>
</html>
"""
response_statusCode = 200
response_statusMessage = 'OK'
response_contentType = 'text/html'





# IMPORT SERVER CONFIGURATION ... PARSE INTO config OBJECT
try:
  with open('wserver.config', 'r') as wserver_config:
    config = {}

    for line in wserver_config:
      line = line.strip()
      if not line or line.startswith('#'): continue
      if '=' in line:
        setting, value = line.split('=', 1)
        value = value.strip()

        # if value is a boolen
        if value.lower() in ['true', 'false']:
          config[setting.strip()] = bool(value)
        
        # if value is a digit
        elif value.isdigit():
          config[setting.strip()] = int(value)

        # if value is a list
        elif ',' in value:
          config[setting.strip()] = [item.strip().strip("'") for item in value.split(',')]

        # if value is a string
        else:
          config[setting.strip()] = str(value.strip())

except Exception as err:
  print('Fatal error: wserver.config error ... ' + str(err))
  os._exit(0)





# INIT SOCKET
aSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
aSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)


# if single host is listened to then convert to list for iteration
if config['hosts'] == str(config['hosts']):
  SOCKETHOSTS = [str(config['hosts'])]
else:  
  SOCKETHOSTS = config['hosts']

# if single port is listened to the convert to list for iteration
if config['ports'] == str(config['ports']):
  SOCKETPORTS = [str(config['ports'])]
else:
  SOCKETPORTS = config['ports']


# ATTEMPT SOCKET BIND
for host in SOCKETHOSTS:
  for port in SOCKETPORTS:
    # start listening on host:port combo(s)
    try:
      aSocket.bind((host, int(port)))
      print('listening on ' + host + ':' + str(port))
    except Exception as err:
      print('couldn\'t bind ' + host + ':' + str(port) + ' ... ' + str(err))

# LISTEN TO x CONNECTIONS CONCURRENTLY
aSocket.listen(int(config['max_connections']))





# PARSE THE REQUEST INTO SOMETHING USABLE
def parseRequest(request):
  global request_headers
  request_headers = {}

  request = str(request)
  lines = request.split("\r\n")
  
  rqstLine = lines[0]
  method, path, protocol = rqstLine.split(' ')
  request_headers['method'] = method
  request_headers['path'] = path
  request_headers['protocol'] = protocol

  for line in lines[1:]:
    if line == "":
      break

    key, value = line.split(":", 1)
    request_headers[key.strip()] = value.strip()

  return(request_headers)


def constructResponse():
  response =  f"HTTP/1.1 {response_statusCode} {response_statusMessage}\r\n"
  response += f"Content-Type: {response_contentType}"
  response += f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
  response += f"Connection: close\r\n"  
  response += f"\r\n" # end of headers
  response += response_content
  return response






# GET DATA FROM PORT TO BEGIN RESPONSE
try:
  while True:
    connection, address = aSocket.accept()
    clientRequest = connection.recv(1024).decode("utf-8")

    if len(clientRequest) > 0:
      svr = parseRequest(clientRequest)
      print(svr)
      print(svr['path'])

      response = constructResponse()
      connection.sendall(response.encode('utf-8'))
      connection.close()

except Exception as err:
  connection.close()
  print("Error:", err)
