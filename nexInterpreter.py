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
methodTypes = nexServerGlobals.methodTypes

variables:dict = {} # a list of references and values
content:str = '' # CONTENT INTERPRETED!!





def interpretAST(AST:object)->str:
  """USES AST TO GENERATE AN OUTPUT"""
  #global allReservedTokens
  #global exprTypeTokens
  #global stringDelimTokens
  #global xmlDelimTokens
  #global refTokens
  global methodTypes

  def interp_var_assignment(node:dict, nodeID:int, childReturns:list)->None:
    """Interprets the assignment of a value to a variable"""

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
      if isValidType == True: continue
      if valueType in varTypes: isValidType = True

    if operation == "ASSIGN":
      if not isValidType:                     # illegal type assignment
        raise Exception(f"Cannot assign type {valueTypes} value to variable of value type(s) {varTypes}.")
      else:
        variables[varName]['value'] = value   # assign new value

    return(None)



  def interp_ref_call(node:dict, nodeID:int, childReturns:list)->None:
    """Run a call to a reference, such as var, function, object calls"""
    global content

    refName = childReturns[0]['refName']
    refParams = childReturns[0]['refParams']
    refMethods = childReturns[0]['refMethods']

    refMode = None  # variables? functions? something else?
    if refName in variables: refMode = 'var_call'
    else: refMode = 'UNKNOWN_REF_MODE'


  # proccess a call to a variable
    if refMode == 'var_call': 
      varValue = variables[refName]['value']
      varTypes = variables[refName]['types']
      if refMethods:
        contentVal = interp_ref_methods(varValue, varTypes, refMethods)  # modify the value of 
      else: contentVal = varValue
      content += contentVal

    else:
      print(f'interp_ref_call for {refName} could not be completed... {refMode}')



  def interp_ref_methods(value:any, valueTypes:list, methods:dict):
    """
    modifies a value depending on its type and methods
    BUILT IN METHODS:
    methods for any:
    methods for blank:
    methods for null:
    methods for str: strip

    methods for list:
    methods for dict:
    methods for ref:

    methods for bool:
    methods for datetime:
    methods for number:
    methods for int:
    methods for float:
    methods for double:
    methods for money:

    methods for base64:
    methods for binary:
    methods for hex:
    methods for utf8:
    """
    global methodTypes
    returnVal = value

    # process each method independently 
    for nodeID in methods:  # methods are passed as nodeID's
      # get the method name and check its types
      methodName = methods[nodeID]['nodeName']
      if not methodName in methodTypes:
        print(f'Method Warning! "{methodName.upper()}" is not a built-in method and custom type-methods don\'t exist yet!')
      else: methodTypes = methodTypes[methodName]

      # can this method be applied to this value?
      isValidType = False 
      for methodType in methodTypes:
        if isValidType == True: continue
        if methodType in valueTypes: isValidType = True

      if isValidType:
        # the type(s) this method can apply to matches the type(s) of the value... run the method
        if methodName == 'strip': returnVal = returnVal.strip()
      else:
        print(f'Method "{methodName.upper()}" cannot be applied to value of type(s) {valueTypes} ... no change to value!')

    return(returnVal)



  exprMode = None # tracks what the current expression is (eg, var assignment, reference call, etc)
  def processNode(node:dict, nodeID:int, childReturns:list)->any:
    """Processes the node"""
    global variables
    nonlocal exprMode

    nodeType = node["nodeType"]
    nodeRef = node["nodeRef"]
    nodeName = node["nodeName"]
    nodeArgs = node["nodeArgs"]

    #print(nodeID, nodeType, nodeRef, nodeName, nodeArgs)

    if nodeType == "ROOT":
      """Functionality for root of AST"""
      ...



    elif nodeType == "EXPR":
      """Functionality for an expression call"""
      # exprMode was previously assigned... use to determine how to interpret the expression

      if   exprMode == 'varAssign': interp_var_assignment(node, nodeID, childReturns)
      elif exprMode == 'refCall': interp_ref_call(node, nodeID, childReturns)
      exprMode = None # reset after interpreting
      


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
        variables.update({f'{varName}': {'types': varTypes, 'value': None}})
        exprMode = 'varAssign'
        return({'varName': varName, 'varTypes': varTypes})
      

      elif nodeRef == "ARG":
        """handle calls to variables, functions, objects, etc"""
        params = nodeArgs['params']
        if 'methods' in nodeArgs: methods = nodeArgs['methods']
        else: methods = {}
        exprMode = 'refCall'
        return({'refName':nodeName, 'refParams':params, 'refMethods':methods})



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
  #print(json.dumps(AST.tree, indent=2))  # USED FOR DEBUGGING
  #return(json.dumps(AST.tree, indent=2)) # USED FOR DEBUGGING
  return(content)                         # CONTENT IS GENERATED, RETURN IT
