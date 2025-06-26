"""
PARSER MAKES NODES FROM TOKENS AND POPULATES ABSTRACT SYNTAX TREE (AST)
RETURNS AST OBJECT FROM TOKEN OBJECT
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





class AbstractSyntaxTree:
  def __init__(self):
    self.tree = {}

  def update(self, aNode:dict):
    """Accepts dictionary that is updated/appened to the AST"""
    #print(f"Stored parsed node: {aNode}")
    self.tree.update(aNode)

  def clear(self):
    """Clears entire AST"""
    self.tree.clear()

obj_AST = AbstractSyntaxTree()





def determineNexusType(value:any)->str:
  """Returns a string representing the NEXUS type of a value"""

  # NEED TO ADD TEST SUPPORT FOR any, blank, null, list, dict, ref, bool, datetime, double, money, base64, binary, hex, utf8

  def isString(value):
    try: str(value); return True
    except: return False

  def isInt(value):
    try: int(value); return True
    except: return False

  def isFloat(value):
    try: float(value); return True
    except: return False

  def isNumber(value):
    if isInt(value) or isFloat(value): return True
    else: return False

  value_types = [] # matching types

  """
  specific test order
  int, float, number before str because strs can contain numbers
  """
  if isInt(value): value_types.append('INT')
  if isFloat(value): value_types.append('FLOAT')
  if isNumber(value): value_types.append('NUMBER')
  if isString(value): value_types.append('STR')
  else: value_types.append(type(value).__name__.upper())

  return(value_types)

  

  





# PARSE TOKENS from tokenizeScript returned object... NEXPARSER ENTRY POINT
# Returns an Abstract Syntax Tree (AST) as object
def parseTokens(token_stack:object, script_name:str = "Uknown Nexus Module")->object:
  """Initialize the parsing of tokens"""
  #global all_reserved_tokens
  #global expr_type_tokens
  #global string_delim_tokens
  #global xml_delim_tokens
  #global ref_type_tokens
  #global method_types

  current_node:dict = {}       # temp container for current node to be stored
  node_id:int = 0              # unique id for each node
  # parts of a token
  last_token:list = None       # last_token is a list formatted same as current_token
  current_token:list = None    # current_token[0] is token_line_number, [1] is token_type, [2] is token_value
  token_line_number:int = None  # current_token[0]
  token_type:str = None        # current_token[1]
  token_value:any = None       # current_token[2]

  # these are used later to modify how the parser handles tokens
  do_bypass_exprend:bool = False  # sometimes an assumed EXPREND is added ... this bypasses it
  is_righthand_side:bool = False  # lets parser know the right hand side of a statement is being processed


  def getNextToken() -> None:
    """Clear current_token data and advance to the next token if it exists"""
    nonlocal token_stack, last_token, current_token, token_line_number, token_type, token_value
    nonlocal do_bypass_exprend, is_righthand_side

    # clean the token data
    last_token = current_token  # move current token to last token
    current_token = None
    token_line_number = None
    token_type = None
    token_value = None

    # only attempt to process next token if it actually exists
    if len(token_stack.stack) > 0:
      # get next token's data and pop so it isn't reprocessed
      current_token = token_stack.readCurrentToken()
      token_line_number = current_token[0]
      token_type = current_token[1]
      token_value = current_token[2]
      token_stack.pop()
    else:
      try: raise neh.NexException('Expected more tokens but token stack is empty')
      except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)



  def peakNextTokenType()->str:
    """Peak at the next token type without advancing the stack"""
    if len(token_stack.stack) > 0: return(token_stack.stack[0][1])
    else: return(None)
  


  def peakNextTokenValue()->str:
    """Peak at the next token value without advancing the stack"""
    if len(token_stack.stack) > 0: return(token_stack.stack[0][2])
    else: return(None)
  


  def peakLastTokenType()->str:
    """Peak at the previous token type without altering the stack"""
    return(last_token[1])
  


  def peakLastTokenValue()->str:
    """Peak at the previous token value without altering the stack"""
    return(last_token[2])



  def getNode() -> dict:
    """Returns all of the information about a node, by processing up the token_stack starting at the bottom token_stack.stack[0]"""
    nonlocal token_stack, current_token, token_line_number, token_type, token_value
    nonlocal node_id
    nonlocal do_bypass_exprend, is_righthand_side

    node_id += 1            # inc to next node_id
    this_node_id = None     # this_node_id is used when storing nested nodes to a parent node... this_node_id is the parent's node_id
    node_type:str = None     # ie ref, type, op, etc
    node_ref:str = None      # ie var, def, calc, etc
    node_name:str = None     # ie var BAR, def FOO class AST (bar, foo, ast)
    node_line:int = None     # line number
    node_args:dict = {}      # any args that node needs to function... non-iterative and applies only to this node
    node_body:dict = {}      # child nodes (eg function definition... iterative and can be many layers deep)

    def formattedNode(this_node_id:int=node_id):
      """Formats the node into a dictionary"""
      nonlocal node_id, node_type, node_ref, node_name, node_line, node_args, node_body
      return({this_node_id: {"nodeType": node_type, "nodeRef": node_ref, "nodeName": node_name, "nodeLineNumber": node_line, "nodeArgs": node_args, "nodeBody": node_body}})

    

    def getTypes()->list:
      """Gets all the immediately following type declarations for vars, consts, functions, etc"""
      type_list:list = []

      # check that next token is of type EXPRTYPE (:)
      if not peakNextTokenType() == "EXPRTYPE":
        try: raise neh.NexException(f'Expecting TYPE-INDICATOR (:) but found {token_value}({token_type})')
        except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
      else:
        getNextToken()  # eat EXPRTYPE (:)
      
      # TYPE-INDICATOR was found, meaning the loop for finding types can be initiated
      while True:    
        getNextToken()  # the exprType token doesn't contain the type itself, so skip it

        if token_type == "TYPE":
          type_list.append(token_value)
          if peakNextTokenType() in ["EXPRTYPE", "TYPE"]:
            getNextToken()
          else:
            break # exit once the next token isn't related to types
          
        else: 
          try: raise neh.NexException(f'{token_value}({token_type}) is not a valid type')
          except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
        
      return(type_list)
    


    def getParams()->dict:
      """Gets all params/args for an expression declaration or call"""
      params:dict = {}
      
      do_process_tokens = True if peakNextTokenType() == "PARENOPN" else False  # should tokens be processed?
      if do_process_tokens:
        getNextToken()  # eat parenopn so it isn't added to
        while True:
          if peakNextTokenType() == "PARENCLS":
            getNextToken()  # eat parencls so it isn't added to AST
            break
          else:
            params.update(getNode()) # add this node as a param

      return(params)
       


    # get the next token to process into the node
    if peakNextTokenType() != None:
      getNextToken()
    else: token_type = None

    # since there are no more tokens, this node needs to be returned empty
    if token_type == None:
      this_node_id = 0
      node_type = None
      node_ref = None
      node_name = None
      node_line = None
      node_args = None
      node_body = None
      return(formattedNode())


    # start of script
    elif token_type == 'SCPTSTRT':
      this_node_id = node_id  # preserve node_id
      node_type = 'ROOT'       # root / start of script
      node_ref = None          # override to no ref
      node_name = None         # override to no name
      node_line = 0            # override to line 0
      node_args = {}           # override to no args
    
      # start getting child nodes and appending them to body using [dict].update(...)
      while len(token_stack.stack) > 0:
        if peakNextTokenType() == "SCPTEND":
          getNextToken() # eat scptend so it isn't added
          break
        else: node_body.update(getNode())  # scptstrt is root of AST ... body is all other nodes as children ... this is iterative


    # end of script shouldn't be stored
    elif token_type == "SCPTEND":
      try: raise neh.NexException(f"SCRPTEND token wasn't eaten as expected")
      except neh.NexException as err: neh.nexError(err, True, script_name, node_line)

      node_type = token_type    # end of script
      node_ref = None          # override to no ref
      node_name = None         # override to no name
      node_line = token_line_number
      node_args = {}           # override to no args
      node_body = {}           # override to no body


    # start of an expression
    elif token_type == "EXPRSTRT":
      this_node_id = node_id
      node_type = 'EXPR'       # an expression
      node_ref = None
      node_name = None
      node_line = token_line_number
      node_args = {}

      if peakLastTokenType() == 'OP': is_righthand_side = True  # now handling the right hand side of an assignment

      # all following nodes are children until this expression ends
      while True:
        if peakNextTokenType() == "EXPREND":
          getNextToken()  # eat exprend so it isn't stored as child node
          break
        else: node_body.update(getNode())
    

    # EXPREND isn't stored expressions with nested elements, but it IS stored to separate same-nodal-level elements
    elif token_type == "EXPREND":
      node_type = token_type
      node_ref = token_value
      node_name = None
      node_line = token_line_number
      node_args = {}
      node_body = {}


    # start of a string
    elif token_type == "STRLITERAL":
      this_node_id = node_id
      node_type = token_type
      node_ref = None
      node_name = None
      node_line = token_line_number
      node_args = {}

      # all following nodes are children until this string ends
      while True:
        if peakNextTokenType() == "STREND":
          getNextToken() # eat strend so it isn't stored
          break
        else: node_body.update(getNode())
    

    # end of string shouldn't be returned
    elif token_type == "STREND":
      print('PARSER ERROR - STREND WASN\'T EATEN AS EXPECTED!!')
      node_type = token_type
      node_ref = None
      node_name = None
      node_line = token_line_number
      node_args = {}
      node_body = {}


    # for built in expressions such as var, def, class, etc
    elif token_type == "REF":
      """
      List of built-in ref-typed expressions
      abort, stop, cookie, httpget, httppost, output, sleep, wait, rspns_header, rspns_redir,
      calc, min, max, chr, ord, date, now, today, guid, random,
      def, getglobal, nonlocal, print, return, class, object, self, library, use
      tern, if, switch, when, else, const, var
      """
      
      match token_value:         

        #case "ABORT":


        #case "STOP":


        #case "COOKIE":


        #case "HTTPGET":


        #case "HTTPPOST":


        #case "OUTPUT":


        #case "SLEEP":


        #case "WAIT":


        #case "RSPNS_HEADER":


        #case "RSPNS_REDIR":


        case "CALC":
          """
          example: @calc(@val1 + @val2); @calc(@val3**4)
          evaluates to a numeric literal (float or int) value from a mathematical equation
          """
          this_node_id = node_id
          node_type = token_type
          node_ref = token_value
          node_name = token_value
          node_line = token_line_number
          node_args = {}
          node_args.update({"params":getParams()})
          node_body = {}

          while True:
            if peakNextTokenType() != "METHOD": break
            else: node_args.update({"methods":getNode()})


        #case "MIN":


        #case "MAX":


        #case "CHR":


        #case "ORD":


        #case "DATE":


        #case "NOW":


        #case "TODAY":


        #case "GUID":


        #case "RANDOM":


        case "DEF":
          """
          example: @def foo(num1:int, num2:int):int {
            ...
          }
          """
          this_node_id = node_id
          node_type = token_type
          node_ref = token_value
          #node_name
          node_line = token_line_number
          node_args = {}
          node_body = {}

          # next token type must be arg [node_name]
          if peakNextTokenType() == "ARG":
            getNextToken()
            node_name = token_value
          else:
            try: raise neh.NexException("@DEF requires NAME")
            except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
          
          # get parameters for function definition then return type(s)
          node_args.update({"params":getParams()})
          node_args.update({"returnTypes":getTypes()})

          # get definition (required)
          if peakNextTokenType() == "BRACEOPN":
            getNextToken()  # eat braceopn { so it isn't added to AST
            while True:
              if peakNextTokenType() == "BRACECLS":
                getNextToken() # eat bracecls } so it isn't added to AST
                break
              else: node_body.update(getNode())
          

        #case "GETGLOBAL":


        #case "NONLOCAL":


        case "PRINT":
          """
          example: @print(@someValue);
          prints some value to the operating console
          """
          this_node_id = node_id
          node_type = token_type
          node_ref = token_value
          node_name = token_value
          node_line = token_line_number
          node_args = {}
          node_args.update({"params":getParams()})
          node_body = {}


        case "RETURN":
          """
          example: @return(@someValue);
          return value of a function
          """
          this_node_id = node_id
          node_type = token_type
          node_ref = token_value
          node_name = token_value
          node_line = token_line_number
          node_args = {}
          node_args.update({"params":getParams()})
          node_body = {}


        #case "CLASS":


        #case "OBJECT":


        #case "SELF":


        #case "LIBRARY":


        #case "USE":


        #case "TERN":


        #case "IF":


        #case "SWITCH":


        #case "WHEN":


        #case "ELSE":


        case "CONST":
          """
          example: @const bar:int = 5;
          @const [name]:[type] = [value];
          """
          this_node_id = node_id     # preserve node_id
          node_type = token_type
          node_ref = token_value
          #node_name
          node_line = token_line_number
          node_args = {}
          node_body = {}
         
          # next token must be arg [node_name]
          if peakNextTokenType() == "ARG":
            getNextToken()
            node_name = token_value
          else:
            try: raise neh.NexException(f"@CONST requires NAME")
            except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
          
          # const expression does not require getParams()
          # next part of syntax is always :[TYPE] (exactly one, not "any"-type)
          node_args.update({"returnTypes":getTypes()})

          # exactly one type
          if len(node_args['returnTypes']) > 1 or len(node_args['returnTypes']) == 0:
            try: raise neh.NexException(f"@CONST requires exactly ONE type")
            except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
          
          # type can't be "ANY"
          if node_args['returnTypes'][0] == "ANY":
            try: raise neh.NexException(f"@CONST cannot be of 'ANY' type")
            except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
          
          # must have a value assigned immediately
          if peakNextTokenValue() != "=": # using nextTokenValue since there are many types of OP token_types but only one is allowed
            try: raise neh.NexException(f"@CONST requires ASSIGNMENT (=)")
            except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
          
          if peakNextTokenValue() == "=":
            do_bypass_exprend = True  # bypass the EXPREND auto-insert if it is missing (in this case, it should be missing since an OP is found)


               
        case "VAR":
          """
          example: @var bar:int = 5;
          @var [name]:[type] [(optional) = [value]];
          """
          this_node_id = node_id     # preserve node_id
          node_type = token_type
          node_ref = token_value
          #node_name
          node_line = token_line_number
          node_args = {}
          node_body = {}
         
          # next token must be arg [node_name]
          if peakNextTokenType() == "ARG":
            getNextToken()
            node_name = token_value
          else:
            try: raise neh.NexException(f"@VAR requires NAME")
            except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
          
          # var expression does not require getParams()               
          # next part of syntax is always :[TYPE] ... or multiple types (the types the variable can be, ie returnTypes)
          node_args.update({"returnTypes":getTypes()})
          
          if peakNextTokenType() not in ["OP", "EXPREND"]:
            try: raise neh.NexException(f"@VAR expecting ASSIGNMENT (=) or EXPRESSION END (;)")
            except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
          
          if peakNextTokenValue() == "=":
            do_bypass_exprend = True  # bypass the EXPREND auto-insert if it is missing (in this case, it should be missing since an OP is found)


        # Other REF-typed tokens
        case _:
          print(f"Parser Warning B - REF-typed token {token_value} is not implemented in parser yet. Attempted to create node anyway.")
          node_type = token_type
          node_ref = token_value
          node_name = "MISSING"
          node_line = token_line_number
          node_args = {}
          node_body = {}

      
      # at this point an end of expression is always expected ... if expression end is missing, add it
      # exception to this rule is vars and consts, which may be assigned a value before expr end
      if peakNextTokenType() != "EXPREND" and not do_bypass_exprend:
        token_stack.insert(token_line_number, "EXPREND", ";", 0)

        
    # for built in operators such as +, =, etc
    elif token_type == "OP":
      """
      List of built in operators:
      +, -, *, /, **, //, %, +=, -=, *=, /=, =
      """

      match token_value:
        case "+":
          """Adds right value to left value"""
          node_type = token_type
          node_ref = token_value
          node_name = "ADD"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "-":
          """Subtracts right value from left value"""
          node_type = token_type
          node_ref = token_value
          node_name = "SUBTRACT"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "*":
          """Multiplies left value by right value"""
          node_type = token_type
          node_ref = token_value
          node_name = "MULTIPLY"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "/":
          """Divides left value by right value"""
          node_type = token_type
          node_ref = token_value
          node_name = "DIVIDE"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "**":
          """Raises left value to power of right value"""
          node_type = token_type
          node_ref = token_value
          node_name = "NPOW"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "//":
          """nth root of left value (where n is right value)"""
          node_type = token_type
          node_ref = token_value
          node_name = "NROOT"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "%":
          """Modulates left value by right value"""
          node_type = token_type
          node_ref = token_value
          node_name = "MODULO"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "+=":
          """Adds right value to left expression value and assigns result to left expression"""
          node_type = token_type
          node_ref = token_value
          node_name = "ADDANDEQ"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "-=":
          """Subtracts right value from left expression value and assigns result to left expression"""
          node_type = token_type
          node_ref = token_value
          node_name = "DIVANDEQ"
          node_line = token_line_number
          node_args = {}
          node_body = {}
         


        case "*=":
          """Multiplies left expression value by right value and assigns result to left expression"""
          node_type = token_type
          node_ref = token_value
          node_name = "MULANDEQ"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "/=":
          """Divides left expression value by right value and assigns result to left expression"""
          node_type = token_type
          node_ref = token_value
          node_name = "DIVANDEQ"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case "=":
          """Assigns right value to left expression"""
          node_type = token_type
          node_ref = token_value
          node_name = "EQUALS"
          node_line = token_line_number
          node_args = {}
          node_body = {}


        case _:
          print(f"Parser Warning C - {token_value} ({token_type}) not implemented in parser yet. Attempted to create node anyway.")
          node_type = token_type
          node_ref = token_value
          node_name = None
          node_line = token_line_number
          node_args = {}
          node_body = {}


    # for generic arg-typed tokens
    elif token_type == "ARG":
      # this is a user defined function, object, or variable call
      if peakLastTokenType() == "EXPRSTRT":
        this_node_id = node_id
        node_type = "REF"
        node_ref = "ARG"
        node_name = token_value
        node_line = token_line_number
        node_args.update({"params":getParams()})
        node_body = {} # empty or attached methods

        # get attached methods
        while True:
          if peakNextTokenType() != "METHOD": break
          else: node_args.update({"methods":getNode()})

        # end of methods implies end of expression ... if expression end is missing, add it
        if peakNextTokenType() != "EXPREND":
          token_stack.insert(token_line_number, "EXPREND", ";", 0)

        # this node is a user defined ref-call that is on the right-side of an expression ... therefore it MUST have an implied end
        if is_righthand_side:
          #is_righthand_side = False # reset
          token_stack.insert(token_line_number, "EXPREND", ";", 0)


      # this is a definition parameter
      elif peakNextTokenType() == "EXPRTYPE":
        node_type = token_type
        node_ref = token_value
        node_name = "PARAM"
        node_line = token_line_number
        node_args = {}
        node_body = {}
        
        # get allowed types for this param
        node_args.update({"returnTypes":getTypes()})

        # assign default value, delimit, or see end of params.
        if peakNextTokenType() not in ["OP", "EXPRDLM", 'PARENCLS']:
          try: raise neh.NexException(f"PARAMETER expecting ASSIGNMENT (=) or DELIM (,)")
          except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)

        
      # generic arg (such as literals, strings, etc)
      elif peakLastTokenType() != "EXPRSTRT":  
        node_type = "ARG"
        node_ref = "ARG"
        node_name = "LITERAL"
        node_line = token_line_number
        node_args.update({"types":determineNexusType(token_value), "value":token_value})
        node_body = {} # this will always be empty for generic args as they never have bodies/children


    elif token_type == "METHOD":
      # format: @expr.meth().meth().meth()...
      this_node_id = node_id
      node_type = token_type
      node_ref = token_value
      #node_name
      node_line = token_line_number
      node_args = {}
      node_body = {}

      # next token must be arg [node_name]
      if peakNextTokenType() == "ARG":
        getNextToken()
        node_name = token_value
      else:
        try: raise neh.NexException(f"METHOD requires NAME")
        except neh.NexException as err: neh.nexError(err, True, script_name, token_line_number)
      
      # next token must be args (even if none/null/blank are supplied)
      node_args.update({"params":getParams()})
      

    # catch-all for missing items
    else:
      print(f"Parser Warning A - {token_value} ({token_type}) not implemented in parser yet. Attempted to create node anyway.")
      node_type = token_type
      node_ref = None
      node_name = token_value
      node_line = token_line_number
      node_args = {}
      node_body = {}



    # RUNS AFTER THE IF/ELSE STATEMENT FOR PARSING NODES BASED ON TOKEN TYPES
    this_node_id = node_id if this_node_id is None else this_node_id   # is node_id unless a value is assigned
    return(formattedNode(this_node_id))
      


  # initialize the building of the node tree
  #if current_node is None: current_node = getNode()

  # continue looping until end of token stack 
  while len(token_stack.stack) > 0:
    current_node = getNode()   # get the next node
    obj_AST.update(current_node)   # put into tree
    current_node = None        # reset for next node

  # print parser warnings then clear
  if len(neh.warnings) != 0:
    print('PARSER WARNINGS:')
    for warning in neh.warnings:
      print(warning)
    neh.warnings.clear()

  #print(json.dumps(obj_AST.tree, indent=2))  # USED FOR DEBUGGING
  return ((obj_AST, script_name))
