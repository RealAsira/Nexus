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
    # tokenType, tokenValue
    ' ': 'whitespace',
    '\n': 'newline',
    '@': 'expressionStart',
    '(': 'argumentsStart',
    ')': 'argumentsEnd',
    '{': 'definitionStart',
    '}': 'definitionEnd',
    ';': 'expressionEnd',
    ',': 'delimiter',
    'func': 'reference',
    'int': 'type',
    'float': 'type',
}

ignoreTokens = {
    ' ',
}





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
