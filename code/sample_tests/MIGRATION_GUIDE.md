# Migration Guide: Removing Traditional Approach

This guide provides step-by-step instructions for migrating from the traditional inheritance-based approach to the plugin framework approach.

## Overview

The traditional approach uses:
- `WP_APIs.py` - Classes inheriting from `API` base class
- Manual `AssertTest` and `AssertSearch` functions
- Individual class instances for each API operation

The plugin framework uses:
- `wp_api_client.py` - Single client class with composition
- PyTest fixtures and assertion helpers
- Type-safe, modern Python patterns

## Migration Steps

### Step 1: Identify Files to Migrate

Files that need migration:
- `test_wpT01.py` → `test_wpT01_migrated.py` ✅
- `test_wpT02.py` → `test_wpT02_migrated.py` ✅

### Step 2: Update Import Statements

**Before (Traditional):**
```python
from apis import WP_APIs
from pyrest.util import AssertTest
```

**After (Plugin Framework):**
```python
from apis.wp_api_client import wp_client, authenticated_wp_client, assert_api
```

### Step 3: Replace API Calls

**Before (Traditional):**
```python
test = WP_APIs.GetPages(env=env)
test.CallAPI()
test.Call_Succeeded(test)
AssertTest(testObject=test, assertTest="len(test.content) > 10", 
           message="There was no data sent back from the call")
```

**After (Plugin Framework):**
```python
response = wp_client.get_pages()
assert_api.status_code(response, 200)
assert_api.has_content(response)
assert len(response.content) > 10, "There was no data sent back from the call"
```

### Step 4: Replace Authentication Patterns

**Before (Traditional):**
```python
test = WP_APIs.PostNewPost(user='testAdmin01', data=data, env=env)
```

**After (Plugin Framework):**
```python
response = authenticated_wp_client.create_post(
    title=post_title,
    content=content,
    status="publish"
)
```

### Step 5: Update Test Functions

**Before (Traditional):**
```python
def test_tmp():
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    # ... test code ...
```

**After (Plugin Framework):**
```python
@pytest.mark.api
def test_get_pages():
    """Migrated version of test_tmp() using plugin framework"""
    test_name = inspect.stack()[0][3]
    myLogger.info("Test " + test_name + " is starting")
    # ... test code ...
```

## Files to Remove

Once migration is complete, these files can be safely removed:

1. `code/sample_tests/apis/WP_APIs.py`
2. `code/sample_tests/test_wpT01.py` (after confirming migrated version works)
3. `code/sample_tests/test_wpT02.py` (after confirming migrated version works)

## Files to Update

1. `code/sample_tests/PLUGIN_VS_TRADITIONAL.md` - Update to reflect migration status
2. Any documentation that references the traditional approach

## Testing the Migration

1. Run the original tests to establish baseline:
   ```bash
   pytest code/sample_tests/test_wpT01.py -v
   pytest code/sample_tests/test_wpT02.py -v
   ```

2. Run the migrated tests to ensure they work:
   ```bash
   pytest code/sample_tests/test_wpT01_migrated.py -v
   pytest code/sample_tests/test_wpT02_migrated.py -v
   ```

3. Compare results to ensure functionality is preserved

## Benefits of Migration

1. **Cleaner Code**: Less boilerplate, more readable
2. **Better Error Handling**: Clear error messages and validation
3. **Type Safety**: Full type hints and IDE support
4. **PyTest Integration**: Automatic fixtures and markers
5. **Maintainability**: Easier to extend and modify
6. **Consistency**: All tests use the same modern patterns

## Rollback Plan

If issues arise during migration:

1. Keep original files until migration is fully tested
2. Use feature flags or environment variables to switch between approaches
3. Maintain both versions temporarily if needed

## Final Cleanup

After successful migration:

1. Remove traditional approach files
2. Update documentation
3. Remove any remaining references to `WP_APIs`
4. Clean up any unused imports or dependencies

## Common Migration Patterns

### Pattern 1: Simple GET Request
```python
# Traditional
test = WP_APIs.GetPages(env=env)
test.CallAPI()
test.Call_Succeeded(test)

# Plugin Framework
response = wp_client.get_pages()
assert_api.status_code(response, 200)
assert_api.has_content(response)
```

### Pattern 2: Authenticated POST Request
```python
# Traditional
test = WP_APIs.PostNewPost(user='admin', data=data, env=env)
test.CallAPI()
test.Call_Succeeded(test, return_code="201")

# Plugin Framework
response = authenticated_wp_client.create_post(
    title=title,
    content=content,
    status="publish"
)
assert_api.status_code(response, 201)
assert_api.has_content(response)
```

### Pattern 3: Error Testing
```python
# Traditional
test = WP_APIs.GetPosts_bad(env=env)
test.CallAPI()
test.Call_Failed(test, return_code="404", returns_content='yes')

# Plugin Framework
response = wp_client.get_post(99999)  # Non-existent post
assert_api.status_code(response, 404)
```
