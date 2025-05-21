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

variables:dict = {} # a list of references and values
content:str = None # CONTENT INTERPRETED!!





def interpretAST(AST:object)->str:
  """USES AST TO GENERATE AN OUTPUT"""
  #global allReservedTokens
  #global exprTypeTokens
  #global stringDelimTokens
  #global xmlDelimTokens
  #global refTokens


  def interp_var_assignment(node:dict, nodeID:int, childReturns:list)->any:
    """Interprets the assignment of a value to a variable"""
    global variables
    
    nodeType = node["nodeType"]
    nodeRef = node["nodeRef"]
    nodeName = node["nodeName"]
    nodeArgs = node["nodeArgs"]

    varName = childReturns[0]['varName']
    varTypes = childReturns[0]['varTypes']
    operation = childReturns[1]
    value = childReturns[2]['argValue']
    valueTypes = childReturns[2]['argTypes']

    isValidType = False
    for valueType in valueTypes:
      if valueType in varTypes: isValidType = True

    if operation == "ASSIGN":
      if not isValidType:                     # illegal type assignment
        raise Exception(f"Cannot assign type {valueTypes} value to variable of value type(s) {varTypes}.")
      else:
        variables[varName]['value'] = value   # assign new value

    return(None)



  def interp_xxx(node:dict, nodeID:int, childReturns:list)->any:
    """Placeholder"""
    ...



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
      # all children of an expression have been ... determine how it is interpretted

      # FUNCTION CURRENTLY ASSUMES VARIABLE VALUE ASSIGNMENTS ... 
      # NEED TO INSTEAD USE RETURNED CHILDREN AS CONTEXT OF HOW TO PROCESS
      print('TESTING VAR ASSIGNMENT', variables)
      interp_var_assignment(node, nodeID, childReturns)
      print('TESTING VAR ASSIGNMENT', variables)



    elif nodeType == "STRLITERAL":
      """
      Functionality for a string literal
      returns a string from concatted child elements
      """
      strLiteral:str = ''
      returnVal:dict = {}

      # concat childReturns (arg literals) into string
      for item in childReturns:
        strLiteral = f"{strLiteral}{item['argValue']}"

      # return as nodeArg dict for interp_assignment
      returnVal = {'argTypes': ['STR'], 'argValue': strLiteral}
      return(returnVal)



    elif nodeType == "REF":
      """
      Functionality for an expression
      List of built-in ref-typed expressions:
      iv, nv, abort, stop, cookie, httpget, httppost, output, sleep, wait, rspns_header, rspns_redir,
      calc, min, max, chr, ord, date, now, today, guid, random,
      def, getglobal, nonlocal, print, return, class, object, self, library, use
      tern, if, switch, when, else, const, var
      """

      if nodeRef == "VAR":
        """handle variable declaration"""
        varName = nodeName
        varTypes = nodeArgs['returnTypes']
        #value appended separately

        # create the placeholder variable, return the name in case it is needed
        variables.update({f'{varName}': {'type': varTypes, 'value': None}})
        return({'varName': varName, 'varTypes': varTypes})
        


    elif nodeType == "OP":
      """Funtionality for an operator"""
      return('ASSIGN')



    elif nodeType == "ARG":
      """
      Functionality for an arg literal
      returns the literal's type and value
      """
      arg = {'argValue': nodeArgs['value'], 'argTypes': nodeArgs['types']}
      return(arg)



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
