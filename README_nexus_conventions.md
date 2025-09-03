# Project Naming Conventions

Note: These conventions apply to code written in the Nexus language, not the Nexus Python Project. Additionally, this document is very likely to evolve while the language is being developed.

In an effort to keep naming consistent across Nexus code, the following variable, constant, function, method, and class naming conventions are used:

| Construct | Convention | Example           |
|-----------|------------|-------------------|
|Variables  |`snake_case`|`user_first_name`  |
|Constants  |`SNAKE_CASE`|`MAX_RETRIES`      |
|Functions  |`snake_case`|`parse_tokens(...)`|
|Methods    |`snake_case`|`pop_token(...)`   |
|Classes    |`PascalCase`|`TokenStack()`     |
|Files      |`PascalCase`|`_OnStart.nex`     |

## Notes

- Functions should come in verb-noun pairs such as `parse` and `tokens` becoming `parse_tokens([params])`.
- Booleans are prefixed with "is", "has", "can", or similar; for example, `is_active`.
- Variables should have explicit units when applicable (`delay_seconds`) and are written in all lower case.
- Constants are similar to variables but are written in all upper case (`MAX_CONNECTIONS`).
- Abbreviations are strictly forbidden, unless they are common such as "ID", "URL", or "AST".
- Classes are common abbreviations (uppercase) or single to multi-noun pairs (PascalCase) such as `AST`, `AbstractSyntaxTree`, `TokenStack`.
- Objects follow variable naming conventions as they are named references to instances of developer-defined types; for example `@var token_stack:TokenStack = TokenStack();`
- Type declarations for built in classes are all lowercase, such as typing `@var my_string:str = "...";`.
- Type declarations are always required.
- All reference-calls, be it variables, constants, functions, methods, classes, or objects, must end with `()`. This is a space to pass in parameters, if any are supplied. This applies even to variables and constants, which do not actually take in parameters.
- Reference calls ideally end with a `;` but this is not strictly required.
- While Nexus is case-insensitive, the case conventions should still be followed.

## Example

In order to illustrate the above conventions, the following example code will be used. The code establishes a class with an initialization and one method. An instance (object) typed to that class is created. A function is defined that returns the method from the object instance and returns data. That data is printed.

### WARNING! THE LANGUAGE IS STILL IN DEVELOPMENT SO THESE CONVENTIONS AND THIS SPECIFIC EXAMPLE ARE BOTH EXTREMELY LIKELY TO CHANGE AND BE UPDATED OVER TIME

Here is the more detail example of what the code might look like:

<!-- C# used as the code block "language" as Nexus syntax highlighting doesn't exist yet ... C# happened to work well enough -->
```C#
# class convention
@class User {
  # method convention
  @def init():none {
    # automatically scoped to @self
    # variable convention
    @var user_id:int;
    @var first_name:str;
    @var last_name:str;
  }

  @def lookup_user(@self, user_id:int):object {
    # [hypothetical database lookup here]
    @self.user_id = @user_id();
    @self.first_name:str = @database_result[first_name];
    @self.last_name:str = @database_result[last_name];
  }
}


# object instance convention
@var user:object = @User();

# constant convention
@const USER_ID:int = 1;


# function convention
@def establish_user(user_id:int):json {
  @user_data:json = @user.lookup_user(@user_id());
  @return(@user_data());
}


@print(@establish_user(@USER_ID()));

```
