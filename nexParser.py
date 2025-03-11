"""
PARSER MAKES NODES FROM TOKENS AND POPULATES ABSTRACT SYNTAX TREE (AST)
RETURNS AST OBJECT FROM TOKEN OBJECT
"""

import json
import nexServerGlobals
allReservedTokens = nexServerGlobals.allReservedTokens
exprTypeTokens = nexServerGlobals.exprTypeTokens
stringDelimTokens = nexServerGlobals.stringDelimTokens
xmlDelimTokens = nexServerGlobals.stringDelimTokens
refTokens = nexServerGlobals.refTokens





class abstractSyntaxTree:
  def __init__(self):
    self.tree = {}

  def update(self, aNode:dict):
    """Accepts dictionary that is updated/appened to the AST"""
    #print(f"Stored parsed node: {aNode}")
    self.tree.update(aNode)

  def clear(self):
    """Clears entire AST"""
    self.tree.clear()

AST = abstractSyntaxTree()





# PARSE TOKENS from tokenizeScript returned object... NEXPARSER ENTRY POINT
# Returns an Abstract Syntax Tree (AST) as object
def parseTokens(tokenStack:object) -> object:
  """Initialize the parsing of tokens"""
  #global allReservedTokens
  #global exprTypeTokens
  #global stringDelimTokens
  #global xmlDelimTokens
  #global refTokens

  currentNode:dict = {}       # temp container for current node to be stored
  nodeID:int = 0              # unique id for each node
  # parts of a token
  currentToken:list = None    # currentToken[0] is lineNumber, [1] is tokenType, [2] is tokenValue
  tokenLineNumber:int = None  # currentToken[0]
  tokenType:str = None        # currentToken[1]
  tokenValue:any = None       # currentToken[2]



  def getNextToken() -> None:
    """Clear currentToken data and advance to the next token if it exists"""
    nonlocal tokenStack, currentToken, tokenLineNumber, tokenType, tokenValue

    # clean the token data
    currentToken = None
    tokenLineNumber = None
    tokenType = None
    tokenValue = None

    # only attempt to process next token if it actually exists
    if len(tokenStack.stack) > 0:
      # get next token's data and pop so it isn't reprocessed
      currentToken = tokenStack.readCurrentToken()
      tokenLineNumber = currentToken[0]
      tokenType = currentToken[1]
      tokenValue = currentToken[2]
      tokenStack.pop()


  def peakNextTokenType()->str:
    """Peak at the next token type without advancing the stack"""
    return(tokenStack.stack[0][1])


  def getNode() -> dict:
    """Returns all of the information about a node, by processing up the tokenStack starting at the bottom tokenStack.stack[0]"""
    nonlocal tokenStack, currentToken, tokenLineNumber, tokenType, tokenValue
    nonlocal nodeID

    nodeID += 1             # inc to next nodeID
    nodeType:str = None     # ie ref, type, op, etc
    nodeRef:str = None      # ie var, def, calc, etc
    nodeName:str = None     # ie var BAR, def FOO class AST (bar, foo, ast)
    nodeLine:int = None     # line number
    nodeArgs:dict = {}      # any args that node needs to function... non-iterative and applies only to this node
    nodeBody:dict = {}      # child nodes (eg function definition... iterative and can be many layers deep)


    # formats the node as a dictionary
    def formattedNode(thisNodeID:int=nodeID):
      """Formats the node into a dictionary"""
      nonlocal nodeID, nodeType, nodeRef, nodeName, nodeLine, nodeArgs, nodeBody
      return({f"{thisNodeID}": {"nodeType": nodeType, "nodeRef": nodeRef, "nodeName": nodeName, "nodeLineNumber": nodeLine, "nodeArgs": nodeArgs, "nodeBody": nodeBody}})

    
    def getTypes()->list:
      """Gets all the immediately following type declarations for vars, consts, functions, etc"""
      typeList:list = []

      getNextToken()  # begin with getting a new token (needs to be of type EXPRTYPE (:) )
      if not tokenType == "EXPRTYPE":
        raise Exception(f"Syntax Error: Expecting TYPE-INDICATOR (:) but found {tokenValue}({tokenType}) instead.")
      
      # TYPE-INDICATOR was found, meaning the loop for finding types can be initiated
      while True:    
        getNextToken()  # the exprType token doesn't contain the type itself, so skip it

        if tokenType == "TYPE":
          typeList.append(tokenValue)
          if peakNextTokenType() in ["EXPRTYPE", "TYPE"]:
            getNextToken()
          else:
            break # exit once the next token isn't related to types
          
        else: 
          raise Exception(f"{tokenValue}({tokenType}) is not a valid type.")
        
      return(typeList)


    # get the next token to process into the node
    getNextToken()

    # start of script
    if tokenType == 'SCPTSTRT':
      thisNodeID = nodeID     # preserveNodeID
      nodeType = tokenType    # start of script
      nodeRef = None          # override to no ref
      nodeName = None         # override to no name
      nodeLine = 0            # override to line 0
      nodeArgs = {}           # override to no args
    
      # start getting child nodes and appending them to body using [dict].update(...)
      while len(tokenStack.stack) > 0:
        nodeBody.update(getNode())  # scptstrt is root of AST ... body is all other nodes as children ... this is iterative

      return(formattedNode(thisNodeID))


    # end of script
    elif tokenType == "SCPTEND":
      nodeType = tokenType    # end of script
      nodeRef = None          # override to no ref
      nodeName = None         # override to no name
      nodeLine = tokenLineNumber
      nodeArgs = {}           # override to no args
      nodeBody = {}           # override to no body

      return(formattedNode())


    # start of an expression
    elif tokenType == "EXPRSTRT":
      thisNodeID = nodeID
      nodeType = tokenType
      nodeRef = None
      nodeName = None
      nodeLine = tokenLineNumber
      nodeArgs = {}

      # all following nodes are children until this expression ends
      while True:
        if tokenType == "EXPREND": break
        nodeBody.update(getNode())

      return(formattedNode(thisNodeID))


    # for built in expressions such as var, def, class, etc
    elif tokenType == "REF":
      """
      List of built-in ref-typed expressions
      iv, nv, abort, stop, cookie, httpget, httppost, output, sleep, wait, rspns_header, rspns_redir,
      calc, min, max, chr, ord, date, now, today, guid, random,
      def, getglobal, nonlocal, print, return, class, object, self, library, use
      tern, if, switch, when, else, const, var
      """
      match tokenValue:
        case "IV":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "NV":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "ABOR":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "STOP":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "COOKIE":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "HTTPGET":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "HTTPPOST":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "OUTPUT":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "SLEEP":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "WAIT":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "RSPNS_HEADER":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "RASPNS_REDIR":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "CALC":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "MIN":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "MAX":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "CHR":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "ORD":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "DATE":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "NOW":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "TODAY":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "GUID":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "RANDOM":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "DEF":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "GETGLOBAL":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "NONLOCAL":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "PRINT":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "RETURN":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "CLASS":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "OBJECT":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "SELF":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "LIBRARY":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "USE":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "TERN":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "IF":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "SWITCH":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "WHEN":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "ELSE":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "CONST":
          print(f"Parser Warning C - REF-typed token {tokenValue} is not implemented in parser yet but a placeholder has been made. No node was created!")
        

        case "VAR":
          """
          example: @var bar:int = 5;
          @var [name]:[type] [(optional) = [value]];
          """
          nodeType = "REF"
          nodeRef = "VAR"
          #nodeName
          nodeLine = tokenLineNumber
          nodeArgs = {}
          nodeBody = {}

          # next token should be arg [name]
          getNextToken()
          if tokenType == "ARG":
            nodeName = tokenValue
          else:
            raise Exception(f"Variable expecting argument NAME but found {tokenValue}({tokenType}) instead.")
          
          # next part of syntax is always :[TYPE] ... or multiple types (the types the variable can be, ie returnTypes)
          nodeArgs.update({"returnTypes":getTypes()})
          
          if peakNextTokenType not in ["OP", "EXPREND"]:
            raise Exception(f"Variable was expecting ASSIGNMENT (=) or END (;) but found {tokenValue}({tokenType}) instead.")

          return(formattedNode())
        

        case _:
          print(f"Parser Warning B - REF-typed token {tokenValue} is not implemented in parser yet. Attempted to create node anyway.")
          nodeType = tokenType
          nodeRef = tokenValue
          nodeName = "MISSING"
          nodeLine = tokenLineNumber
          nodeArgs = {}
          nodeBody = {}

          return(formattedNode())


    # catch-all for missing items
    else:
      print(f"Parser Warning A - {tokenValue} ({tokenType}) not implemented in parser yet. Attempted to create node anyway.")
      nodeType = tokenType
      nodeRef = None
      nodeName = tokenValue
      nodeLine = tokenLineNumber
      nodeArgs = {}
      nodeBody = {}

      #getNextToken()  # done processing current
      return(formattedNode())
      


  # initialize the building of the node tree
  if currentNode is None:
    currentNode = getNode()



  # continue looping until end of token stack 
  while len(tokenStack.stack) > 0:
    currentNode = getNode()   # get the next node
    AST.update(currentNode)   # put into tree
    currentNode = None        # reset for next node

  print(json.dumps(AST.tree, indent=2))
  return (AST)