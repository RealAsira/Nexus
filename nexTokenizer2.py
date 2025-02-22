"""
TOKENIZER/LEXER CREATES "TOKENS" FROM A SCRIPT
"""





# custom message for tokenizer errors
class customErr(Exception):
  def __init__(self,msg):
    super().__init__(msg)





# reserved symbols and keywords in the language
reservedTokens = {
  # Misc
  ' ': 'whitespace',
  '\n': 'nl',
  '\\': 'escNxt',   #single \ to escape next char
  '#': 'lnCmt',    #single line comment
  '/*': 'cmtStrt',  #multi-line comment
  '*/': 'cmtEnd',

  # Expression
  '@': 'exprStrt',    #special char to start expr
  ';': 'exprEnd',     #ends expr immediately
  ',': 'exprDlm',     #delims args in expr
  '.': 'methStrt',    #start of a method (ie @bar.destroy() where destroy is method)

  # Structure
  '(': 'parenOpn',    #used for args
  ')': 'parenCls',  
  '{': 'braceOpn',    #used for defs
  '}': 'braceCls',  
  '[': 'bracketOpn',  #used for data
  ']': 'bracketCls',  
  '"': 'quote',       #used for strings .. yes, they need to be stored here too
  "'": 'apos',

  # Comparison
  '<': 'lsThan',      
  '>': 'gtThan',
  '>=': 'gtThanEqTo',
  '<=': 'lsThanEqTo',
  '==': 'eqTo',             #compare
  '!==': 'notEqTo',         #compare NOT
  '===': 'eqToStrict',      #compare strict
  '!===': 'notEqToStrict',  #comapre strict NOT

  # Binary Comparison
  '!': 'binCmpr',               #NOT - eval to inverse
  '&&': 'binCmpr',              #AND - both in comparison eval to true
  #NAND = !(var1 && var 2)  #NAND - intentionally excluded for simplicity
  '||': 'binCmpr',               #OR - either in comparison eval to true
  #NOR = !(var1 || var 2)   #NOR - intentionally excluded for simplicity
  'x||': 'binCmpr',             #XOR - both in comparison are different
  #XNOR = !(var1 x|| var 2) #XNOR -intentionally excluded for simplicity

  # Binary-ish Comparison
  'all': 'ref',       #@all() - ie several chained &&    
  'any': 'ref',       #several chained ||
  'either': 'ref',    #like any but only two expressions
  'none': 'ref',      #!(@any)
  'neither': 'ref',   #like none but only two expressions
  'not': 'ref',       #same as !() but as reference
  'iv': 'ref',        #value is non-null, non-blank
  'nv': 'ref',        #value is null or blank

  # Operators
  '+': 'op',    
  '-': 'op',    
  '*': 'op',    
  '/': 'op',    
  '**': 'op',   #power
  '//': 'op',   #root
  '%': 'op',    #modulo
  '+=': 'op',   
  '-=': 'op',   
  '*=': 'op',   
  '/=': 'op',   
  '=': 'op',    #assign

  # Keywords (reserved references)
  'abort': 'ref',     #kill entire response w/o sending anything
  'stop': 'ref',      #stop further addition to response.. parse it and send
  'cookie': 'ref',    #assign a cookie to client
  'httpGET': 'ref',   #try to get data from somewhere
  'httpPOST': 'ref',  #post something somewhere
  'output': 'ref',    #sets the current output value
  'sleep': 'ref',     #sleep? should this be in lang?
  'wait': 'ref',      #wait? should this be in lang?

  'rspns_header': 'ref',
  'rspns_redir': 'ref',

  'calc': 'ref',
  'min': 'ref',
  'max': 'ref',

  'chr': 'ref',
  'ord': 'ref',

  'date': 'ref',    #@date(12/25/2025 13:05:17:999) returns date as float .. @now() if no arg
  'now': 'ref',     #datetime right now as float
  'today': 'ref',   #date with 00:00:00 time as float

  'guid': 'ref',    #returns global identifier string
  'random': 'ref',  #@random(967) returns int 0-967 .. @random(451.07) returns float 0.00-451.07 

  'func': 'ref',
  'getglobal': 'ref', #gets a module level or global var for the function
  'print': 'ref',
  'return': 'ref',

  'type': 'ref',
  'class': 'ref',
  'object': 'ref',
  'this': 'ref',
  'self': 'ref',

  'library': 'ref',
  'mode': 'ref',
  'module': 'ref',

  'tern': 'ref',      #ternary
  'if': 'ref',        #execute def if expr evals to true
  'switch': 'ref',    #switch block
  'when': 'ref',      #when the expr in switch evals to this
  'else': 'ref',      #when the expr in switch evals to none of the whens

  'const': 'ref',     #immutable, non-reassignable var
  'global': 'ref',    #makes a variable or const accessible across all modules
  'var': 'ref',       #mutable unless type explicitly stated in declaration

  # Types
  'blank': 'type',    #value is "empty" or "blank"
  'null': 'type',     #has no value, not even blank
  'variant': 'type',  #a generic type that will attempt to determine the actual type when called
  'str': 'type',
    
  'array': 'type',      #data structure array
  'dict': 'type',       #data structure dictionary
  'reference': 'type',  #points to another expression
    
  'bool': 'type',
  'datetime': 'type',
  'int': 'type',      #trunc decimals to make whole number
  'float': 'type',
  'double': 'type',   #subtype of float.. currently no difference)
  'money': 'type',    #subtype of float.. returns 0.00 format

  'base64': 'type',   #encoded data in base64
  'binary': 'type',   #encoded data in binary
  'hex': 'type',      #encoded data in hex
  'utf8': 'type',     #encoded data in UTF8
    
  # Special Args (args to modify behavior of expression)
  'disable': 'spArg',
  'nointerpret': 'spArg',
  'protected': 'spArg',
}

# these tokens are concatted instead
stringDelimTokens = {
  "'",  # start or end of a string
  '"',
}

# these tokens require additional processing to determine if they are comparison operators or xml/html
xmlDelimTokens = {
  '<',  # possible xml open-tag start
  '>',  # possible xml open-tag end
  '/>', # xml open-tag self-close
  '/',  # first char in /> ..
  '</', # xml close-tag start
}





# the stack all tokens are stored in
class tokenStack:
  def __init__(self):
    # [[lineNumber, tokenType, tokenValue], .., ..]
    self.stack = []

  # add token to end of stack
  def insert(self, lineNumber, tokenType, tokenValue):
    #print(f"Stored token", lineNumber, tokenType, tokenValue)
    self.stack.insert(len(self.stack), [int(lineNumber), tokenType.strip(), tokenValue.strip()])
    return
  
  # remove first token from stack
  def pop(self):
    self.stack.pop(0)
  
  # return first token in stack
  def readCurrentToken(self):
    return self.stack[0]
  
  # the tokenStack is reused and needs to be cleared between uses
  def clear(self):
    self.stack.clear()
  
tokenStack = tokenStack()
  




# process to tokenize a submitted script
def tokenizeScript(script, scriptName:str = "Unknown Nexus Module"):
  print(f"{script}\n\n\n")

  global currentToken
  global reservedTokens
  global stringDelimTokens
  global xmlDelimTokens

  currentToken = None
  tokenLineNumber = 1
  processingStr = False
  processingStrDelim = None
  processingXML = False

  scriptLen = len(script) # total length of the script
  pos = 0                 # position where is being processed


  # returns the position of the next single character token
  def findNextReservedSingleCharToken(searchToken:str = None) -> int:
    nonlocal script
    nonlocal pos
    cursor = pos

    while True:
      if cursor < scriptLen:

        # searching for any reserved token
        if not searchToken:
          if script[cursor] in reservedTokens:
            break # found match
          else: cursor += 1

        # searching for a specific reserved token
        if searchToken:
          if script[cursor] == searchToken:
            break # found match
          else: cursor +=1
          
      else:
        cursor = scriptLen  #end of script is last char
        break
    
    return cursor



  # gets and returns the next token
  def getToken():
    nonlocal script
    nonlocal tokenLineNumber
    nonlocal processingStr
    nonlocal processingStrDelim
    nonlocal processingXML
    
    aToken = script[pos]
    
    # new-line = inc line number
    if aToken == '\n':
      tokenLineNumber += 1
      #print(f"a. Found token newline")
      return aToken

    # this is the start of a string
    elif aToken in stringDelimTokens:
      #print(f"b. Found token {aToken}")

      # currently processing a string AND end delim match start delim .. end of string
      if processingStr and (aToken == processingStrDelim):
        processingStr = False
        processingStrDelim = None # no longer processing, don't store
        return aToken
      
      if not processingStr:
        processingStr = True
        processingStrDelim = aToken
        return aToken

    # ADD XML DELIM STUFF HERE
    # ADD XML DELIM STUFF HERE
    # ADD XML DELIM STUFF HERE
    # ADD XML DELIM STUFF HERE

    # this token is either XML or comparison
    #elif aToken in xmlDelimTokens:
    #  ..#get info abt if this is comparison or xml


    # reserved single char token (including space delim)
    elif aToken in reservedTokens:
      #print(f"c. Found token {aToken.replace(' ', '_')}")
      return aToken

    # multi-character reserved or generic arg..
    else:
      # get entire token

      if not processingStr: # simply find end of this token by getting start of next
        endPos = findNextReservedSingleCharToken()
        aToken = script[pos:endPos]

      if processingStr:     # only certain chars should split the string
        endPos = findNextReservedSingleCharToken('"')
        aToken = script[pos:endPos]

      #print(f"d. Found token {aToken}")
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
      #print(currentToken)


      # space character delims tokens ... doesn't get stored
      if currentToken == ' ':
        pos += 1
        currentToken = None
        continue


      # the currentToken is a string delimiter
      elif currentToken in stringDelimTokens:
        # processingStr is toggled in getToken. If true, then a str just started..
        if processingStr:
          #print(f"Stored token as strStrt {currentToken}")
          tokenStack.insert(tokenLineNumber, "strStrt", currentToken)
          
        if not processingStr:
          #print(f"Stored token as strEnd {currentToken}")
          tokenStack.insert(tokenLineNumber, "strEnd", currentToken)

        pos += len(currentToken)
        currentToken = None
        continue


      # the currentToken is a reserved token and needs to be stored
      elif currentToken in reservedTokens:
        #print(f"Stored token as reserved token {reservedTokens[currentToken]} {currentToken}")
        tokenStack.insert(tokenLineNumber, reservedTokens[currentToken], currentToken)
        pos += len(currentToken)
        currentToken = None
        continue


      # generic arg token
      else:
        #print(f"Stored token as generic arg {currentToken}")
        tokenStack.insert(tokenLineNumber, "arg", currentToken)
        pos += len(currentToken)
        currentToken = None
        continue

  # insert an end of script token
  tokenStack.insert(tokenLineNumber + 1, 'scptEnd', '')
  
  print("TOKEN STACK:\n")
  for item in tokenStack.stack:
    print(item)
  
  return (tokenStack.stack)
