"""
TOKENIZER/LEXER CREATES "TOKENS" FROM A SCRIPT
"""
import NexErrorHandler as neh

import NexServerGlobals
all_reserved_tokens = NexServerGlobals.all_reserved_tokens
expr_type_tokens = NexServerGlobals.expr_type_tokens
string_delim_tokens = NexServerGlobals.string_delim_tokens
xml_delim_tokens = NexServerGlobals.xml_delim_tokens
ref_type_tokens = NexServerGlobals.ref_type_tokens
method_types = NexServerGlobals.method_types





# the stack all tokens are stored in
class TokenStack:
  def __init__(self):
    # [[line_number, token_type, token_value], .., ..]
    self.stack = []

  def insert(self, line_number:int, token_type:str, token_value, stack_position:int=None):
    """Add a token at position in stack OR at top of stack if no position specified"""
    #print(f"Stored token from line", line_number, 'as', token_type, token_value)
    position = stack_position if stack_position != None else len(self.stack)
    self.stack.insert(position, [int(line_number), token_type.strip().upper(), token_value.strip()])
  
  def pop(self, pos:int=0):
    """Remove a token from the bottom of the stack"""
    self.stack.pop(pos)
  
  def readCurrentToken(self):
    """Return the bottom token from the stack, doesn't remove"""
    return self.stack[0]
  
  def clear(self):
    """Clears the entire token stack"""
    # the TokenStack is reused and needs to be cleared between uses
    self.stack.clear()
  
default_stack = TokenStack()
  




def tokenizeScript(script:str, script_name:str = "Unknown Nexus Module", token_stack:object=default_stack)->tuple:
  """Process a script into a token stack"""
  global all_reserved_tokens, string_delim_tokens, xml_delim_tokens
  #global expr_type_tokens
  #global ref_type_tokens
  #global method_types

  current_token:str = None
  token_line_number:int = 1           # file line number for where token is at
  is_processing_string:bool = False   # currently processing a string token
  processing_string_delim:chr = None  # " or '
  is_processing_fstring:bool = False  # currently processing a functional / formatted string token
  is_processing_xml:bool = False      # currently processing an xml token

  script_length:int = len(script)     # total length of the script
  pos:int = 0                     # position where is being processed


  def findNextReservedSingleCharToken(search_token:str = None) -> int:
    """Returns the position of the next single character reserved token"""
    nonlocal script
    nonlocal pos
    cursor:int = pos

    while True:
      if cursor < script_length:

        # searching for any reserved token
        if not search_token:
          if script[cursor].upper() in all_reserved_tokens:
            break # found match
          else: cursor += 1

        # searching for a specific reserved token
        if search_token:
          if script[cursor].upper() == search_token:
            break # found match
          else: cursor +=1
          
      else:
        cursor = script_length  #end of script is last char
        break
    
    return cursor



  def getToken() -> str:
    """Finds and returns the next token"""
    nonlocal script, token_line_number, is_processing_string, processing_string_delim, is_processing_fstring, is_processing_xml
    
    some_token:str = str(script[pos].upper())
    
    # new-line = inc line number
    if some_token == '\n':
      token_line_number += 1
      #print(f"a. Found token newline")
      return some_token
    

    # this is the start of a string
    elif some_token in string_delim_tokens:
      # currently processing a string AND end delim match start delim .. end of string unless escaped
      if is_processing_string and (some_token == processing_string_delim):
        is_escaped = True if script[pos-1] == '\\' else False

        # if it is escaped, continue processing string; otherwise, is end of string
        if not is_escaped:
          is_processing_string = False
          is_processing_fstring = False
          processing_string_delim = None # no longer processing

      elif not is_processing_string:
        is_processing_string = True
        processing_string_delim = some_token
        if script[pos-1].upper() == 'F':
          is_processing_fstring = True   # this is a formatted/functional string

      #print(f"b. Found token {some_token}")
      return some_token


    # this token is either XML or comparison
    elif some_token in xml_delim_tokens:
      # +1 to get next pos, -1 to get set script last char bound
      next_char:str = str(script[min(pos+1, is_processing_xml-1)]).upper()

      if next_char not in all_reserved_tokens: is_processing_xml = True              # not a comparison
      if str(some_token) + str(next_char) in ['/>', '</']: is_processing_xml = True  # is certainly xml
      if some_token == '/' and next_char in ['/', '=']: is_processing_xml = False    # /= and // are reserved
      if some_token == '/' and next_char != '>': is_processing_xml = False           # indicates this is a / OP

      if is_processing_xml == False: # comparison operator
        #print(f"g. Found token {some_token}")
        return some_token

      elif is_processing_xml == True:
        # /> (xml open-tag self-end)
        if (str(some_token) + str(next_char) == '/>'):
          some_token = str(some_token) + str(next_char)  # get /> instead of /
          #print(f"h. Found token {some_token}")
          return some_token
        
        # </ (xml close-tag start)
        elif (str(some_token) + str(next_char) == '</'):
          some_token = str(some_token) + str(next_char)  # get </ instead of <
          #print(f"h. Found token {some_token}")
          return some_token
        
        # < (xml open-tag start)
        elif some_token == '<':
          #print(f"h. Found token {some_token}")
          return some_token
        
        # > (xml tag-end)
        elif some_token == '>':
          #print(f"h. Found token {some_token}")
          return some_token

        else:
          try: raise neh.NexException(f'Failed XML token-type lookup on "{some_token}"')
          except neh.NexException as err:
            neh.nexError(err, False, script_name, token_line_number)
            is_processing_xml = False
            return some_token


    # vanilla string
    elif is_processing_string and not is_processing_fstring:     
      end_pos:int = findNextReservedSingleCharToken(processing_string_delim)
      some_token = script[pos:end_pos]
      #print(f"e. Found token {some_token}")
      return some_token
    

    # reserved single char token (including space delim)
    elif some_token.upper() in all_reserved_tokens:
      #print(f"c. Found token {some_token.replace(' ', '_')}")
      return some_token


    # functional string - tokenize each possible token in it
    elif is_processing_string and is_processing_fstring:
      end_pos:int = findNextReservedSingleCharToken()
      some_token = script[pos:end_pos]
      #print(f"f. Found token {some_token}")
      return some_token
    

    # multi-character reserved or generic arg...
    # simply find end of this token by getting start of next
    elif not is_processing_string and not is_processing_fstring:
      end_pos:int = findNextReservedSingleCharToken()
      some_token = script[pos:end_pos]
      #print(f"d. Found token {some_token}")
      return some_token



  # reset the stack and insert scptStrt
  token_stack.clear()
  token_stack.insert(0, 'scptStrt', '')



  while True:
  # PROCESS SCRIPT INTO TOKENS
    # full script has been processed
    if pos >= script_length:
      break
    
    # new token
    if current_token is None:
      current_token = getToken() # now that the token is found, the next step will store it
      #print(f"New token found: {current_token}")
      #print(current_token, all_reserved_tokens[current_token.upper()])

      # space character delims tokens ... doesn't get stored
      if current_token == ' ':
        pos += 1
        current_token = None
        continue


      # the current_token is a string delimiter
      elif current_token in string_delim_tokens:
        # is_processing_string is toggled in getToken. If true, then a str just started..
        if is_processing_string:
          is_escaped:bool = True if script[pos-1] == '\\' else False

          if is_escaped:
            token_stack.insert(token_line_number, all_reserved_tokens[current_token.upper()].upper(), current_token.upper())
  
          elif not is_escaped:
            #print(f"Stored token as STRLITERAL {current_token}")
            token_stack.insert(token_line_number, "STRLITERAL", current_token.upper())

        elif not is_processing_string:
          #print(f"Stored token as STREND {current_token}")
          token_stack.insert(token_line_number, "STREND", current_token.upper())

        pos += len(current_token)
        current_token = None
        continue


      # the current token is an XML tag of some kind instead of comparison operator
      elif is_processing_xml and current_token in xml_delim_tokens:
        # /> (xml open-tag self-end)
        if (current_token == '/>'):
          #print(f"Stored token as xmlSlfEnd {current_token}")
          token_stack.insert(token_line_number, 'XMLSLFEND', current_token.upper())
          is_processing_xml = False # end of tag

        # </ (xml close-tag start)
        elif (current_token == '</'):
          #print(f"Stored token as xmlClsStrt {current_token}")
          token_stack.insert(token_line_number, 'XMLCLSSTRT', current_token.upper())
          is_processing_xml = True  # still processing

        # < (xml open-tag start)
        elif current_token == '<':
          #print(f"Stored token as xmlOpnStrt {current_token}")
          token_stack.insert(token_line_number, 'XMLOPNSTRT', current_token.upper())
          is_processing_xml = True  # still processing

        # > (xml tag-end)
        elif current_token == '>':
          #print(f"Stored token as xmlTagEnd {current_token}")
          token_stack.insert(token_line_number, 'XMLTAGEND', current_token.upper())
          is_processing_xml = False # end of tag

        pos += len(current_token)
        current_token = None
        continue


      # the current_token is a reserved token and needs to be stored ... don't store new-lines
      elif current_token.upper() in all_reserved_tokens:
        # new line tokens previously counted line number, but shouldn't be stored
        if all_reserved_tokens[current_token.upper()].upper() == "NL":
          pos += len(current_token)
          current_token = None
          continue

        # handle operators differently
        elif all_reserved_tokens[current_token.upper()].upper() == "OP":
          # built in operators: +, -, *, /, **, //, %, +=, -=, *=, /=, =
          if str(current_token) + str(script[min(pos+1, script_length-1)]) in ['+=', '-=', '*=', '/=', '//']:  # this is a multi-char operator
            current_token = current_token + script[min(pos+1, script_length-1)] # store mutli-char operator as current_token
              
          # store the operator token
          #print(f"Stored token as reserved token {all_reserved_tokens[current_token.upper()]} {current_token}")
          token_stack.insert(token_line_number, all_reserved_tokens[current_token.upper()].upper(), current_token.upper())
          pos += len(current_token)
          current_token = None
          continue
          
        else: # default reserved token procedure
          #print(f"Stored token as reserved token {all_reserved_tokens[current_token.upper()]} {current_token}")
          token_stack.insert(token_line_number, all_reserved_tokens[current_token.upper()].upper(), current_token.upper())
          pos += len(current_token)
          current_token = None
          continue


      # generic arg token
      else:
        #print(f"Stored token as generic arg {current_token}")
        token_stack.insert(token_line_number, "ARG", current_token)
        pos += len(current_token)
        current_token = None
        continue

  # insert an end of script token
  token_stack.insert(token_line_number + 1, 'SCPTEND', '')
  
  """
  print(f"\n{script}\n")
  """
  print("TOKEN STACK:\n")
  for item in token_stack.stack:
    print(item)
  print('\n')


  # print tokenizer warnings then clear
  if len(neh.warnings) != 0:
    print('TOKENIZER WARNINGS:')
    for warning in neh.warnings:
      print(warning)
    neh.warnings.clear()
  
  return ((token_stack, script_name))
