"""
TOKENIZER/LEXER CREATES "TOKENS" FROM A SCRIPT
"""

import nexServerGlobals
allReservedTokens = nexServerGlobals.allReservedTokens
exprTypeTokens = nexServerGlobals.exprTypeTokens
stringDelimTokens = nexServerGlobals.stringDelimTokens
xmlDelimTokens = nexServerGlobals.xmlDelimTokens
refTokens = nexServerGlobals.refTokens





# the stack all tokens are stored in
class tokenStack:
  def __init__(self):
    # [[lineNumber, tokenType, tokenValue], .., ..]
    self.stack = []

  # add token to end of stack
  def insert(self, lineNumber:int, tokenType:str, tokenValue):
    #print(f"Stored token from line", lineNumber, 'as', tokenType, tokenValue)
    self.stack.insert(len(self.stack), [int(lineNumber), tokenType.strip().upper(), tokenValue.strip()])
  
  # remove token from stack (first by default)
  def pop(self, pos:int=0):
    self.stack.pop(pos)
  
  # return first token in stack
  def readCurrentToken(self):
    return self.stack[0]
  
  # the tokenStack is reused and needs to be cleared between uses
  def clear(self):
    self.stack.clear()
  
tokenStack = tokenStack()
  




# process to tokenize a submitted script
def tokenizeScript(script:str, scriptName:str = "Unknown Nexus Module") -> object:
  global allReservedTokens, stringDelimTokens, xmlDelimTokens
  #global exprTypeTokens
  #global refTokens

  currentToken:str = None
  tokenLineNumber:int = 1         # file line number for where token is at
  processingStr:bool = False      # currently processing a string token
  processingStrDelim:chr = None   # " or '
  processingFStr:bool = False     # currently processing a functional / formatted string token
  processingXML:bool = False      # currently processing an xml token

  scriptLen:int = len(script)     # total length of the script
  pos:int = 0                     # position where is being processed


  # returns the position of the next single character token
  def findNextReservedSingleCharToken(searchToken:str = None) -> int:
    nonlocal script
    nonlocal pos
    cursor:int = pos

    while True:
      if cursor < scriptLen:

        # searching for any reserved token
        if not searchToken:
          if script[cursor].upper() in allReservedTokens:
            break # found match
          else: cursor += 1

        # searching for a specific reserved token
        if searchToken:
          if script[cursor].upper() == searchToken:
            break # found match
          else: cursor +=1
          
      else:
        cursor = scriptLen  #end of script is last char
        break
    
    return cursor



  # gets and returns the next token
  def getToken() -> str:
    nonlocal script, tokenLineNumber, processingStr, processingStrDelim, processingFStr, processingXML
    
    aToken:str = str(script[pos].upper())
    
    # new-line = inc line number
    if aToken == '\n':
      tokenLineNumber += 1
      #print(f"a. Found token newline")
      return aToken
    

    # this is the start of a string
    elif aToken in stringDelimTokens:
      # currently processing a string AND end delim match start delim .. end of string unless escaped
      if processingStr and (aToken == processingStrDelim):
        isEscaped = True if script[pos-1] == '\\' else False

        # if it is escaped, continue processing string; otherwise, is end of string
        if not isEscaped:
          processingStr = False
          processingFStr = False
          processingStrDelim = None # no longer processing

      elif not processingStr:
        processingStr = True
        processingStrDelim = aToken
        if script[pos-1].upper() == 'F':
          processingFStr = True   # this is a formatted/functional string

      #print(f"b. Found token {aToken}")
      return aToken


    # this token is either XML or comparison
    elif aToken in xmlDelimTokens:
      # +1 to get next pos, -1 to get set script last char bound
      nextChar:str = str(script[min(pos+1, scriptLen-1)]).upper()

      if nextChar not in allReservedTokens: processingXML = True
      if nextChar == '/': processingXML = True  # / is reservered, but </ is xml-close tag start

      if not processingXML: # comparison operator
        processingXML = False
        #print(f"g. Found token {aToken}")
        return aToken

      elif processingXML:
        # /> (xml open-tag self-end)
        if (str(aToken) + str(nextChar) == '/>'):
          aToken = aToken + nextChar  # get /> instead of /
          #print(f"h. Found token {aToken}")
          return aToken
        
        # </ (xml close-tag start)
        elif (str(aToken) + str(nextChar) == '</'):
          aToken = aToken + nextChar  # get </ instead of <
          #print(f"h. Found token {aToken}")
          return aToken
        
        # < (xml open-tag start)
        elif aToken == '<':
          #print(f"h. Found token {aToken}")
          return aToken
        
        # > (xml tag-end)
        elif aToken == '>':
          #print(f"h. Found token {aToken}")
          return aToken

        else:
          raise Exception('XML token-type lookup error:', aToken)

          
    # reserved single char token (including space delim)
    elif aToken.upper() in allReservedTokens:
      #print(f"c. Found token {aToken.replace(' ', '_')}")
      return aToken


    # multi-character reserved or generic arg..
    else:
      # simply find end of this token by getting start of next
      if not processingStr and not processingFStr:
        endPos:int = findNextReservedSingleCharToken()
        aToken = script[pos:endPos]
        #print(f"d. Found token {aToken}")

      # vanilla string
      if processingStr and not processingFStr:     
        endPos:int = findNextReservedSingleCharToken(processingStrDelim)
        aToken = script[pos:endPos]
        #print(f"e. Found token {aToken}")

      # functional string - tokenize each possible token in it
      if processingStr and processingFStr:
        endPos:int = findNextReservedSingleCharToken()
        aToken = script[pos:endPos]
        #print(f"f. Found token {aToken}")

      return aToken



  # reset the stack and insert scptStrt
  tokenStack.clear()
  tokenStack.insert(0, 'scptStrt', '')



  while True:
  # PROCESS SCRIPT INTO TOKENS
    # full script has been processed
    if pos >= scriptLen:
      break
    
    # new token
    if currentToken is None:
      currentToken = getToken() # now that the token is found, the next step will store it
      #print(f"New token found: {currentToken})


      # space character delims tokens ... doesn't get stored
      if currentToken == ' ':
        pos += 1
        currentToken = None
        continue


      # the currentToken is a string delimiter
      elif currentToken in stringDelimTokens:
        # processingStr is toggled in getToken. If true, then a str just started..
        if processingStr:
          isEscaped:bool = True if script[pos-1] == '\\' else False

          if isEscaped:
            tokenStack.insert(tokenLineNumber, allReservedTokens[currentToken].upper(), currentToken.upper())
  
          elif not isEscaped:
            #print(f"Stored token as strStrt {currentToken}")
            tokenStack.insert(tokenLineNumber, "STRSTRT", currentToken.upper())
          
        elif not processingStr:
          #print(f"Stored token as strEnd {currentToken}")
          tokenStack.insert(tokenLineNumber, "STREND", currentToken.upper())

        pos += len(currentToken)
        currentToken = None
        continue


      # the current token is an XML tag of some kind instead of comparison operator
      elif processingXML and currentToken in xmlDelimTokens:
        # /> (xml open-tag self-end)
        if (currentToken == '/>'):
          #print(f"Stored token as xmlSlfEnd {currentToken}")
          tokenStack.insert(tokenLineNumber, 'XMLSLFEND', currentToken.upper())
          processingXML = False # end of tag

        # </ (xml close-tag start)
        elif (currentToken == '</'):
          #print(f"Stored token as xmlClsStrt {currentToken}")
          tokenStack.insert(tokenLineNumber, 'XMLCLSSTRT', currentToken.upper())
          processingXML = True  # still processing

        # < (xml open-tag start)
        elif currentToken == '<':
          #print(f"Stored token as xmlOpnStrt {currentToken}")
          tokenStack.insert(tokenLineNumber, 'XMLOPNSTRT', currentToken.upper())
          processingXML = True  # still processing

        # > (xml tag-end)
        elif currentToken == '>':
          #print(f"Stored token as xmlTagEnd {currentToken}")
          tokenStack.insert(tokenLineNumber, 'XMLTAGEND', currentToken.upper())
          processingXML = False # end of tag

        pos += len(currentToken)
        currentToken = None
        continue


      # the currentToken is a reserved token and needs to be stored
      elif currentToken.upper() in allReservedTokens:
        #print(f"Stored token as reserved token {reservedTokens[currentToken]} {currentToken}")
        tokenStack.insert(tokenLineNumber, allReservedTokens[currentToken.upper()].upper(), currentToken.upper())
        pos += len(currentToken)
        currentToken = None
        continue


      # generic arg token
      else:
        #print(f"Stored token as generic arg {currentToken}")
        tokenStack.insert(tokenLineNumber, "ARG", currentToken)
        pos += len(currentToken)
        currentToken = None
        continue

  # insert an end of script token
  tokenStack.insert(tokenLineNumber + 1, 'SCPTEND', '')
  
  """
  print(f"\n{script}\n")
  print("TOKEN STACK:\n")
  for item in tokenStack.stack:
    print(item)
  print('\n')
  """
  
  return (tokenStack)
