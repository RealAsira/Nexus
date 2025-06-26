"""
This module uses custom error handling for Nexus

fatal False = warning, True = fatal error
moduleName is the nexus (.nex) file
lineNumber is the line number in the .nex file where the error occurred

example:

import NexErrorHandler as neh
try: raise neh.NexException('[errorMessage]')
except neh.NexException as err: neh.nexError(err, [fatal], '[moduleName]', [lineNumber]) 
"""



fatalError:str = ''     # if value is assigned, stop interpreting and return this value only
warnings:list = []      # a list of warnings that may not be fatal ... print to console



class NexException(Exception):
  def __init__(self, msg):
    """child of Exception class ... eg, raise Exception('errmsg')"""
    super().__init__(msg)

  

def nexError(err:str, fatal=False, module_name:str='Unknown Nexus Module', line_number:int=0):
  """call on nexus exception to handle"""
  global warnings, fatalError

  # ensure proper debug-naming
  if module_name in [None, '']:
    module_name = 'unidentified'
  
  if not fatal:
    warnings.append(f'[WARNING | {module_name.upper()}.NEX | LN {line_number}] {err}.')

  if fatal:
    fatalError = f'[ERROR | {module_name.upper()}.NEX | LN {line_number}] {err}.'
    print(fatalError)

    # this is because error handling hasn't been built into the nexus language itself, yet
    # some level of handling needs to be added to the language before it can be properly handled here
    print('FATAL WARNING: Fatal Errors do NOT stop execution of script')
