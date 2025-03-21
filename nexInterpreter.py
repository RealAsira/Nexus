"""
INTERPRETER USES ABSTRACT SYNTAX TREE TO INTERPRET AND EXECUTE DATA/CODE
RETURNS SINGLE STRING, CONTENT
ALSO ASSIGNS VALS TO response_headers
"""

import json
import nexServerGlobals
allReservedTokens = nexServerGlobals.allReservedTokens
exprTypeTokens = nexServerGlobals.exprTypeTokens
stringDelimTokens = nexServerGlobals.stringDelimTokens
xmlDelimTokens = nexServerGlobals.stringDelimTokens
refTokens = nexServerGlobals.refTokens

content:str = None # CONTENT INTERPRETED!!



def interpretAST(AST:object)->str:
  """USES AST TO GENERATE AN OUTPUT"""
  #global allReservedTokens
  #global exprTypeTokens
  #global stringDelimTokens
  #global xmlDelimTokens
  #global refTokens


  def processNode(subAST, nodeID):
    """Processes a node's functionality"""

    nodeType = subAST["nodeType"]
    nodeRef = subAST["nodeRef"]
    nodeName = subAST["nodeName"]
    nodeArgs = subAST["nodeArgs"]
    nodeBody = subAST["nodeBody"]

    for childNodeID in sorted(nodeBody.keys(), key=int):
      processNode(nodeBody[childNodeID], childNodeID)  # use current node to extract a sub/derived AST

    print(nodeID, nodeType, nodeRef, nodeName, nodeArgs)
    return


  nodeID:int = next(iter(AST.tree.keys()))  # get first nodeID (entry point)
  processNode(AST.tree[nodeID], nodeID) # iterative processor entry point ... use full AST and root nodeID
 
  
  print(json.dumps(AST.tree, indent=2))
  return(json.dumps(AST.tree, indent=2))
