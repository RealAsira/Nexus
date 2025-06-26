# Project Naming Conventions

Note: These conventions apply to the Nexus Python Project, not code written in the Nexus language itself.

In an effort to keep naming consistent across this project, the following variable, constant, function, method, and class naming conventions are used:

| Construct | Convention | Example          |
|-----------|------------|------------------|
|Variables  |`snake_case`|`user_first_name` |
|Constants  |`SNAKE_CASE`|`MAX_RETRIES`     |
|Functions  |`camelCase` |`parseTokens(...)`|
|Methods    |`camelCase` |`popToken(...)`   |
|Classes    |`PascalCase`|`TokenStack`      |
|Files      |`PascalCase`|`NexServer.py`    |

## Notes

- Python typically uses snake case for function names. For the sake of unique-ness (between vars vs functions) and consistency between a variety of languages, camelCase is used for functions instead.
- Functions should come in verb-noun pairs such as `parse` and `tokens` becoming `parseTokens()`.
- Booleans are prefixed with "is", "has", "can", or similar; for example, `is_active`.
- Variables should have explicit units when applicable (`delay_seconds`) and are written in all lower case.
- Constants are similar to variables but are written in all upper case (`MAX_CONNECTIONS`).
- Abbreviations are strictly forbidden, unless they are common such as "ID", "URL", or "AST".
- Classes are common abbreviations (uppercase) or single to multi-noun pairs (PascalCase) such as `AST`, `AbstractSyntaxTree`, `TokenStack`.
- Objects follow variable naming conventions as they are named references to instances of developer-defined types; for example `token_stack:TokenStack = TokenStack()`
- Type declarations for built in classes are all lowercase, such as typing `my_string:str = "..."`.
- Type declarations are used whenever possible.

## Example

In order to illustrate the above conventions, the following example code will be used. The code establishes a class with an initialization and three additional methods. Constants are declared to be used with the initialization (object instantiation) of the class. A function declaration is made to operate on (in this case, retrieve) data from the class. The function is called and the returned data is printed.

Here is the more detail example of what the code might look like:

```Python
# class convention
class Database():
  def __init__(self, DB_NAME:str, DB_PASSWORD:str):
    """Establish a new database"""
    self.DB_NAME:str = DB_NAME
    self.DB_PASSWORD:str = DB_PASSWORD

  # method convention
  def openConnection(self)->None:
    """Connect to the database"""
    ...

  def closeConnection(self)->None:
    """Disconnect from database"""
    ...

  def runQuery(self, query:str)->object:
    """Query the database and return respone as an object"""
    ...


# constant convetion
PRIMARY_DB_NAME:str = "ExampleDB"
PRIMARY_DB_PASSWORD:str = "dontgetanyideas"
TEST_USER_ID:int = 1

# object instance convention
example_database:Database = Database()


# function convention
def getUserData(user_id:int)->object:
  # variable convention
  user_data_query:str = f"""
  SELECT user_id, first_name, last_name
  FROM dbo.users WHERE user_id = {user_id}
  """

  # object with method call convention
  example_database.openConnection()
  user_data:object = example_database.runQuery(user_data_query)
  example_database.closeConnection()
  return(user_data)

if __name__ == "__main__":
  user_data:object = getUserData(TEST_USER_ID)
  print(str(user_data))

```
