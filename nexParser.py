"""
PARSER MAKES NODES FROM TOKENS
"""





# what kinsd of nodes are there?
nodeTypes = {
  "expression",
}





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
  currentToken:list
  tokenLineNumber:int
  tokenType:str
  tokenValue:any

  currentToken = None   # currentToken[0] is lineNumber, [1] is tokenType, [2] is tokenValue
  tokenLineNumber = 0   # currentToken[0]
  tokenType = None      # currentToken[1]
  tokenValue = None     # currentToken[2]
  
  # parts of a node
  currentNode: dict
  nodeID:int = 1
  nodeType:str
  nodeRef:str
  nodeName:str
  nodeVal:str



  # update nodeID, reset current token and node container
  def resetForNextNode() -> None:
    nonlocal nodeID
    nonlocal currentToken
    nonlocal currentNode

    nodeID += 1
    currentToken = None
    currentNode = None



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

    

  # process tokens into nodes
  while True:
    # all tokens have been processed and popped
    if len(tokenStack.stack) == 0:
      break

    getNextToken()
    print(currentToken)
    