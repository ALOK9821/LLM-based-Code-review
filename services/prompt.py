def promptV1(code):
    prompt = f"""
    You are given code snippets from a GitHub pull request in the format {{ "line number": "code" }}. 
    Each line represents code that has been added or modified in the pull request. 
    You are tasked with performing a code review based on the following criteria:
        Code Style and Formatting: Identify any style or formatting issues, such as line length, indentation, or spacing inconsistencies.
        Potential Bugs or Errors: Detect potential bugs, logical errors, or cases where variables may be used without initialization.
        Performance Improvements: Suggest any potential optimizations to improve code efficiency or performance.
        Best Practices: Flag any issues where the code does not follow best practices for Python, such as import usage, function naming conventions, or readability enhancements.
    Input Format
        The code is presented as pairs in the format {{ "line number": "code" }}, where:
            The first element of each pair is the line number in the actual file.
            The second element is the string containing the line of code at that line number.
    Example Input: 
       {{
            "42": "from pandas.util._decorators import (",
            "43": "    cache_readonly,",
            "44": "    set_module,",
            "45": ")",
            "144": "@set_module(\\"pandas\\")",
            "509": "@set_module(\\"pandas\\")"
        }}

    Output Format:
        Return a JSON object with a single key, issues, containing an array of up to ten issue objects (if more than ten issues are found, return only the first ten). 
        Each issue object should have the following keys:
            type: Type of issue identified (style, bug, performance improvement, or best practice).
            line: Line number where the issue is found.
            description: A concise one-line description of the issue.
            suggestion: A concise one-line suggestion to resolve the issue.
    
    Example Output:
        {{
            "issues": [
                {{
                    "type": "style",
                    "line": 15,
                    "description": "Line too long",
                    "suggestion": "Break line into multiple lines"
                }},
                {{
                    "type": "bug",
                    "line": 23,
                    "description": "Potential null pointer",
                    "suggestion": "Add null check"
                }}
            ]
        }}
    Additional Important Notes:
        If the code adheres to all review criteria, return an empty list for issues.
        Limit the response to a maximum of ten issues if more than ten are found.
        Be concise and precise in your descriptions and suggestions.
        Skip the lines of code where you are unsure or it cannot be reviewed without extra code from file (currently only code that is changed in the PR is given).
        Code for Review: {code}
    """
    
    return prompt
