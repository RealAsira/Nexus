#import NexServerGlobals
import asyncio
import datetime
import os
import socket
from NexTokenizer import tokenize_script
from NexParser import parse_tokens
from NexInterpreter import interpret_AST


# GLOBAL VARIABLES
config:dict = {}             # nexus server configuration options
sockets:list = []            # hosts/ports to bind to





def get_config()->None:
  """Import server configuration and parse into config list"""
  global config
  try:
    with open('NexServer.config', 'r') as server_config:

      for line in server_config:
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
    print('Fatal Error: NexServer.config error ... ' + str(err))
    os._exit(0)





def setup_sockets()->None:
  """Configure sockets array from hosts/ports in config object"""
  global config
  global sockets

  # if single host is listened to then convert to list for iteration
  if config['hosts'] == str(config['hosts']):
    SOCKET_HOSTS = [str(config['hosts'])]
  else:  
    SOCKET_HOSTS = config['hosts']

  # if single port is listened to the convert to list for iteration
  if isinstance(config['ports'], int):
    SOCKET_PORTS = [str(config['ports'])]
  else :
    SOCKET_PORTS = config['ports']
  

  # ATTEMPT SOCKET BIND
  for host in SOCKET_HOSTS:
    for port in SOCKET_PORTS:
      # init sockets
      aSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      aSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      if hasattr(socket, "SO_REUSEPORT"):
        try:
          aSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
          print('System does not utilize SO_REUSEPORT')
          pass
      sockets.append(aSocket)

      # bind the socket to a port
      try:
        aSocket.bind((host, int(port)))
        aSocket.listen(int(config['max_connections']))  # max connections allowed (per socket)
        print(f"Configured socket binding for {host}:{str(port)}")
      except Exception as err:
        print(f"Couldn't configure socket binding for {host}:{str(port)} ... {str(err)}")





def parse_request(request:str)->dict:
  """Parse client request into usable parts"""
  request_headers = {}
  request = str(request)
  lines:str = request.split("\r\n")
  
  request_line:str = lines[0]
  method, path, protocol = request_line.split(' ')
  request_headers['method'] = method
  request_headers['path'] = path
  request_headers['protocol'] = protocol
  request_headers['date'] = datetime.datetime.now().strftime("%a, $d %b %Y %H:%M:00 MST")

  for line in lines[1:]:
    if line == "":
      break

    key, value = line.split(":", 1)
    request_headers[key.strip()] = value.strip()
  
  return request_headers





def construct_response() -> bytes:
  """Setup initial headers then run response through tokenizer, parser, and interpretter"""
  response_content = {}


  # TOKENIZE AND PARSE .NEX FILES ... begin with _OnStart.nex
  # get starting .nex script
  try:
    script_path:str = config['library'] + '/_OnStart.nex'
    with open(script_path, "r", encoding="utf-8") as file:
      content_OnStart = file.read()  #placeholder to ensure everything up to tokenize_script and parse_tokens works
  except:
    print(f"Fatal Error: _OnStart.nex file doesn't exist in the configured library directory.")

  # attempt tokenization
  try:
    tokenized_script:tuple = tokenize_script(content_OnStart, '_OnStart')
    token_stack:object = tokenized_script[0]
    script_name:str = tokenized_script[1]

    # attempt parse
    try:
      parsed_tokens:tuple = parse_tokens(token_stack, script_name)
      obj_AST:object = parsed_tokens[0]
      script_name:str = parsed_tokens[1]

      # attempt interpret
      try:
        interpretted_AST:tuple = interpret_AST(obj_AST, script_name)
        response_content = interpretted_AST[0]
        script_name:str = interpretted_AST[1]
      
      except Exception as err:
        print(f"Fatal Error: Could not interpret the AST ... Error: {str(err)}")
    except Exception as err:
      print(f"Fatal Error: Could not parse tokens into nodal-AST ... Error: {str(err)}")
  except Exception as err:
    print(f"Fatal Error: Could not tokenize script ... Error: {str(err)}")
  
  # set default headers
  response_headers = {}
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
  
  # client is expecting \r\n\r\n ...
  # because previous header has \r\n, one more is needed. This marks end of headers, start of body
  headers += f"\r\n"

  # convert headers and body to bytes
  headers_encoded = headers.encode('utf-8')
  content_encoded = response_content.encode('utf-8')

  # send headers and payload as response
  response = headers_encoded + content_encoded
  return response





async def handle_request(reader, writer)->None:
  """Handle a client request"""
  request = await reader.read(1024)
  client_address = writer.get_extra_info('peername')

  # new request has content
  if len(request) > 0:
    request_headers = parse_request(request.decode('utf-8'))
    print(f"\nconn with {client_address}: requested {request_headers['path']}")

    response = construct_response()
    writer.write(response)
    print(f"conn with {client_address}: sent response")
    await writer.drain()  # ensures actual sending of response

  print(f"conn with {client_address}: closed")
  writer.close()





# LISTEN ON EACH SOCKET ASYNC'd
async def start_server()->None:
  """Initialize the server"""
  # async'd server tasks
  tasks:list = []

  # indefinitely server on each socket
  for aSocket in sockets:
    host, port = aSocket.getsockname()

    if host != '0.0.0.0' and port != '0':
      try:
        # coroutine to run upon receiving a request (handle_request)
        server = await asyncio.start_server(handle_request, sock=aSocket)

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
  get_config(); print('\n')
  setup_sockets(); print('\n')
  asyncio.run(start_server())
