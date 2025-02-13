import datetime
import os
import socket
from wtokenizer import tokenizeScript
from wparser import parseTokens


# GLOBAL VARIABLES
request_headers = {}    # client's request headers
response_headers = {}   # server's response headers
response_content = None # content returned by server





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
  print('Fatal Error: wserver.config error ... ' + str(err))
  os._exit(0)





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
sockets = []
for host in SOCKETHOSTS:
  for port in SOCKETPORTS:
    # init sockets
    aSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    aSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # start listening on host:port combo(s)
    try:
      aSocket.bind((host, int(port)))
      aSocket.listen(int(config['max_connections']))  # max connections
      sockets.append(aSocket)
      print('listening on ' + host + ':' + str(port))
    except Exception as bindFail:
      print('couldn\'t bind ' + host + ':' + str(port) + ' ... ' + str(bindFail))





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
  request_headers['date'] = datetime.datetime.now().strftime("%a, $d %b %Y %H:%M:00 MST")

  for line in lines[1:]:
    if line == "":
      break

    key, value = line.split(":", 1)
    request_headers[key.strip()] = value.strip()

  return(request_headers)





def constructResponse():
  global response_headers
  global response_content


  # TOKENIZE AND PARSE W-LANG FILES ... begin with _onStart.wlang
  # get starting .wlang script
  try:
    scriptPath = config['library'] + '/_onStart.wlang'
    with open(scriptPath, "r", encoding="utf-8") as file:
      response_content = file.read()  #placeholder to ensure everything up to tokenizeScript and parseTokens works
  except:
    print("Fatal Error: _onStart.wlang file doesn't exist in the configured library directory.")

  # attempt tokenization
  try:
    tokens = tokenizeScript(scriptPath)
  except Exception as err:
    print('Fatal Error: Could not parse script ' + str(script) + ' ... Error: ' + str(err))

  # attempt parse
  try:
    AST = parseTokens(tokens)
  except Exception as err:
    print('Fatal Error: Could not parse tokenized script into AST ... Error: ' + str(err))
  

  # set default headers
  response_headers.setdefault('statusCode', 200)
  response_headers.setdefault('statusMessage', 'OK')
  response_headers.setdefault('contentType', 'text/html; charset="UTF-8"')
  response_headers.setdefault('connection', 'close')

  # construct the payload header
  response =  f"HTTP/1.1 {response_headers['statusCode']} {response_headers['statusMessage']}\r\n"
  response += f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
  response += f"Connection: {response_headers['connection']}\r\n"  
  response += f"Content-Type: {response_headers['contentType']}\r\n"
  response += f"Date: {datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:00 MST')}\r\n"
 #response += f"set-cookie: cookieName=%7BcookieVal%7D; domain=www.example.com; expires=Wed, 11 Feb 2026 00:00:00 GMT;SameSite=Lax\r\n"
  
  # append payload content
  response += f"\r\n" # this line marks end of headers
  response += response_content
  return response





# GET DATA FROM PORT TO BEGIN RESPONSE
try:
  while True:
    for aSocket in sockets:
      connection, address = aSocket.accept()
      clientRequest = connection.recv(1024).decode("utf-8")

      if len(clientRequest) > 0:
        parseRequest(clientRequest)
        print(request_headers)
        print('\n')

        response = constructResponse()
        print(response)

        connection.sendall(response.encode('utf-8'))
        connection.close()

except Exception as err:
  connection.close()
  print("Fatal Error: ", err)
