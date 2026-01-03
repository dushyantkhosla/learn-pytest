## Unit tests 

- validate the behavior of a small piece of code, like a function or a method
- typically fast, deterministic and easy to run
- help catch bugs
- help make refactoring safer by checking things don't break as a side effect
- help document how code is supposed to behave 

## Patching

Monkey patching is a technique to *dynamically modify or extend* existing classes or functions *at runtime* so we don't actually need to perform an expensive operation (like an API call) for testing the code around it.

For example, let's say we have a function that calls an external API to fetch the weather
Now, we haven't authored the API so we're not testing the API
What we are testing is our function that does something with the response

```python
monkeypatch.setattr("httpx.get", fake_get)
```

The `get_temperature` method of `WeatherService` relies on an API call
Using `monkeypatch.setattr`, we replace the `httpx.get` function with our own patch `fake_get` and proceed as usual

See below for the full example

```python
# --- weather.py ---
class WeatherService:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    def get_temperature(self, city: str) -> float:
        response = httpx.get(
            "https://api.weatherapi.com/v1/current.json",
            params={"key": self.api_key, "q": city},
        )
        response.raise_for_status()
        data = response.json()
        return data["current"]["temp_c"]
        
# --- test_weather.py ---
from weather import WeatherService
import pytest
from typing import Any

def test_get_temperature_with_monkeypatch(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, params: dict[str, Any]) -> Any:
        class FakeResponse:
            def raise_for_status(self) -> None: pass
            def json(self) -> dict[str, Any]:
                return {"current": {"temp_c": 19}}
        return FakeResponse()

    monkeypatch.setattr("httpx.get", fake_get)
    service = WeatherService(api_key="fake-key")
    temp = service.get_temperature("Amsterdam")
    assert temp == 19
```

## Mocking

Mocking refers to *creating simulated objects* that replicate the behavior of real objects in a controlled way. A method can be mocked to return a fixed value, allowing you to test it without depending on the actual implementation.

```python
# --- test_weather.py ---
from unittest.mock import MagicMock, patch
import pytest
from weather import WeatherService

def test_get_temperature_with_mocking() -> None:
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {"current": {"temp_c": 25}}

    with patch("httpx.get", return_value=mock_response) as mock_get:
        service = WeatherService(api_key="fake-key")
        temp = service.get_temperature("London")

        assert temp == 25
        mock_get.assert_called_once()
```


## Mocking vs Patching

|Feature|Mocking|Monkey Patching|
|---|---|---|
|Purpose|Simulate behavior for unit testing|Modify classes or functions at runtime|
|Control|Controlled via mock configurations|Direct alteration of the original code|
|Scope|Isolated to the test|Affects all instances of the class|
|Use Cases|Unit tests with dependencies|Quick fixes or tests without re-deploy|
Mocking is generally safer for isolating tests, while monkey patching is more intrusive and can lead to unintended side effects if not used carefully.
## Fixtures

`pytest` fixtures are 
- a way of providing *data*, test doubles, or *state setup and teardown* to your tests
	- especially useful when many different tests need the same data or objects
- functions that can return a wide range of values
- explicitly passed as arguments to tests
- **modular**, which means they can be imported, can import other modules, and can depend on and import other fixtures

If we have several tests that rely on a list of user data, we can create a fixture to hold this data and inject it to tests that need it

```python
@pytest.fixture
def user_data():
    return [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35}
    ]

# Test function to check for a specific user by name and age
def test_user_exists(user_data):
    user = {"name": "Alice", "age": 30}

    # Check if the target user is in the list
    assert user in user_data

# Test average age of users
def test_average_age(user_data):
    ages = [user["age"] for user in user_data]
    avg_age = sum(ages) / len(ages)
    assert avg_age == 30
```

### `conftest.py`

`pytest` looks for a `conftest.py` module in each directory. Fixtures placed in this file can be used throughout the module’s parent directory and in any subdirectories *without having to import it* 

## Marks

- a way to avoid running _all_ the tests each time
- pytest allows you to *mark a test* with any number of *categories* 
- if some tests require access to a db, we can create a `@pytest.mark.db_access` mark
- to only run tests that require db access, use `pytest -m db_access`
- to run all tests except these, use `pytest -m "not db_access"`

`pytest` provides a few marks out of the box:
- **`skip`** to skip a test unconditionally
- **`skipif`** skips a test if the expression passed to it evaluates to `True`
- **`xfail`** indicates that a test is expected to fail, so if the test _does_ fail, the overall suite can still result in a passing status
- **`parametrize`** creates multiple variants of a test with different values as arguments. You’ll learn more about this mark shortly

```python
 @pytest.mark.skip(reason="Feature not yet implemented")
 def test_feature():
     pass
 
 @pytest.mark.skipif(sys.platform == "win32", reason="does not run on windows")
 class TestClass:
     def test_function(self):
         "This test will not run under 'win32' platform"

 @pytest.mark.xfail(reason="division by zero not handled yet")
 def test_divide_by_zero():
     assert divide(10, 0) == 0
```

### Parametrization

- if there are several tests with slightly different inputs and expected outputs
- argument 1 to `parametrize()` is a comma-delimited string of parameter names
- argument 2 is a list of 1D values or tuples that represent the parameter values

```python
@pytest.mark.parametrize("palindrome", [
    "",
    "a",
    "Bob",
    "Never odd or even",
    "Do geese see God?",
])
def test_is_palindrome(palindrome):
    assert is_palindrome(palindrome)
```


## Duration Reports

- `pytest` can automatically record test durations for you and report the top offenders.
- Use the `--durations=N` option to get a duration report in your test results
	- here, N represents the N slowest tests
- Each test that shows up in the durations report is a good candidate to speed up because it takes an above-average amount of the total testing time.

```bash
(venv) $ pytest --durations=5
```

## Plugins

- [`pytest-randomly`](https://github.com/pytest-dev/pytest-randomly) forces your tests to run in a random order.
	- great way to discover tests that have a **stateful dependency** on some other test
- [`pytest-cov`](https://pytest-cov.readthedocs.io/en/latest/) integrates coverage, so you can run `pytest --cov` to see the test coverage report
- `pytest-xdist` for running tests in parallel (`pytest -n 4`)