"""
PARSER MAKES NODES FROM TOKENS AND POPULATES ABSTRACT SYNTAX TREE (AST)
"""

import nexServerGlobals
allReservedTokens = nexServerGlobals.allReservedTokens
exprTypeTokens = nexServerGlobals.exprTypeTokens
stringDelimTokens = nexServerGlobals.stringDelimTokens
xmlDelimTokens = nexServerGlobals.stringDelimTokens
refTypeTokens = nexServerGlobals.refTypeTokens





class abstractSyntaxTree:
  def __init__(self):
    # list of dictionaries where each entry is a node
    # contains: nodeID, nodeType
    self.tree = []

  def insert(self, nodeID, nodeType):
    self.tree.insert(len(self.tree), {'nodeID': nodeID, 'nodeType': nodeType})
  
AST = abstractSyntaxTree()
  




# PARSE TOKENS from tokenizeScript) INTO ABSTRACT SYNTAX TREE
def parseTokens(tokenStack:object) -> object:
  #global allReservedTokens
  #global exprTypeTokens
  global refTypeTokens
  #global stringDelimTokens
  #global xmlDelimTokens

  # parts of a token
  currentToken:list = None    # currentToken[0] is lineNumber, [1] is tokenType, [2] is tokenValue
  tokenLineNumber:int = None  # currentToken[0]
  tokenType:str = None        # currentToken[1]
  tokenValue:any = None       # currentToken[2]
  
  # parts of a node
  nodeID:int = 1          # inc IDs so each node has a unique ID#
  nodeType:str = None     # ref, type, etc
  nodeRef:str = None      # ie var, def, calc
  nodeName:str = None     # ie var BAR, def FOO class AST
  nodeLine:int = None     # self-explanatory
  nodeArgs:list = []      # any args that node needs to function
  nodeBody:dict = {}      # child nodes



  # inc nodeID, reset temp token and node data
  def resetForNextNode() -> None:
    nonlocal currentToken
    nonlocal tokenLineNumber
    nonlocal tokenType
    nonlocal tokenValue

    currentToken = None
    tokenLineNumber = None
    tokenType = None
    tokenValue = None

    nonlocal nodeID
    nonlocal nodeType
    nonlocal nodeName
    nonlocal nodeRef
    nonlocal nodeLine
    nonlocal nodeArgs
    nonlocal nodeBody

    nodeID += 1
    nodeType = None
    nodeRef = None
    nodeName = None
    nodeLine = None
    nodeArgs = []
    nodeBody = {}



  # unpack current token into parts
  def getNextToken()->None:
    nonlocal currentToken
    nonlocal tokenLineNumber
    nonlocal tokenType
    nonlocal tokenValue

    # ensure token data is clean by erasing previous
    currentToken = None
    tokenLineNumber = None
    tokenType = None
    tokenValue = None

    # get the currentToken, lineNumber, type, and value
    # remove from stack so it doesn't get processed again
    currentToken = tokenStack.readCurrentToken()
    tokenLineNumber = currentToken[0]
    tokenType = currentToken[1]
    tokenValue = currentToken[2]
    tokenStack.pop()
    


  # will return nodes and child nodes if the node has a "definition" (eg func declares, etc within {...} )
  def getNode():
    nonlocal currentToken
    nonlocal tokenLineNumber
    nonlocal tokenType
    nonlocal tokenValue

    ...



  # process tokens into nodes
  while True:
    # if stack is empty then go on to interpretting else get the next token
    if len(tokenStack.stack) <= 0: break
    else: getNextToken()


    # start of script
    if tokenType == 'SCPTSTRT':
      nodeType = "SCPTSTRT"
      nodeRef = None
      nodeName = None
      nodeLine = tokenLineNumber
      nodeArgs = None
      nodeBody = {} # THIS NEEDS TO BE ENTRY POINT TO RECURSIVE/NESTED NODES! THIS CURRENTLY DOES NOT HAPPEN
      print('NODE:', nodeType, nodeRef, nodeName, nodeLine, nodeArgs, nodeBody)
      resetForNextNode()
      continue


    # end of script
    elif tokenType == 'SCPTEND':
      nodeType = "SCPTEND"
      nodeRef = None
      nodeName = None
      nodeLine = tokenLineNumber
      nodeArgs = None
      nodeBody = {}
      print('NODE:', nodeType, nodeRef, nodeName, nodeLine, nodeArgs, nodeBody)
      resetForNextNode()
      break


    # start of an expression
    elif tokenType == 'EXPRSTRT':
      print(f"3. {currentToken}")

      # next token will dictate how to process
      getNextToken() 

      # tokenValue instead of tokenType because checking if the value of the type is in refTypeTokens
      if not tokenValue in refTypeTokens:
        # this is a call to a developer defined expression
        print(f"3. {currentToken}")
        continue
      
      else:
        # then this is a built in expression... list of possible values:
        # all, any, either, notAny, neither, not, iv, nv
        # abort, stop, cookie, httpGet, httpPost, output, sleep, wait
        # rspns_header, rspns_redir
        # calc, min, max, chr, ord, date, now, today
        # guid, random
        # def, getglobal, nonlocal, print, return
        # class, object, self
        # library, use
        # tern, if, switch, when, else
        # const, var
        match tokenValue:
          #03/07/2025 removed all, any, either, notany, neither, not
          #removed so binary comparison operators take precedence and to prevent conflicting keywords 
          # case 'ALL':
            # """
            # example:
            # ref: all, args: 2+
              # returns true if all args evaluate to bool 1
            # """
            # print(currentToken)
            # continue
# 
# 
          # case 'ANY':
            # """
            # example:
            # ref:any, args: 2+
              # returns true if any arg is evaluated to bool 1
            # """
            # print(currentToken)
            # continue
#
# 
          # case 'either':
            # """
            # example:
            # ref: either, args: exactly 2
              # returns true if either arg is evaluated to bool 1
            # """
            # print(currentToken)
            # continue
# 
#
          # case 'neither':
            # """
            # example:
            # ref: neither, args: exactly 2
              # returns true if all args are evaluated to bool 0
            # """
            # print (currentToken)
            # continue
# 
#
          # case 'notAny':
            # """
            # example:
            # ref: notany, args: 2+
              # returns true if all args are evaluated to bool 0
            # """
            # print(currentToken)
            # continue
# 
#
          # case 'not':
            # """
            # example:
            # ref: not, args: exactly 1
              # returns inverse of bool value
            # """
            # print(currentToken)
            # continue


          case 'IV':
            """
            example:
            ref: iv, args: exactly 1
              returns true if bool 1, true, or expression has a non-0, non-null, non-blank value
            """
            print(currentToken)
            continue


          case 'NV':
            """
            example:
            ref: nv, args: exactly 1
              returns true if bool 0, false, or expression has a 0, null, blank value
            """
            print(currentToken)
            continue


          case 'ABORT':
            """
            example:
            ref: abort, args: 0
              aborts response and doesn't send it
            """
            print(currentToken)
            continue


          case 'STOP':
            """
            example:
            ref: stop, args: 0
              stops response and sends what is already available
            """
            print(currentToken)
            continue


          case 'COOKIE':
            """
            example:
            ref: cookie, args: up to 8, x required (name:str, value:str, domain:str, path:str, expires:datetime, httponly:bool, secure:bool, samesite:str)
              sends a cookie to the client
            """
            print(currentToken)
            continue


          case 'HTTPGET':
            """
            example:
            ref: httpGet, args: exactly 1 (url:str)
              gets data from another server ..
              .. assign as a value to a variable to use (@var result = @httpGet(...))
            """
            print(currentToken)
            continue


          case 'HTTPPOST':
            """
            example:
            ref: httpPost, args: exactly 1 (url:str)
              posts data to another server .. no return value
            """
            print(currentToken)
            continue


          case 'OUTPUT':
            """
            example:
            ref: output, args: exactly 1 (responseContent:str)
              what the server's response content is
            """
            print(currentToken)
            continue


          case 'SLEEP':
            """
            example:
            ref: sleep, args: exactly 1 (time in sec:number)
              time before continuing this response
            """
            print(currentToken)
            continue


          case 'WAIT':
            """
            example:
            ref: wait, args: exactly 1 (time in sec:number)
              time before server will continue responding
              PAUSES ALL RESPONSES
            """
            print(currentToken)
            continue


          case 'RSPNS_HEADER':
            """
            example:
            ref: rspns_header, args: exactly 2 (headerName:str, headerValue:str)
              add a header to the response
            """
            print(currentToken)
            continue


          case 'RSPNS_REDIR':
            """
            example:
            ref:rspns_redir, args: exactly 1 (url:str)
              redirect client to new page
            """
            print(currentToken)
            continue


          case 'CALC':
            """
            example:
            ref:calc, args 2+ (numericalLiterals, operators, refs)
              calculates the value of a mathematical or binary expression
            """
            print(currentToken)
            continue


          case 'MIN':
            """
            example:
            ref:min, args 2+ (numericalLiterals)
              returns smallest value
            """
            print(currentToken)
            continue


          case 'MAX':
            """
            example:
            ref:max, args 2+ (numericalLiterals)
              returns largest value
            """
            print(currentToken)
            continue


          case 'CHR':
            """
            example:
            ref:chr, args: exactly 1 (numericLiteral ASCII table)
              returns the ordinal value of an ASCII character ie @chr(64) -> @
            """
            print(currentToken)
            continue


          case 'ORD':
            """
            example:
            ref:ord, args: exactly 1 (alphaLiteral in ASCII table)
              returns the character value of an ASCII ordinal ie @chr(|) -> 124
            """
            print(currentToken)
            continue


          case 'DATE':
            """
            example:
            ref:date, args: 0-2 (date:str, time:str)
              0 args - acts as @now()
              1-2 args: returns datetime as float value
            """
            print(currentToken)
            continue
            

          case 'NOW':
            """
            example:
            ref:now, args: 0
              returns right now's datetime as float value
            """
            print(currentToken)
            continue


          case 'TODAY':
            """
            example:
            ref:today, args: 0
              returns today's date, at 00:00:00:000, as float value
            """
            print(currentToken)
            continue


          case 'GUID':
            """
            example:
            ref:guid, args: 0-1 (seed:str:number)
              returns a random alphanumeric string xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
            """
            print(currentToken)
            continue


          case 'RANDOM':
            """
            example:
            ref:random, args: 0-1 (limit:int:float)
              0 args - random number up to 2,147,483,647 (note that ints can be larger than signed 32-bit)
              1 arg - random number up to that value, including same number of decimal points
            """
            print(currentToken)
            continue


          case 'DEF':
            """
            example:
            ref:def, name:str, args: 0-many (vars:any), returnType:any, definition
              this is a function
            """
            print(currentToken)
            continue


          case 'GLOBAL':
            """
            example:
            ref:getglobal, args: 1 (:ref to global var)
              allows use of global variable in a func/method
            """
            print(currentToken)
            continue


          case 'NONLOCAL':
            """
            example:
            ref:nonlocal, args: 1 (:ref to var one scope up)
              allows use of a variable at one scope up in a func/method (cascades)
            """
            print(currentToken)
            continue


          case 'PRINT':
            """
            example:
            ref:print, args: 1 (value:any)
              prints value to terminal cast as string
            """
            print(currentToken)
            continue


          case 'RETURN':
            """
            example:
            ref:return, args: 1 (value:any)
              returns value as literal:type from func/method to program
            """
            print(currentToken)
            continue


          case 'CLASS':
            """
            example:
            UNFINISHED
            """
            print(currentToken)
            continue


          case 'OBJECT':
            """
            example:
            UNFINISHED
            """
            print(currentToken)
            continue


          case 'SELF':
            """
            example:
            ref:self, args: 0
              reference to containing class
            """
            print(currentToken)
            continue


          case 'LIBRARY':
            """
            example:
            ref:libary, args: 1 (path:str)
              use the modules in this library as part of program
            """
            print(currentToken)
            continue


          case 'USE':
            """
            example:
            ref:use, args:1 (moduleName:str)
              goto/use this module here
            """
            print(currentToken)
            continue


          case 'TERN':
            """
            example:
            ref:tern, args: 2-3 (conditional, returnVal if true, returnVal if false), returnType:type
              returns one value or another depending on conditional result
            """
            print(currentToken)
            continue
            

          case 'IF':
            """
            example:
            ref:if, args: 1 (conditional), definition
              execute definition if conditional is true
            """
            print(currentToken)
            continue


          case 'SWITCH':
            """
            example:
            ref:switch, args 1 (expression), definition (when/else expressions)
              execute one of the definition depending on resulting value of expression
            """
            print(currentToken)
            continue


          case 'WHEN':
            """
            example:
            ref:when, args 1 (value:any), definition
              execute this definition when value matches that of parent switch
            """
            print(currentToken)
            continue


          case 'ELSE':
            """
            example:
            ref:else, args 0, definition
              execute this definition when no previous when statements nested in same parent switch definition match switch expression value
            """
            print(currentToken)
            continue


          case 'VAR':
            """
            example: @var url:str = "https://example.com";
            ref:var, name:str, type:any, args:none, value:any (must match type unless any)
              assign mutable value (as literal or reference) to a variable
              if type is any, the mutable type, if not any, then type is not mutable
            """
            nodeType = "REF"
            nodeRef = "VAR"
            nodeLine = tokenLineNumber
            #node Args ... need type
            #node body node

            # get nodeName
            getNextToken()
            if tokenType == "ARG":
              nodeName = tokenValue
            else:
              raise Exception(f"Syntax error on line {tokenLineNumber}): Expected argument NAME but got {tokenValue}({tokenType}).")
            
            # check for exprType syntax (char :)
            getNextToken()
            if tokenType != "EXPRTYPE": raise Exception(f"Syntax error on line {tokenLineNumber}: Expected type declarator (: character) but got {tokenValue}({tokenType}).")

            # get variable type nodeArg
            getNextToken()
            if tokenType == "TYPE":
              nodeArgs.append({"EXPRTYPE": f"{tokenValue}"})
            else:
              raise Exception(f"Syntax error on line {tokenLineNumber}: Expected TYPE but got {tokenValue}({tokenType}).")
          
            nodeBody = None # no nodeBody for var

            print('NODE:', nodeType, nodeRef, nodeName, nodeLine, nodeArgs, nodeBody)
            resetForNextNode()
            continue


          case 'CONST':
            """
            example:
            ref:const, name:str, type:any (except any), value:any (must match type)
              assign immutable value (as literal or reference) to a constant
              type and value are both immutable once assigned
            """
            print(currentToken)
            continue


          case _:
            print(f"Parser Warning A - {tokenValue} ({currentToken}) not implemented in parser yet!")
            #raise Exception ("Fatal Error: AST Parser found reserved keyword that does not have logic programmed yet.")


    else:
      print(f"Parser Warning B - {tokenValue} ({tokenType}) not implemented in parser yet! ")


    # print(currentToken)
    