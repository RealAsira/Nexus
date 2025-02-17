"""
TOKENIZER/LEXER CREATES "TOKENS" FROM A SCRIPT
"""


#which line the token is on ... starts at 1
lineNumber = 1

# TOKENS RESERVED BY THE LANGUAGE
currentToken = None
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
  '.': 'methStrt',    #start of a method (ie @bar.kill() where kill is method)

  # Structure
  '(': 'parenOpn',    #used for args
  ')': 'parenCls',  
  '{': 'braceOpn',    #used for defs
  '}': 'braceCls',  
  '[': 'bracketOpn',  #used for data
  ']': 'bracketCls',
  '\'': 'apos',       #used for strings
  '"': 'quote',       #used for strings

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
  'stop': 'ref',      #stop further addition to response... parse it and send
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

  'date': 'ref',    #@date(12/25/2025 13:05:17:999) returns date as float ... @now() if no arg
  'now': 'ref',     #datetime right now as float
  'today': 'ref',   #date with 00:00:00 time as float

  'guid': 'ref',    #returns global identifier string
  'random': 'ref',  #@random(967) returns int 0-967 ... @random(451.07) returns float 0.00-451.07 

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

  'if': 'ref',        #ternary
  'ifTrue': 'ref',    #execute def if expr evals to true
  'ifFalse': 'ref',   #execute def if expr evals to false
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
  'double': 'type',   #subtype of float... currently no difference)
  'money': 'type',    #subtype of float... returns 0.00 format

  'base64': 'type',   #encoded data in base64
  'binary': 'type',   #encoded data in binary
  'hex': 'type',      #encoded data in hex
  'utf8': 'type',     #encoded data in UTF8
    
  # Special Args (args to modify behavior of expression)
  'disable': 'spArg',
  'nointerpret': 'spArg',
  'protected': 'spArg',
}

# these tokens aren't added to the token array
ignoreTokens = {
  ' ',
}

# these tokens are concatted instead
stringDelimTokens = {
  '\'',   # start or end of a string
  '"',    # start or end of a string
}





# tokenStack is where all the tokens are stored during the tokenization phase
class tokenStack:
  def __init__(self):
    # [[lineNumber, tokenType, tokenValue], [tokenType, tokenValue] ...]
    self.stack = []              
    #print('created token stack')

  # add a token to end of the stack
  def insert(self, lineNumber, tokenType, tokenValue):
    #print('stored token', tokenType, tokenValue.replace(' ', '_'))
    self.stack.insert(len(self.stack), [int(lineNumber), tokenType.strip(), tokenValue.strip()])
    return
  
  # remove the first token from the stack
  def pop (self):
    self.stack.pop(0)

  # read the first token in the stack
  def readNext(self):
    return self.stack[0]

tokenStack = tokenStack()





def tokenizeScript(script):
  print(script, '\n\n\n')

  global currentToken
  global reservedTokens
  global ignoreTokens
  global stringDelimTokens
  global lineNumber #which line the token is on ... starts at 1
  processingStr = False   #ignore reserved tokens until the string is closed

  #insert a token indicating the start of a tokenized script
  tokenStack.insert(0, 'scptStrt', '')
  
  # loop through entire script
  for char in script:
    #print(currentToken, char, processingStr)

    #new token
    if currentToken is None:
      currentToken = tokenizeNewChar(char)
      if currentToken in stringDelimTokens: processingStr = True  #now processing a string
      continue

    #multi-char token
    elif currentToken is not None:
      currentToken = str(currentToken) + str(char)  #append new char

      #the current token is a multi-char token that exists in reserved tokens
      #eg func, var, return, print, etc
      if currentToken in reservedTokens:
        #print('inserted token as multi char reserved token:', reservedTokens[currentToken], currentToken)
        tokenStack.insert(lineNumber, reservedTokens[currentToken], currentToken)
        currentToken = None
        continue

      #current token is a string
      elif processingStr:
        if char in ignoreTokens: continue #space char already added, goto next char
        if char in stringDelimTokens:
          if char != currentToken[0]: continue #wrong delimiter to end string
          if currentToken[len(currentToken)-1] == '\\': continue #end string delim is escaped
          else: #store string
            #print('inserted token as string:', currentToken)
            tokenStack.insert(lineNumber, 'arg', currentToken)
            processingStr = False #string has ended
            currentToken = None   #string was stored, end token
            continue
      
      #current char is a space, indicating the multi-char generic arg is over
      elif char == ' ':
        #print('inserted token as generic arg:', currentToken)
        tokenStack.insert(lineNumber, 'arg', currentToken[0:len(currentToken)-1])
        
        #start new token because previous was just ended
        currentToken = tokenizeNewChar(char)
        if currentToken in stringDelimTokens: processingStr = True  #now processing a string
        continue

      #the current char is a reserved token, this indicates end of current token and start of a new one
      elif char in reservedTokens:
        tokenStack.insert(lineNumber, 'arg', currentToken[0:(len(currentToken)-1)])
        currentToken = tokenizeNewChar(char)
        if currentToken in stringDelimTokens: processingStr = True #a string has started

      else: continue #character was appended to token

  #insert a token indicating the end of a script
  #len statement gets last token's line number, adds one
  tokenStack.insert(tokenStack.stack[len(tokenStack.stack)-1][0]+1, 'scptEnd', '')
  
  print("TOKEN STACK:\n")
  for item in tokenStack.stack:
    print(item)





def tokenizeNewChar(char):
  global currentToken
  global reservedTokens
  global ignoreTokens
  global stringDelimTokens
  global lineNumber #which line the token is on ... starts at 1
  processingStr = False   #ignore reserved tokens until the string is closed
  
  currentToken = char
  if currentToken == '\n': lineNumber += 1  #increment line number where tokens are at

  #new char is in ignore list... skip it
  if currentToken in ignoreTokens:
    currentToken = None 
    return currentToken
  
  #new char starts non-reserved token of type "arg"
  if currentToken not in reservedTokens:
    return currentToken
  
  #new char is a reserved token in and of itself
  if currentToken in reservedTokens:
    if currentToken in stringDelimTokens: return currentToken #start of a string
    #ADD HTML vs COMPARISON TOKENS HERE
    #ADD HTML vs COMPARISON TOKENS HERE
    #ADD HTML vs COMPARISON TOKENS HERE
    
    # all possible special conditions (strings, html, etc) have been tested already... this is simply a reserved token and nothing more
    else:
      #print('inserted token as single char reserved token:', reservedTokens[currentToken], currentToken)
      tokenStack.insert(lineNumber, reservedTokens[currentToken], currentToken)
      currentToken = None
      return currentToken
