"""
INTERPRETER USES ABSTRACT SYNTAX TREE TO INTERPRET AND EXECUTE DATA/CODE
RETURNS SINGLE STRING, CONTENT
ALSO ASSIGNS VALS TO response_headers
"""

import json
import nexErrHandler as neh
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
    nodeLineNumber = node["nodeLineNumber"]
    nodeArgs = node["nodeArgs"]

    varName = childReturns[0]['varName']
    varTypes = childReturns[0]['varTypes']
    operation = childReturns[1]
    value = childReturns[2]['argValue']
    valueTypes = childReturns[2]['argTypes']

    oldValue = variables[varName]['value']
    mutable = variables[varName]['mutable']

    # is either a variable (mutable) or is a constant that doesn't have a value yet
    if mutable or (not mutable and oldValue is None):
      isValidType = False
      for valueType in valueTypes:
        if isValidType == True: continue
        if valueType in varTypes: isValidType = True

      if operation == "ASSIGN":
        if not isValidType:                     # illegal type assignment
          try: raise neh.nexException(f"Cannot assign a(n) {valueTypes} value to @VAR of type(s) {varTypes}")
          except neh.nexException as err: neh.nexError(err, True, None, nodeLineNumber)
        else:
          variables[varName]['value'] = value   # assign new value

    else:
      # no change is made to the value, supply warning to console
      try: raise neh.nexException(f'Const @{varName.upper()} cannot be reassigned a new value')
      except neh.nexException as err: neh.nexError(err, False, None, nodeLineNumber)

    return(None)



  def interp_ref_call(node:dict, nodeID:int, childReturns:list)->None:
    """Run a call to a reference, such as var, function, object calls"""
    global content

    refName = childReturns[0]['refName']
    refParams = childReturns[0]['refParams']
    refMethods = childReturns[0]['refMethods']
    nodeLineNumber = node['nodeLineNumber']

    refMode = None  # variables? functions? something else?
    if refName in variables: refMode = 'var_call'
    else: refMode = 'UNKNOWN_REF_MODE'


  # proccess a call to a variable
    if refMode == 'var_call': 
      varValue = variables[refName]['value']
      varTypes = variables[refName]['types']
      if refMethods:
        contentVal = interp_ref_methods(varValue, varTypes, refMethods, nodeLineNumber)  # modify the value of 
      else: contentVal = varValue
      if contentVal is None: contentVal = ''  # replace None with empty string since None can't concat to string

      try:
        content += contentVal
      except:
        try: raise neh.nexException(f'Could not append "{contentVal}" to server response')
        except neh.nexException as err: neh.nexError(err, False, None, nodeLineNumber)

    else:
      print(f'interp_ref_call for {refName} could not be completed... {refMode}')



  def interp_ref_methods(value:any, valueTypes:list, methods:dict, nodeLineNumber:int):
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
        try: raise neh.nexException(f'The ".{methodName.upper()}()" method doesn\'t exist')
        except neh.nexException as err: neh.nexError(err, True, None, nodeLineNumber)
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
        try: raise neh.nexException(f'The ".{methodName.upper()}()" method cannot be applied to value of type(s) {valueTypes}')
        except neh.nexException as err: neh.nexError(err, True, None, nodeLineNumber)

    return(returnVal)



  exprMode = None # tracks what the current expression is (eg, var assignment, reference call, etc)
  def processNode(node:dict, nodeID:int, childReturns:list)->any:
    """Processes the node"""
    global variables
    nonlocal exprMode

    nodeType = node["nodeType"]
    nodeRef = node["nodeRef"]
    nodeName = node["nodeName"]
    nodeLineNumber = node["nodeLineNumber"]
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
        # value appended separately

        # previously existed
        if varName in variables:
          if variables[varName]['mutable']: # is an existing variable, not a constant
            for varType in varTypes:
              if varType not in variables[varName]['types']:
                # check for type mismatches ... warn if mismatched
                try: raise neh.nexException(f'Variable reassignment type mismatch for @{varName.upper()} (new: {varType}, old: {variables[varName]['types']})')
                except neh.nexException as err: neh.nexError(err, False, None, nodeLineNumber)

            # assign new type(s) and empty value
            variables[varName]['types'] = varTypes
            variables[varName]['value'] = None

          elif not variables[varName]['mutable']: # is an existing constant
            try: raise neh.nexException(f'Cannot create @{varName.upper()} as a VAR because it is already an existing CONST')
            except neh.nexException as err: neh.nexError(err, False, None, nodeLineNumber)

        # new variable ... create as placeholder
        else: 
          variables.update({f'{varName}': {'types': varTypes, 'value': None, 'mutable': True}})
        
        # return data to parent node
        return({'varName': varName, 'varTypes': varTypes})
      

      elif nodeRef == 'CONST':
        """handle constant declaration"""
        constName = nodeName
        constTypes = nodeArgs['returnTypes']
        # value appended separately

        # can't change an existing constant
        if constName in variables:
          try: raise neh.nexException(f'Const @{constName.upper()} already exists (redeclaration warning)')
          except neh.nexException as err: neh.nexError(err, False, None, nodeLineNumber)

        else:
          variables.update({f'{constName}': {'types': constTypes, 'value': None, 'mutable': False}})

        return({'varName': constName, 'varTypes': constTypes})  # next item is the assignment

      

      elif nodeRef == "ARG":
        """handle calls to variables, functions, objects, etc"""
        params = nodeArgs['params']
        if 'methods' in nodeArgs: methods = nodeArgs['methods']
        else: methods = {}
        exprMode = 'refCall'
        return({'refName':nodeName, 'refParams':params, 'refMethods':methods})



    elif nodeType == "OP":
      """Funtionality for an operator"""
      # THIS CURRENTLY ASSUMES THE OPERATOR IS AN =
      # in the future, this will handle differently depending on OP type
      exprMode = 'varAssign'
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
  print(json.dumps(AST.tree, indent=2))  # USED FOR DEBUGGING
  nodeID:int = next(iter(AST.tree.keys()))  # get first nodeID (entry point)
  traverseAST(AST.tree[nodeID], nodeID)     # iterative processor entry point ... use full AST and root nodeID

  # print interpreter warnings then clear, before exit point
  if len(neh.warnings) != 0:
    print('INTERPRETER WARNINGS:')
    for warning in neh.warnings:
      print(warning)
    neh.warnings.clear()
  
  # EXIT POINT
  return(content) # CONTENT IS GENERATED, RETURN IT
