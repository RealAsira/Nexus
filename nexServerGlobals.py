
# ALL reserved symbols and keywords in the language
allReservedTokens:dict = {
  # Misc
  ' ': 'whitespace',
  '\n': 'nl',
  '\\': 'escNxt',   #single \ to escape next char
  '#': 'lnCmt',     #single line comment
  '/*': 'cmtStrt',  #multi-line comment
  '*/': 'cmtEnd',

  # Expression
  '@': 'exprStrt',    #special char to start expr
  ':': 'exprType',    #assign type to var, func, method
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
  'notAny': 'ref',    #!(@any)... @not(@any(...))
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

  'date': 'ref',    #@date('12/25/2025', '13:05:17:999') returns date as float .. @now() if no arg
  'now': 'ref',     #datetime right now as float
  'today': 'ref',   #date with 00:00:00 time as float

  'guid': 'ref',    #returns global identifier string
  'random': 'ref',  #@random(967) returns int 0-967 .. @random(451.07) returns float 0.00-451.07 

  'def': 'ref',       #function
  'global': 'ref',    #gets a module level or global var for the function
  'nonlocal': 'ref',  #gets a var one scope above the function
  'print': 'ref',
  'return': 'ref',

  'class': 'ref',
  'object': 'ref',
  'self': 'ref',

  'library': 'ref',
  'use': 'ref',

  'tern': 'ref',      #ternary
  'if': 'ref',        #execute def if expr evals to true
  'switch': 'ref',    #switch block
  'when': 'ref',      #when the expr in switch evals to this
  'else': 'ref',      #when the expr in switch evals to none of the whens

  'const': 'ref',     #immutable, non-reassignable var
  'var': 'ref',       #mutable unless type explicitly stated in declaration

  # Types
  'any': 'type',      #a generic type that will attempt to determine the actual type when called
  'blank': 'type',    #value is "empty" or "blank"
  'null': 'type',     #has no value, not even blank
  'none': 'type',     #func/method doesn't return a value
  'str': 'type',
    
  'array': 'type',      #data structure array
  'dict': 'type',       #data structure dictionary
  'ref': 'type',        #points to another expression
    
  'bool': 'type',
  'datetime': 'type',
  'numb': 'type',       #super type of both int and float... generic number container than handles eitehr
  'int': 'type',        #trunc decimals to make whole number (signed)
  'float': 'type',      
  'double': 'type',     #subtype of float.. currently no difference)
  'money': 'type',      #subtype of float.. returns 0.00 format

  'base64': 'type',     #encoded data in base64
  'binary': 'type',     #encoded data in binary
  'hex': 'type',        #encoded data in hex
  'utf8': 'type',       #encoded data in UTF8
    
  # Special Args (args to modify behavior of expression)
  'global': 'spArg',      #makes this variable globally scoped
  'disable': 'spArg',     #disables this block entirely
  'nointerpret': 'spArg', #returns block as string literal
}


# built-in references pointing to built-in functionality
refTypeTokens = {
  # Binary-ish Comparison
  'all': 'ref',       #@all() - ie several chained &&    
  'any': 'ref',       #several chained ||
  'either': 'ref',    #like any but only two expressions
  'notAny': 'ref',    #!(@any)... @not(@any(...))
  'neither': 'ref',   #like none but only two expressions
  'not': 'ref',       #same as !(...) but as reference eg @not(...)
  'iv': 'ref',        #value is non-null, non-blank
  'nv': 'ref',        #value is null or blank

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

  'def': 'ref',       #function
  'global': 'ref',    #gets a module level or global var for the function
  'nonlocal': 'ref',  #gets a var one scope above the function
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
}


# these tokens are concatted instead
stringDelimTokens:dict = {
  "'",  # start or end of a string
  '"',
}


# these tokens require additional processing to determine if they are comparison operators or xml/html
xmlDelimTokens:dict = {
  '<',  # possible xml open-tag start
  '>',  # possible xml open-tag end
  '/>', # xml open-tag self-close
  '/',  # first char in /> ..
  '</', # xml close-tag start
}
