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

variables:list = [] # a list of references and values
content:str = None # CONTENT INTERPRETED!!





def interpretAST(AST:object)->str:
  """USES AST TO GENERATE AN OUTPUT"""
  #global allReservedTokens
  #global exprTypeTokens
  #global stringDelimTokens
  #global xmlDelimTokens
  #global refTokens


  def interpretExpr(node:dict, nodeID:int, childReturns:list)->any:
    global variables
    
    nodeType = node["nodeType"]
    nodeRef = node["nodeRef"]
    nodeName = node["nodeName"]
    nodeArgs = node["nodeArgs"]

    print('expr: ', nodeID, nodeType, nodeRef, nodeName, nodeArgs, childReturns)


  def processNode(node:dict, nodeID:int, childReturns:list)->any:
    """Processes the node"""
    global variables

    nodeType = node["nodeType"]
    nodeRef = node["nodeRef"]
    nodeName = node["nodeName"]
    nodeArgs = node["nodeArgs"]


    if nodeType == "ROOT":
      """Functionality for root of AST"""
      ...



    elif nodeType == "EXPR":
      """Functionality for an expression call"""
      interpretExpr(node, nodeID, childReturns)



    elif nodeType == "STRLITERAL":
      """
      Functionality for a string literal
      returns a string from concatted child elements
      """
      returnVal:str = ''

      for item in childReturns:
        returnVal = f"{returnVal}{item}"

      #print('STRLITERAL:', returnVal)
      return(returnVal)



    elif nodeType == "REF":
      """
      Functionality for an expression
      List of built-in ref-typed expressions
      iv, nv, abort, stop, cookie, httpget, httppost, output, sleep, wait, rspns_header, rspns_redir,
      calc, min, max, chr, ord, date, now, today, guid, random,
      def, getglobal, nonlocal, print, return, class, object, self, library, use
      tern, if, switch, when, else, const, var
      """


      if nodeRef == "VAR":
        """handle variable declaration"""
        varName = nodeName
        varType = nodeArgs['returnTypes']
        #value appended separately

        # create the placeholder variable, return the name in case it is needed
        variables.append({'name': varName, 'type': varType, 'value': None})
        return({'varName': varName, 'varType': varType})
        



    elif nodeType == "OP":
      """Funtionality for an operator"""
      return('ASSIGN')



    elif nodeType == "ARG":
      """
      Functionality for a arg literal
      returns raw data literal
      """
      #print('ARG:', nodeArgs['value'])
      return(nodeArgs['value'])



    elif nodeType == "METHOD":
      """Functionality for a method"""
      #HYPOTHETHICALLY THIS IS NEVER CALLED...?
      ...



    else:
      """Catch all ... shouldn't ever be called"""
      ...

    

  def traverseAST(subAST:dict, nodeID:int):
    """Traverse AST to then interpret each node"""
    childReturns:list = []

    for childNodeID in sorted(subAST["nodeBody"].keys(), key=int):
      childReturn = traverseAST(subAST["nodeBody"][childNodeID], childNodeID) # get children return value
      childReturns.append(childReturn)                                        # append to list for parent node to process

    return (processNode(subAST, nodeID, childReturns))



  # ENTRY POINT
  nodeID:int = next(iter(AST.tree.keys()))  # get first nodeID (entry point)
  traverseAST(AST.tree[nodeID], nodeID)     # iterative processor entry point ... use full AST and root nodeID
  
  # EXIT POINT
  print(json.dumps(AST.tree, indent=2))
  return(json.dumps(AST.tree, indent=2))
