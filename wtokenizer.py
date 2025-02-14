"""
TOKENIZER/LEXER CREATES "TOKENS" FROM SCRIPT

// example...
@func add (num1(int, float), num2(int, float)) {
  @print('goodnight sky');
}

/*expected token output

@               -expression start
func            -expression pointer
add             -expression name  (technically an arg)
(               -args start
num1            -arg
int             -type
float           -type
num2            -arg
int             -type
float           -type
)               -args end
{               -definition start
@               -expression start
print           -expression pointer
'goodnight sky' -arg
;               -expression end
}               -definition end
(newline)       -expression end

*/
"""





# TOKENS RESERVED BY THE LANGUAGE
currentToken = None
reservedTokens = {
    # Misc
    ' ': 'whitespace',
    '\n': 'newline',
    '\\': 'escNext',      #single \ to escape next char
    '//': 'lnComment',    #single line comment
    '/*': 'commentStart', #multi-line comment
    '*/': 'commentEnd',

    # Expression
    '@': 'exprStart',     #special char to start expr
    ';': 'exprEnd',       #ends expr immediately
    ',': 'exprDelim',     #delims args in expr
    '.': 'methStart',     #start of a method (ie @bar.kill() where kill is method)

    # Structure
    '(': 'parenOpen',     #used for args
    ')': 'parenClose',  
    '{': 'braceOpen',     #use for defs
    '}': 'braceClose',  
    '[': 'bracketOpen',   #used for data
    ']': 'bracketClose',

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
    '!': 'binCompare',               #NOT - eval to inverse
    '&&': 'binCompare',              #AND - both in comparison eval to true
    #NAND = !(var1 && var 2)  #NAND - intentionally excluded for simplicity
    '||': 'binCompare',               #OR - either in comparison eval to true
    #NOR = !(var1 || var 2)   #NOR - intentionally excluded for simplicity
    'x||': 'binCompare',             #XOR - both in comparison are different
    #XNOR = !(var1 x|| var 2) #XNOR -intentionally excluded for simplicity

    # Binary-ish Comparison
    'all': 'expr',       #@all() - ie several chained &&    
    'any': 'reference',       #several chained ||
    'either': 'reference',    #like any but only two expressions
    'none': 'reference',      #!(@any)
    'neither': 'reference',   #like none but only two expressions
    'not': 'reference',       #same as !() but as reference
    'iv': 'reference',        #value is non-null, non-blank
    'nv': 'reference',        #value is null or blank

    # Operators
    '+': 'operator',    
    '-': 'operator',    
    '*': 'operator',    
    '/': 'operator',    
    '**': 'operator',   #power
    '//': 'operator',   #root
    '%': 'operator',    #modulo
    '+=': 'operator',   
    '-=': 'operator',   
    '*=': 'operator',   
    '/=': 'operator',   
    '=': 'operator',    #assign

    # Keywords (reserved references)
    'abort': 'reference',   #kill entire response w/o sending anything
    'stop': 'reference',    #stop further addition to response... parse it and send
    'cookie': 'reference',    #assign a cookie to client
    'httpGET': 'reference',   #try to get data from somewhere
    'httpPOST': 'reference',  #post something somewhere
    'output': 'reference',    #sets the current output value
    'wait': 'reference',      #

    'response_header': 'reference',
    'response_redirect': 'reference',

    'calc': 'reference',
    'min': 'reference',
    'max': 'reference',

    'chr': 'reference',
    'ord': 'reference',

    'date': 'reference',    #@date(12/25/2025 13:05:17:999) returns date as float ... @now() if no arg
    'now': 'reference',     #datetime right now as float
    'today': 'reference',   #date with 00:00:00 time as float

    'guid': 'reference',    #returns global identifier string
    'random': 'reference',  #@random(967) returns int 0-967 ... @random(451.07) returns float 0.00-451.07 

    'func': 'reference',
    'getglobal': 'reference', #gets a module level or global var for the function
    'print': 'reference',
    'return': 'reference',

    'type': 'reference',
    'class': 'reference',
    'object': 'reference',
    'this': 'reference',
    'self': 'reference',

    'library': 'reference',
    'mode': 'reference',
    'module': 'reference',

    'if': 'reference',
    'ifTrue': 'reference',
    'ifFalse': 'reference',
    'switch': 'reference',
    'when': 'reference',
    'else': 'reference',

    'const': 'reference',
    'global': 'reference',    #makes a variable or const accessible across all modules
    'var': 'reference',

    # Types
    'blank': 'type',    #value is "empty" or "blank"
    'null': 'type',     #has no value, not even blank
    'variant': 'type',  #a generic type that will attempt to determine the actual type when called
    
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

ignoreTokens = {
    ' ',
}


"""
TO DO
If  _<_ (_ replaces ' ' here) then this is chevron ...
If _<alpha then part of string (HTML) <htah />

If _> then chevron
If /> then part of string (HTML)
"""


# tokenStack is where all the tokens are stored during the tokenization phase
class tokenStack:
  def __init__(self):
    # [[tokenType, tokenValue], [tokenType, tokenValue] ...]
    self.stack = []              
    #print('created token stack')

  # add a token to end of the stack
  def insert(self, tokenType, tokenValue = 'noVal'):
    #print('stored token', tokenType, tokenValue.replace(' ', '_'))
    self.stack.insert(len(self.stack), [tokenType.strip(), tokenValue.strip()])
    return
  
  # remove the first token from the stack
  def pop (self):
    self.stack.pop(0)

  # read the first token in the stack
  def readNext(self):
    return self.stack[0]

tokenStack = tokenStack()





# TOKENIZE .wlang SCRIPTS INTO COMMAND STACK
def tokenizeScript(script):
  global reservedTokens
  global currentToken

  print(script, '\n\n\n')
  
  # loop through entire script
  for char in script:
    #print(char.replace(' ', '_'), str(currentToken).replace(' ', '_'))

    # multi-character token
    if currentToken is not None:
      currentToken = str(currentToken) + str(char)
      
      # characters or strings such as @, {}, (), ;, func, var, etc... used for syntax structure
      if currentToken in reservedTokens:
        #print('1', reservedTokens[currentToken], currentToken.replace(' ', '_'))
        tokenStack.insert(reservedTokens[currentToken], currentToken)
        currentToken = None

      # character is reserved, therefore the token is complete and is an arg
      if (char in reservedTokens):
        #print('2', 'arg', currentToken[0:(len(currentToken)-1)].replace(' ', '_'))
        tokenStack.insert('arg', currentToken[0:(len(currentToken)-1)])
        
        # because the previous token was ended by a reserved character, a new token is starting and needs to be processed
        currentToken = tokenizeNewChar(char)


    # a brand new token to process
    elif currentToken is None:
      currentToken = tokenizeNewChar(char)

  print("Token Stack:\n")
  for item in tokenStack.stack:
    print(item)





# START OF A NEW TOKEN
def tokenizeNewChar(char):
  global reservedTokens
  global currentToken

  currentToken = char
  # add reserved token, unless it should be ignored (such as white space, delimiters, newlines)
  if (currentToken in reservedTokens) and (currentToken not in ignoreTokens):
    #print('3', reservedTokens[currentToken], currentToken.replace(' ', '_'))
    tokenStack.insert(reservedTokens[currentToken], currentToken)
    currentToken = None

  # this line ensures whitespace is not part of other tokens (such as arg tokens)
  if currentToken in ignoreTokens:
    currentToken = None

  return currentToken
