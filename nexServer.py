#import nexServerGlobals
import asyncio
import datetime
import os
import socket
from nexTokenizer import tokenizeScript
from nexParser import parseTokens


# GLOBAL VARIABLES
request_headers:dict = {}    # client's request headers
response_headers:dict = {}   # server's response headers
response_content = None      # content returned by server
config:dict = {}             # nexus server configuration options
sockets:list = []            # hosts/ports to bind to





def getConfig()->None:
  """Import server configuration and parse into config list"""
  global config
  try:
    with open('nexServer.config', 'r') as nexServer_config:

      for line in nexServer_config:
        line:str = line.strip()
        if not line or line.startswith('#'): continue
        if '=' in line:
          setting, value = line.split('=', 1)
          value = value.strip()

          # if value is a boolen
          if value.upper() in ['TRUE', 'FALSE']:
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
    print('Fatal Error: nexServer.config error ... ' + str(err))
    os._exit(0)





def setupSockets()->None:
  """Configure sockets array from hosts/ports in config object"""
  global config
  global sockets

  # if single host is listened to then convert to list for iteration
  if config['hosts'] == str(config['hosts']):
    SOCKETHOSTS = [str(config['hosts'])]
  else:  
    SOCKETHOSTS = config['hosts']

  # if single port is listened to the convert to list for iteration
  if isinstance(config['ports'], int):
    SOCKETPORTS = [str(config['ports'])]
  else :
    SOCKETPORTS = config['ports']
  

  # ATTEMPT SOCKET BIND
  for host in SOCKETHOSTS:
    for port in SOCKETPORTS:
      # init sockets
      aSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      aSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      aSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
      sockets.append(aSocket)

      # bind the socket to a port
      try:
        aSocket.bind((host, int(port)))
        aSocket.listen(int(config['max_connections']))  # max connections allowed (per socket)
        print(f"Configured socket binding for {host}:{str(port)}")
      except Exception as err:
        print(f"Couldn't configure socket binding for {host}:{str(port)} ... {str(err)}")





def parseRequest(request:str)->None:
  """Parse client request into usable parts"""
  global request_headers
  request_headers = {}

  request = str(request)
  lines:str = request.split("\r\n")
  
  rqstLine:str = lines[0]
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





def constructResponse() -> bytes:
  """Setup initial headers then run response through tokenizer, parser, and interpretter"""
  global response_headers
  global response_content


  # TOKENIZE AND PARSE .NEX FILES ... begin with _onStart.nex
  # get starting .nex script
  try:
    scriptPath:str = config['library'] + '/_onStart.nex'
    with open(scriptPath, "r", encoding="utf-8") as file:
      response_content = file.read()  #placeholder to ensure everything up to tokenizeScript and parseTokens works
  except:
    print(f"Fatal Error: _onStart.nex file doesn't exist in the configured library directory.")

  # attempt tokenization
  try:
    tokenStack:object = tokenizeScript(response_content)

    # attempt parse
    try:
      AST:object = parseTokens(tokenStack)
    except Exception as err:
      print(f"Fatal Error: Could not parse tokens into nodal-AST ... Error: {str(err)}")
  except Exception as err:
    print(f"Fatal Error: Could not tokenize script ... Error: {str(err)}")
  
  # set default headers
  response_headers.setdefault('statusCode', 200)
  response_headers.setdefault('statusMessage', 'OK')
  response_headers.setdefault('contentType', 'text/html; charset="UTF-8"')
  response_headers.setdefault('connection', 'close')

  # construct the response header
  headers =  f"HTTP/1.1 {response_headers['statusCode']} {response_headers['statusMessage']}\r\n"
  headers += f"Content-Length: {len(response_content.encode('utf-8'))}\r\n"
  headers += f"Connection: {response_headers['connection']}\r\n"  
  headers += f"Content-Type: {response_headers['contentType']}\r\n"
  headers += f"Date: {datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:00 MST')}\r\n"
 #headers += f"set-cookie: cookieName=%7BcookieVal%7D; domain=www.example.com; expires=Wed, 11 Feb 2026 00:00:00 GMT;SameSite=Lax\r\n"
  
  # client is expected \r\n\r\n ...
  # because previous header has \r\n, one more is needed. This marks end of headers, start of body
  headers += f"\r\n"

  # convert headers and body to bytes
  headersEncoded = headers.encode('utf-8')
  contentEncoded = response_content.encode('utf-8')

  # send headers and payload as response
  response = headersEncoded + contentEncoded
  return response





# GET DATA FROM PORT TO BEGIN RESPONSE
"""
OLD CODE ONLY WORKS FOR SINGLE SOCKET CONFIGURATION
if __name__ == "__main__":
  getConfig()
  setupSockets()

  print(config, sockets)

  # THIS LOOP ONLY WORKS FOR SINGLE SOCKETS (IE, cannot listen to multiple hosts or ports simultaneously)
  try:
    while True:
      for aSocket in sockets:
        print(f"Awaiting conn via {aSocket.getsockname}")
        connection, address = aSocket.accept()
        print(f"Established conn via {aSocket.getsockname}")

        clientRequest = connection.recv(1024).decode("utf-8")

        if len(clientRequest) > 0:
          parseRequest(clientRequest)
          #print('\n\n', request_headers)
          #print('\n')

          response = constructResponse()
          #print('\n\n' + str(response))

          try:
            connection.sendall(response)
          except Exception as err:
            print(f"Error transmitting response: {err}")
          finally:
            connection.close()
            print(f"Conn closed {aSocket.getsockname}")

  except Exception as err:
    print("Error processing request or response: ", err)
    pass  # continue loop even on error
"""




async def handleRequest(reader, writer)->None:
  """Handle a client request"""
  request = await reader.read(1024)
  clientAddr = writer.get_extra_info('peername')

  # new request has content
  if len(request) > 0:
    parseRequest(request.decode('utf-8'))
    print(f"\nconn with {clientAddr}: requested {request_headers['path']}")

    response = constructResponse()
    writer.write(response)
    print(f"conn with {clientAddr}: sent response")
    await writer.drain()  # ensures actual sending of response

  print(f"conn with {clientAddr}: closed")
  writer.close()





# LISTEN ON EACH SOCKET ASYNC'd
async def startServer()->None:
  """Initialize the server"""
  # async'd server tasks
  tasks:list = []

  # indefinitely server on each socket
  for aSocket in sockets:
    host, port = aSocket.getsockname()

    if host != '0.0.0.0' and port != '0':
      try:
        # coroutine to run upon receiving a request (handleRequest)
        server = await asyncio.start_server(handleRequest, sock=aSocket)

        # add socket to async tasks
        tasks.append(server.serve_forever())
        print(f"Success! Now serving on {host}:{port}")
      except Exception as err:
        print(f"Error: Couldn't add {host}:{port} to async listener. Server is not listening to this socket!: {err}")
        pass
    else:
      print(f"Skipped binding on {host}:{port}")
  
  # run all socket listening tasks
  await asyncio.gather(*tasks)





# MAIN LOOP
if __name__ == "__main__":
  getConfig(); print('\n')
  setupSockets(); print('\n')
  asyncio.run(startServer())
