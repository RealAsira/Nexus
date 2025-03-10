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
    #print(f"Stored parsed node: {aNode}")
    self.tree.update(aNode)

  def clear(self):
    self.tree.clear()

AST = abstractSyntaxTree()





# PARSE TOKENS from tokenizeScript returned object... NEXPARSER ENTRY POINT
# Returns an Abstract Syntax Tree (AST) as object
def parseTokens(tokenStack:object) -> object:
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



  def getNode() -> dict:
    nonlocal tokenStack, currentToken, tokenLineNumber, tokenType, tokenValue
    nonlocal nodeID

    nodeID += 1             # inc to next nodeID
    nodeType:str = None     # ie ref, type, op, etc
    nodeRef:str = None      # ie var, def, calc, etc
    nodeName:str = None     # ie var BAR, def FOO class AST (bar, foo, ast)
    nodeLine:int = None     # line number
    nodeArgs:list = []      # any args that node needs to function
    nodeBody:dict = {}      # child nodes (eg function definition)


    def formattedNode(thisNodeID:int=nodeID):
      nonlocal nodeID, nodeType, nodeRef, nodeName, nodeLine, nodeArgs, nodeBody
      return({f"{thisNodeID}": {"nodeType": nodeType, "nodeRef": nodeRef, "nodeName": nodeName, "nodeLineNumber": nodeLine, "nodeArgs": nodeArgs, "nodeBody": nodeBody}})


    # get the next token to process into the node
    getNextToken()

    # start of script
    if tokenType == 'SCPTSTRT':
      thisNodeID = nodeID     # preserveNodeID
      nodeType = tokenType    # start of script
      nodeRef = None          # override to no ref
      nodeName = None         # override to no name
      nodeLine = 0            # override to line 0
      nodeArgs = []           # override to no args
    
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
      nodeArgs = []           # override to no args
      nodeBody = {}           # override to no body

      return(formattedNode())


    # start of an expression
    elif tokenType == "EXPRSTRT":
      thisNodeID = nodeID
      nodeType = tokenType
      nodeRef = None
      nodeName = None
      nodeLine = tokenLineNumber
      nodeArgs = []

      # all following nodes are children until this expression ends
      while True:
        if tokenType == "EXPREND": break
        nodeBody.update(getNode())

      return(formattedNode(thisNodeID))


    # for built in expressions such as var, def, class, etc
    elif tokenType == "REF":
      """
      List of built-in ref-typed expressions
      iv, nv,
      abort, stop, cookie, httpget, httppost, output, sleep, wait,
      rspns_header, rspns_redir,
      calc, min, max,
      chr, ord,
      date, now, today,
      guid, random,
      def, getglobal, nonlocal, print, return,
      class, object, self,
      library, use
      tern, if, switch, when, else,
      const, var
      """
      match tokenValue:
        #case "VAR":
        #  ...

        case _:
          print(f"Parser Warning B - REF-typed token {tokenValue} is not implemented in parser yet. Attempted to create node anyway.")
          nodeType = tokenType
          nodeRef = tokenValue
          nodeName = "MISSING"
          nodeLine = tokenLineNumber
          nodeArgs = []
          nodeBody = {}

          return(formattedNode())


    # catch-all for missing items
    else:
      print(f"Parser Warning A - {tokenValue} ({tokenType}) not implemented in parser yet. Attempted to create node anyway.")
      nodeType = tokenType
      nodeRef = None
      nodeName = tokenValue
      nodeLine = tokenLineNumber
      nodeArgs = []
      nodeBody = {}

      #getNextToken()  # done processing current
      return(formattedNode())
      


  # SUB FUNCTIONS, ETC
  if currentNode is None:
    currentNode = getNode()



  # continue looping until end of token stack 
  while len(tokenStack.stack) > 0:
    currentNode = getNode()   # get the next node
    AST.update(currentNode)   # put into tree
    currentNode = None        # reset for next node

  print(json.dumps(AST.tree, indent=2))
  return (AST)