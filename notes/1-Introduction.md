## Topics

- Directory structure (`/tests` at root)
- pytest discovery (naming with `test_*`)
- Writing simple tests
- Import functions from `src` into `tests/test_*.py`
- Running tests
- Atomicity - each test should concern just *one thing*
- pytest **Markers** - organise and run specific groups of tests 
- pytest **Hooks**
- **Fixtures** for classes and db connections + teardown
	- **Custom fixtures**
- **Parameterised** testing with `@pytest.mark.parameterize`
- **Mocks** for db or APIs - using `mocker.patch` or `unittest.mock.MagicMock`
- Checking if a function fired with `assert_called_once_with`
- VSCode settings for pytest - tell the IDE where to find tests
- Built-in testing of API frameworks like Flask, Django, FastAPI with **testing mode**
- Advanced features - **plugins**, running tests in **parallel**, code **coverage**

## Why write Unit tests?

- to ensure that we get the expected result from a unit of code
- cover a majority of the code
- ensure all components are working as intended
- if there is an error, we can isolate the source and implement a fix 

### Advice for writing unit tests

- make sure that you're covering as many things as possible
- consider edge cases, empty inputs, weird errors

### Other types of tests

- Integration 
- System
- End-to-end

## What is Pytest

- Pytest is a Python testing framework that makes it easy to write small, scalable, and highly maintainable test cases.
- It supports fixtures, parameterized testing, and plugins to extend its capabilities.

### Why Use Pytest

- Simple syntax for writing tests.
- Automatic test discovery.
- Rich ecosystem of plugins.
- Built-in support for fixtures and mocking.

### Features

- **Fixtures** for handling test dependencies, state, and reusable functionality
- **Marks** for categorizing tests and limiting access to external resources
- **Parametrization** for reducing duplicated code between tests
- **Durations** to identify your slowest tests
- **Plugins** for integrating with other frameworks and testing tools

## Dependencies

```bash
uv pip install pytest pytest-mock
```

## Directory Structure

```bash
my_project/
├── src/
│   └── my_code.py
└── tests/
    └── test_my_code.py
├── pyproject.toml    
```

Add the following lines to your `pyproject.toml`

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
```

With this, when importing functions from `src` in `tests` reference them as 

```python
from user import get_userame 

# not like this
# from src.user import get_username
```

## Writing a Test

- import the target function from another module that you want to test
- write a test function with an `assert` statement
	- these can optionally include a string message
- use the same name as the target function, prefixed with `test_`
- if the assert returns `False`, the test has failed

```python
# --- src/code.py ---
def add(a, b):
    return a + b

# --- tests/test_code.py ---
from src.code import add
def test_add():
	assert add(1, 4) == 5, "1 + 4 should be 5"
	assert add(1, -1) == 0, "1 - 1 should be 0"
```

Run the test with

```bash
pytest tests/test_code.py
```

### Testing error handling

- to test whether a try-except/error handling block is working
- we use `pytest.raises` and specify the *exception* and an *error string*

```python
# ---- ./main.py ----
def divide(a, b): 
	if b == 0:
		raise ZeroDivisionError("Cannot divide by zero")
	return a / b
	
# ---- ./tests/test_main.py ----
def test_divide():
	with pytest.raises(ZeroDivisionError, match="Cannot divide by zero")
		divide(10, 0)
```

Raise
- `ValueError` when a function receives an argument with an incorrect value
- `TypeError` when an operation is applied to an object of an inappropriate type
- `KeyError` when we try to access a dictionary key that doesn’t exist
## Running Tests

- running `pytest` on your Terminal will automatically look for and run all files of the form `test_*.py` or `*_test.py` in the current directory and subdirectories

To run tests 
- in a specific file, use `pytest test_app.py`
- in a specific directory, use `pytest tests/`
- using specific keywords, write `pytest -k "keyword"`
	- pytest will look for functions, classes, or files matching that keyword in the current directory and subdirectories and run them
- a single test in a particular module, `pytest test_app.py::test_get_user`
- `pytest --html=report.html` generates a report, requires the `pytest-html` plugin

## Fixtures 

- When testing logic or functionality we want to start with a blank slate
	- This is to avoid the run of one test impacting the run of another
	- Tests should be run in isolation
- *Fixtures* run before tests they're *injected* into, usually for a *setup* 
- In the example below, to test the functionality of `UserManager` we use a fixture to create a fresh instance before each test

```python
from users import UserManager

@pytest.fixture
def user_manager():
	return UserManager()
	
def test_add_user(user_manager):
	assert user_manager.add_user("john doe", "john@doe.com") == True
	assert user_manager.get_user("john doe") == "john@doe.com"
	
def test_add_duplicate_user(user_manager):
	user_manager.add_user("john doe", "john@doe.com")
	with pytest.raises(ValueError):
		user_manager.add_user("john doe", "john@doe.com")
```

### Teardown

- the `yield` keyword provides an instance when called
	- code that comes before `yield` is used for set up
	- code that comes after `yield` is used to teardown or cleanup

```python
from db import Database

@pytest.fixture
def db():
	database = Database()
	yield database
	database.data.clear()
	
def test_add_user(db):
	db.add_user(1, "Alice")	
	assert db.get_user(1) == "Alice"
```

## Parameterized Testing

- convenient way to avoid writing multiple asserts
- especially useful when testing the same function for a list of inputs
- the `parameterize` decorater takes 
	- a comma-separated string listing the inputs and expected
	- a list of tuples containing the input and expected values

```python
from main import is_prime

@pytest.mark.parameterize("num, expected", [
	(1, False),
	(2, True),
	(3, True),
	(4, False),
	(17, True),
	(19, True),				
])
def test_is_prime(num, expected):
	assert is_prime(num) == expected
```

## Mocking

- testing code that's not a part of the testing environment
- let's say some front-end code relies on an API call
	- we don't want to deploy the API just for testing
	- instead we "mock" or create a version of the dependency that returns fake data
	- this avoids having to actually send an API request 
- finally, we can also check whether a mock we created was called or not

```python
# --- ./main.py ...
import requests
def get_weather(city):
	response = requests.get(f"https://api.weather.com/v1/{city}")
	if response.status_code == 200:
		return response.json()
	else:
		raise ValueError("Could not fetch weather data")
		
# --- ./tests/test_main.py ---
import pytest
from main import get_weather
def test_get_weather(mocker):
	mock_get = mocker.patch("main.requests.get")		
	mock_get.return_value.status_code = 200
	mock_get.return_value.json.return_value = {"temp": 25, "condition": "Sunny"}
	
	result = get_weather("Dubai")
	
	assert result == {"temp": 25, "condition": "Sunny"}
	mock_get.assert_called_once_with("https://api.weather.com/v1/Dubai")
```

### Patching Functions

In the example above, to test the `get_weather` function without calling the API, we need to *modify or patch* the behavior of its `requests.get()` method

Steps:
- create a `mock_get` by initializing a patch for the `main.requests.get` call
- modify the `return_value`(s) so the patch gives a value without making a get request 
- run the `get_weather` function, which will now use the patched `requests.get`
- write assertions
- check if the `mock_get` patch was called correctly

### Patching Classes

- To test a service, without relying on an API - we can mock the API client
- We mock classes using `mocker.Mock(spec=MyClass)`
	- Then, we patch the functions within the class 
	- Use the patched client and test the result
- Use  `assert_called_once_with(value)` to confirm that the API client was called

```python
# --- service.py ---
class APIClient():
	def get_user_data(self, user_id):
		response = requests.get(f"https://api.example.com/users/{user_id}")
		if response.status_code == 200:
			return response.json()
		raise ValueError("API Request Failed")

class UserService:
	def __init__(self, api_client):
		self.api_client = api_client
	def get_username(self, user_id):
		user_data = self.api_client.get_user_data(user_id)
		return user_data["name"].upper()
		
# --- test_service.py ---
from service import APIClient, UserService

def test_get_username(mocker):
	mock_api_client = mocker.Mock(spec=APIClient)		
	mock_api_client.get_user_data.return_value = {"id":1, "name":"Alice"}
	service = UserService(mock_api_client)
	result = service.get_username(1)
	
	assert result == "ALICE"
	mock_api_client.get_user_data.assert_called_once_with(1)
```

## Testing a Flask API

- frameworks usually have testing built-in, or specify ways to perform testing

```python
# --- api.py ---
from flask import Flask, jsonify, request
app = Flask(__name__)
users = {} # simulates an in-memory db

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
	user = users.get(user_id)
	if user:
		return jsonify({"id": user_id, "name": user}), 200
	return jsonify({"error": "User not found"}), 404
	
# --- test_api.py ---	
import pytest
from api import app

@pytest.fixture
def client():
	app.config["TESTING"] = True        # enables testing mode
	with app.test_client() as client:
		yield client                    # provides a test client instance
		
def test_get_user(client):
	client.post('/users', json={"id": 2, "name": "Bob"})
	response = client.get('/users/2')
	assert response.status_code == 200
	assert response.json() == {"id": 2, "name": "Bob"}
```
