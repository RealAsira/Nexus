
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
  #'ALL': 'ref',       #@all() - ie several chained &&    
  #'ANY': 'ref',       #several chained ||
  #'EITHER': 'ref',    #like any but only two expressions
  #'NOTANY': 'ref',    #!(@any)... @not(@any(...))
  #'NEITHER': 'ref',   #like none but only two expressions
  #'NOT': 'ref',       #same as !() but as reference
  'IV': 'ref',        #value is non-null, non-blank
  'NV': 'ref',        #value is null or blank

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
  'ABORT': 'ref',     #kill entire response w/o sending anything
  'STOP': 'ref',      #stop further addition to response.. parse it and send
  'COOKIE': 'ref',    #assign a cookie to client
  'HTTPGET': 'ref',   #try to get data from somewhere
  'HTTPPOST': 'ref',  #post something somewhere
  'OUTPUT': 'ref',    #sets the current output value
  'SLEEP': 'ref',     #time before continuing response
  'WAIT': 'ref',      #time before continuing ANY responses

  'RSPNS_HEADER': 'ref',
  'RSPNS_REDIR': 'ref',

  'CALC': 'ref',
  'MIN': 'ref',
  'MAX': 'ref',

  'CHR': 'ref',
  'ORD': 'ref',

  'DATE': 'ref',    #@date('12/25/2025', '13:05:17:999') returns date as float .. @now() if no arg
  'NOW': 'ref',     #datetime right now as float
  'TODAY': 'ref',   #date with 00:00:00 time as float

  'GUID': 'ref',    #returns global identifier string
  'RANDOM': 'ref',  #@random(967) returns int 0-967 .. @random(451.07) returns float 0.00-451.07 

  'DEF': 'ref',       #function
  'GETGLOBAL': 'ref',    #gets a module level or global var for the function
  'NONLOCAL': 'ref',  #gets a var one scope above the function
  'PRINT': 'ref',
  'RETURN': 'ref',

  'CLASS': 'ref',
  'OBJECT': 'ref',
  'SELF': 'ref',

  'LIBRARY': 'ref',
  'USE': 'ref',

  'TERN': 'ref',      #ternary
  'IF': 'ref',        #execute def if expr evals to true
  'SWITCH': 'ref',    #switch block
  'WHEN': 'ref',      #when the expr in switch evals to this
  'ELSE': 'ref',      #when the expr in switch evals to none of the whens

  'CONST': 'ref',     #immutable, non-reassignable var
  'VAR': 'ref',       #mutable unless type explicitly stated in declaration

  # Types
  'ANY': 'type',      #a generic type that will attempt to determine the actual type when called
  'BLANK': 'type',    #value is "empty" or "blank"
  'NULL': 'type',     #has no value, not even blank
  'STR': 'type',
    
  'LIST': 'type',       #data structure array/list
  'DICT': 'type',       #data structure dictionary/object
  'REF': 'type',        #points to another expression
    
  'BOOL': 'type',
  'DATETIME': 'type',
  'NUMB': 'type',       #super type of both int and float... generic number container than handles eitehr
  'INT': 'type',        #trunc decimals to make whole number (signed)
  'FLOAT': 'type',      
  'DOUBLE': 'type',     #subtype of float.. currently no difference)
  'MONEY': 'type',      #subtype of float.. returns 0.00 format

  'BASE64': 'type',     #encoded data in base64
  'BINARY': 'type',     #encoded data in binary
  'HEX': 'type',        #encoded data in hex
  'UTF8': 'type',       #encoded data in UTF8
    
  # Special Args (args to modify behavior of expression)
  'GLOBAL': 'spArg',      #makes this variable globally scoped
  'DISABLE': 'spArg',     #disables this block entirely
  'NOINTERPRET': 'spArg', #returns block as string literal
}


# these types are built into Nexus
exprTypeTokens = {
  # Nexus Primitive Types
  'ANY': 'type',      #a generic type that will attempt to determine the actual type when called
  'BLANK': 'type',    #value is "empty" or "blank"
  'NULL': 'type',     #has no value, not even blank
  'STR': 'type',
    
  'LIST': 'type',       #data structure array/list
  'DICT': 'type',       #data structure dictionary/object
  'REF': 'type',        #points to another expression
    
  'BOOL': 'type',
  'DATETIME': 'type',
  'NUMB': 'type',       #super type of both int and float... generic number container than handles eitehr
  'INT': 'type',        #trunc decimals to make whole number (signed)
  'FLOAT': 'type',      
  'DOUBLE': 'type',     #subtype of float.. currently no difference)
  'MONEY': 'type',      #subtype of float.. returns 0.00 format

  'BASE64': 'type',     #encoded data in base64
  'BINARY': 'type',     #encoded data in binary
  'HEX': 'type',        #encoded data in hex
  'UTF8': 'type',       #encoded data in UTF8
}


# built-in references pointing to built-in functionality
refTokens = {
  # Binary-ish Comparison
  #'ALL': 'ref',       #@all() - ie several chained &&    
  #'ANY': 'ref',       #several chained ||
  #'EITHER': 'ref',    #like any but only two expressions
  #'NOTANY': 'ref',    #!(@any)... @not(@any(...))
  #'NEITHER': 'ref',   #like none but only two expressions
  #'NOT': 'ref',       #same as !() but as reference
  'IV': 'ref',        #value is non-null, non-blank
  'NV': 'ref',        #value is null or blank

  # Keywords (reserved references)
  'ABORT': 'ref',     #kill entire response w/o sending anything
  'STOP': 'ref',      #stop further addition to response.. parse it and send
  'COOKIE': 'ref',    #assign a cookie to client
  'HTTPGET': 'ref',   #try to get data from somewhere
  'HTTPPOST': 'ref',  #post something somewhere
  'OUTPUT': 'ref',    #sets the current output value
  'SLEEP': 'ref',     #time before continuing response
  'WAIT': 'ref',      #time before continuing ANY responses

  'RSPNS_HEADER': 'ref',
  'RSPNS_REDIR': 'ref',

  'CALC': 'ref',
  'MIN': 'ref',
  'MAX': 'ref',

  'CHR': 'ref',
  'ORD': 'ref',

  'DATE': 'ref',    #@date('12/25/2025', '13:05:17:999') returns date as float .. @now() if no arg
  'NOW': 'ref',     #datetime right now as float
  'TODAY': 'ref',   #date with 00:00:00 time as float

  'GUID': 'ref',    #returns global identifier string
  'RANDOM': 'ref',  #@random(967) returns int 0-967 .. @random(451.07) returns float 0.00-451.07 

  'DEF': 'ref',       #function
  'GETGLOBAL': 'ref',    #gets a module level or global var for the function
  'NONLOCAL': 'ref',  #gets a var one scope above the function
  'PRINT': 'ref',
  'RETURN': 'ref',

  'CLASS': 'ref',
  'OBJECT': 'ref',
  'SELF': 'ref',

  'LIBRARY': 'ref',
  'USE': 'ref',

  'TERN': 'ref',      #ternary
  'IF': 'ref',        #execute def if expr evals to true
  'SWITCH': 'ref',    #switch block
  'WHEN': 'ref',      #when the expr in switch evals to this
  'ELSE': 'ref',      #when the expr in switch evals to none of the whens

  'CONST': 'ref',     #immutable, non-reassignable var
  'VAR': 'ref',       #mutable unless type explicitly stated in declaration
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
