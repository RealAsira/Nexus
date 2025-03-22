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


  def interpretNode(node:dict, nodeID:int, childReturns:list)->any:
    """Interprets the node (functionality)"""
    global variables

    nodeType = node["nodeType"]
    nodeRef = node["nodeRef"]
    nodeName = node["nodeName"]
    nodeArgs = node["nodeArgs"]

    print(nodeID, nodeType, nodeRef, nodeName, nodeArgs, childReturns)

    if nodeType == "ROOT":
      """Functionality for root of AST"""
      ...



    elif nodeType == "EXPR":
      """Functionality for an expression call"""
      ...



    elif nodeType == "STRLITERAL":
      """
      Functionality for a string literal
      returns a string from concatted child elements
      """
      returnVal:str = ''

      for item in childReturns:
        returnVal = f"{returnVal}{item}"

      print('STRLITERAL:', returnVal)
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
        ...



    elif nodeType == "OP":
      """Funtionality for an operator"""
      ...



    elif nodeType == "ARG":
      """
      Functionality for a arg literal
      returns raw data literal
      """
      print('ARG:', nodeArgs['value'])
      return(nodeArgs['value'])



    elif nodeType == "METHOD":
      """Functionality for a method"""
      #HYPOTHETHICALLY THIS IS NEVER CALLED...?
      ...



    else:
      """Catch all ... shouldn't ever be called"""
      ...

    

  def processNode(subAST:dict, nodeID:int):
    """Processes a node's functionality"""
    childReturns:list = []

    for childNodeID in sorted(subAST["nodeBody"].keys(), key=int):
      childReturn = processNode(subAST["nodeBody"][childNodeID], childNodeID) # get children return value
      childReturns.append(childReturn) # append to list for parent node to process

    return (interpretNode(subAST, nodeID, childReturns))



  # ENTRY POINT
  nodeID:int = next(iter(AST.tree.keys()))  # get first nodeID (entry point)
  processNode(AST.tree[nodeID], nodeID) # iterative processor entry point ... use full AST and root nodeID
  
  # EXIT POINT
  print(json.dumps(AST.tree, indent=2))
  return(json.dumps(AST.tree, indent=2))
