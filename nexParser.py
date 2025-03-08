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
refTypeTokens = nexServerGlobals.refTypeTokens





class abstractSyntaxTree:
  def __init__(self):
    self.tree = {}

  def update(self, aNode:dict):
    print(f"Stored parsed node: {aNode}")
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
  #global refTypeTokens

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

    """
    Each node some to most of the following:
    nodeID          - unique id for each node
    nodeType        - the type of node (such as ref)
    nodeRef         - sub type (such as var)
    nodeName        - a name assigned to the node
    nodeLineNumber  - the line number where the node was found
    nodeArgs        - additional args for the node
    nodeBody        - any definition (eg function defs, etc)
    """

    # get the next token to process into the node
    if currentToken == None: getNextToken()

    # start of script
    if tokenType == 'SCPTSTRT':
      nodeType = "SCPTSTRT"
      nodeRef = None
      nodeName = None
      nodeLine = tokenLineNumber
      nodeArgs = []

      while len(tokenStack.stack) > 0:
        getNextToken()        # done processing current
        nodeBody.update(getNode())  # scptstrt is root of AST ... body is all other nodes as children

      return ({f"{nodeID}": {"nodeType": nodeType, "nodeRef": nodeRef, "nodeName": nodeName, "nodeLineNumber": nodeLine, "nodeArgs": nodeArgs, "nodeBody": nodeBody}})

    # end of script
    elif tokenType == "SCPTEND":
      nodeType = "SCPTEND"
      nodeRef = None
      nodeName = None
      nodeLine = tokenLineNumber
      nodeArgs = []
      nodeBody = {}

      getNextToken() # done processing current
      return ({f"{nodeID}": {"nodeType": nodeType, "nodeRef": nodeRef, "nodeName": nodeName, "nodeLineNumber": nodeLine, "nodeArgs": nodeArgs, "nodeBody": nodeBody}})
    
    else:
      print(f"Parser Warning A - {tokenValue} ({tokenType}) not implemented in parser yet.")
      getNextToken()
      return ({f"{nodeID}": {"nodeType": 'NONE', "nodeRef": 'NONE', "nodeName": 'NONE', "nodeLineNumber": 'NONE', "nodeArgs": 'NONE', "nodeBody": 'NONE'}})
      


  # SUB FUNCTIONS, ETC
  if currentNode is None:
    currentNode = getNode()



  # continue looping until end of token stack 
  while len(tokenStack.stack) > 0:
    currentNode = getNode()   # get the next node
    AST.update(currentNode)   # put into tree
    currentNode = None        # reset for next node
    print(currentNode)

  print (json.dumps(AST.tree, indent=2))
  return (AST)