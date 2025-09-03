"""
INTERPRETER USES ABSTRACT SYNTAX TREE TO INTERPRET AND EXECUTE DATA/CODE
RETURNS SINGLE STRING, CONTENT
ALSO ASSIGNS VALS TO response_headers
"""

import json
import NexErrorHandler as neh
import NexServerGlobals
all_reserved_tokens = NexServerGlobals.all_reserved_tokens
expr_type_tokens = NexServerGlobals.expr_type_tokens
string_delim_tokens = NexServerGlobals.string_delim_tokens
xml_delim_tokens = NexServerGlobals.xml_delim_tokens
ref_type_tokens = NexServerGlobals.ref_type_tokens
method_types = NexServerGlobals.method_types





def interpretAST(obj_AST:object, script_name:str = "Unknown Nexus Module")->tuple:
  """USES AST TO GENERATE AN OUTPUT"""
  #global all_reserved_tokens
  #global expr_type_tokens
  #global string_delim_tokens
  #global xml_delim_tokens
  #global ref_type_tokens
  global method_types

  variables:dict = {} # a list of references and values
  content:str = '' # CONTENT INTERPRETED!!

  def interpretVarAssignment(node:dict, node_id:int, child_returns:list)->None:
    """Interprets the assignment of a value to a variable"""

    node_type = node["nodeType"]
    node_ref = node["nodeRef"]
    node_name = node["nodeName"]
    node_line = node["nodeLineNumber"]
    node_args = node["nodeArgs"]

    var_name = child_returns[0]['var_name']
    var_types = child_returns[0]['var_types']
    operation = child_returns[1]
    value = child_returns[2]['arg_value']
    value_types = child_returns[2]['arg_types']

    old_value = variables[var_name]['value']
    mutable = variables[var_name]['mutable']

    # is either a variable (mutable) or is a constant that doesn't have a value yet
    if mutable or (not mutable and old_value is None):
      is_valid_type = False
      for value_type in value_types:
        if is_valid_type == True: continue
        if value_type in var_types: is_valid_type = True

      if operation == "ASSIGN":
        if not is_valid_type:                     # illegal type assignment
          try: raise neh.NexException(f"Cannot assign a(n) {value_types} value to @VAR of type(s) {var_types}")
          except neh.NexException as err: neh.nexError(err, True, script_name, node_line)
        else:
          variables[var_name]['value'] = value   # assign new value

    else:
      # no change is made to the value, supply warning to console
      try: raise neh.NexException(f'Const @{var_name.upper()} cannot be reassigned a new value')
      except neh.NexException as err: neh.nexError(err, False, script_name, node_line)

    return(None)



  def interpretRefCall(node:dict, node_id:int, child_returns:list)->None:
    """Run a call to a reference, such as var, function, object calls"""
    nonlocal content

    ref_name = child_returns[0]['ref_name']
    ref_params = child_returns[0]['ref_params']
    ref_methods = child_returns[0]['ref_methods']
    node_line = node['nodeLineNumber']

    # how to processing this ref call ... variables? functions? something else?
    ref_mode = None
    if ref_name in variables: ref_mode = 'var_call'   # the name of the object called was a variable
    else: ref_mode = 'UNKNOWN_REF_MODE'


  # proccess a call to a variable
    if ref_mode == 'var_call': 
      var_value = variables[ref_name]['value']
      var_types = variables[ref_name]['types']
      if ref_methods:
        content_value = interpretRefMethods(var_value, var_types, ref_methods, node_line)  # modify the value of 
      else: content_value = var_value
      if content_value is None: content_value = ''  # replace None with empty string since None can't concat to string

      try:
        content += content_value
      except:
        try: raise neh.NexException(f'Could not append "{content_value}" to server response')
        except neh.NexException as err: neh.nexError(err, False, script_name, node_line)

    else:
      print(f'interpretRefCall for {ref_name} could not be completed... {ref_mode}')



  def interpretRefMethods(value:any, value_types:list, methods:dict, node_line:int):
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
    global method_types
    return_value = value

    # process each method independently 
    for node_id in methods:  # methods are passed as node_id's
      # get the method name and check its types
      method_name = methods[node_id]['node_name']
      if not method_name in method_types:
        try: raise neh.NexException(f'The ".{method_name.upper()}()" method doesn\'t exist')
        except neh.NexException as err: neh.nexError(err, True, script_name, node_line)
      else: method_types = method_types[method_name]

      # can this method be applied to this value?
      is_valid_type = False 
      for method_type in method_types:
        if is_valid_type == True: continue
        if method_type in value_types: is_valid_type = True

      if is_valid_type:
        # the type(s) this method can apply to matches the type(s) of the value... run the method
        if method_name == 'strip': return_value = return_value.strip()
      else:
        try: raise neh.NexException(f'The ".{method_name.upper()}()" method cannot be applied to value of type(s) {value_types}')
        except neh.NexException as err: neh.nexError(err, True, script_name, node_line)

    return(return_value)



  expression_mode = None # tracks what the current expression is (eg, var assignment, reference call, etc)
  def processNode(node:dict, node_id:int, child_returns:list)->any:
    """Processes the node"""
    nonlocal variables
    nonlocal expression_mode

    node_type = node["nodeType"]
    node_ref = node["nodeRef"]
    node_name = node["nodeName"]
    node_line = node["nodeLineNumber"]
    node_args = node["nodeArgs"]

    #print(node_id, node_type, node_ref, node_name, node_args)

    if node_type == "ROOT":
      """Functionality for root of AST"""
      ...



    elif node_type == "EXPR":
      """Functionality for an expression call"""
      # expression_mode was previously assigned... use to determine how to interpret the expression

      if   expression_mode == 'varAssign': interpretVarAssignment(node, node_id, child_returns)
      elif expression_mode == 'refCall': interpretRefCall(node, node_id, child_returns)
      expression_mode = None # reset after interpreting
      


    elif node_type == "STRLITERAL":
      """
      Functionality for a string literal
      returns a string from concatted child elements
      """
      string_literal:str = ''
      return_value:dict = {}

      # concat child_returns (arg literals) into string
      for item in child_returns:
        string_literal = f"{string_literal}{item['arg_value']}"
        # IS STRING_LITERAL += ITEM['ARG_VALUE'] BETTER??
        # IS STRING_LITERAL += ITEM['ARG_VALUE'] BETTER??
        # IS STRING_LITERAL += ITEM['ARG_VALUE'] BETTER??
        # IS STRING_LITERAL += ITEM['ARG_VALUE'] BETTER??
        # IS STRING_LITERAL += ITEM['ARG_VALUE'] BETTER??

      # return as nodeArg dict for interpretAssignment
      return_value = {'arg_types': ['STR'], 'arg_value': string_literal}
      return(return_value)



    elif node_type == "REF":
      """
      Functionality for an expression
      List of built-in ref-typed expressions:
      abort, stop, cookie, httpget, httppost, output, sleep, wait, rspns_header, rspns_redir,
      calc, min, max, chr, ord, date, now, today, guid, random,
      def, getglobal, nonlocal, print, return, class, object, self, library, use
      tern, if, switch, when, else, const, var
      """

      if node_ref == "VAR":
        """handle variable declaration"""
        var_name = node_name
        var_types = node_args['returnTypes']
        # value appended separately

        # previously existed
        if var_name in variables:
          if variables[var_name]['mutable']: # is an existing variable, not a constant
            for var_type in var_types:
              if var_type not in variables[var_name]['types']:
                # check for type mismatches ... warn if mismatched
                try: raise neh.NexException(f'Variable reassignment type mismatch for @{var_name.upper()} (new: {var_type}, old: {variables[var_name]['types']})')
                except neh.NexException as err: neh.nexError(err, False, script_name, node_line)

            # assign new type(s) and empty value
            variables[var_name]['types'] = var_types
            variables[var_name]['value'] = None

          elif not variables[var_name]['mutable']: # is an existing constant
            try: raise neh.NexException(f'Cannot create @{var_name.upper()} as a VAR because it is already an existing CONST')
            except neh.NexException as err: neh.nexError(err, False, script_name, node_line)

        # new variable ... create as placeholder
        else: 
          variables.update({f'{var_name}': {'types': var_types, 'value': None, 'mutable': True}})
        
        # return data to parent node
        return({'var_name': var_name, 'var_types': var_types})
      

      elif node_ref == 'CONST':
        """handle constant declaration"""
        const_name = node_name
        const_types = node_args['returnTypes']
        # value appended separately

        # can't change an existing constant
        if const_name in variables:
          try: raise neh.NexException(f'Const @{const_name.upper()} already exists (redeclaration warning)')
          except neh.NexException as err: neh.nexError(err, False, script_name, node_line)

        else:
          # mutable: False makes this a constant
          variables.update({f'{const_name}': {'types': const_types, 'value': None, 'mutable': False}})

        return({'var_name': const_name, 'var_types': const_types})  # next item is the assignment

      

      elif node_ref == "ARG":
        """handle calls to variables, functions, objects, etc"""
        params = node_args['params']
        if 'methods' in node_args: methods = node_args['methods']
        else: methods = {}
        expression_mode = 'refCall'
        return({'ref_name':node_name, 'ref_params':params, 'ref_methods':methods})



    elif node_type == "OP":
      """Funtionality for an operator"""
      # THIS CURRENTLY ASSUMES THE OPERATOR IS AN =
      # in the future, this will handle differently depending on OP type
      expression_mode = 'varAssign'
      return('ASSIGN')



    elif node_type == "ARG":
      """
      Functionality for an arg literal
      returns the literal's type and value
      """
      arg = {'arg_value': node_args['value'], 'arg_types': node_args['types']}
      return(arg)



    elif node_type == "METHOD":
      """Functionality for a method"""
      #HYPOTHETHICALLY THIS IS NEVER CALLED...?
      ...



    else:
      """Catch all ... shouldn't ever be called"""
      ...

    

  def traverseAST(sub_AST:dict, node_id:int):
    """Traverse AST to then interpret each node"""
    child_returns:list = []

    for child_node_id in sorted(sub_AST["nodeBody"].keys(), key=int):
      childReturn = traverseAST(sub_AST["nodeBody"][child_node_id], child_node_id)  # get children return value
      child_returns.append(childReturn)                                             # append to list for parent node to process

    return (processNode(sub_AST, node_id, child_returns))





  # ENTRY POINT
  print(json.dumps(obj_AST.tree, indent=2))  # USED FOR DEBUGGING
  node_id:int = next(iter(obj_AST.tree.keys()))  # get first node_id (entry point)
  traverseAST(obj_AST.tree[node_id], node_id)     # iterative processor entry point ... use full AST and root node_id

  # print interpreter warnings then clear, before exit point
  if len(neh.warnings) != 0:
    print('INTERPRETER WARNINGS:')
    for warning in neh.warnings:
      print(warning)
    neh.warnings.clear()
  
  # EXIT POINT
  return((content, script_name)) # CONTENT IS GENERATED, RETURN IT
