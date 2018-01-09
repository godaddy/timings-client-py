# timings-client-py

Client for [Timings API](https://www.github.com/godaddy/timings) to support **Python** based test environments

**NOTE:** you need to have a timings API server running in your network to use this client!

## Purpose

- Sending performance data from functional tests to the [timings API](https://www.github.com/godaddy/timings).
- This client makes it easy to communicate with the API without the need to setup your own curl/request/etc. calls.
- The response contains the necessary fields to validate/assert the performance results (look for the `assert` field!).
- The API stores the results in ElasticSearch and can be visualized with Kibana.
- This helps get better visibility into performance improvements/regression trends before moving into production.

To learn more about ELK (Elastic Search, LogStash, Kibana). Click Here [https://www.elastic.co/products/kibana](https://www.elastic.co/products/kibana)

## Installation

Installation of the client can be done with `pip` or `easy_install`:

```python
pip install timingsclient
```

## Configuration

After installation you first need to copy the configuration file and change it to your needs. The client includes a sample config file that can be found here: `https://github.com/godaddy/timings-client-py/blob/master/timingsclient/default.yaml`. You will pass the location of this config file when you initiate the client (see below)

Add a custom config file to your project's root folder and edit to match your situation. Example:

```yaml
PERF_API_URL: "http://localhost/v2/api/cicd/"    # the full fqdn of the API server
api_timeout: 2               # timeout for the API in seconds (valid range: 2-30 seconds)
api_params:                  # the "api parameters" that will be send to the API in the POST body
 sla:                           # This is the "flat SLA" - valid keys are "pageLoadTime" or "visualCompleteTime"
  pageLoadTime: 2000                # Flat maximum threshold - this will be used if baseline (+ padding) is greater or flags.assertBaseline=false!
 baseline:                      # These settings will be used by the API to calculate the baseline
  days: 7                           # Number of days to calculate the baseline for
  perc: 75                          # Percentile to calculate
  padding: 1.2                      # Extra padding on top of the calculated baseline (gives some wiggle-room)
 flags:                         # These booleans will tell the API what to do
  assertBaseline: true              # Whether or not to compare against baseline
  debug: false                      # Request extra debug info from the API
  esTrace: false                    # Request elasticsearch output from API
  esCreate: false                   # Save results to elasticsearch
  passOnFailedAssert: false         # Pass the test, even when the performance is above the threshold
 log:                           # These key-value pairs will be stored in elasticsearch and can be used to slice & dice the data in Kibana
  test_info: "Demo test"            # Info about the test(-step)
  env_tester: "Windows"             # Environment of the test machine (local, saucelabs, selenium grid, etc.)
  browser: "Demo browser"           # Browser used to run the test with
  env_target: "PROD"                # Environment of the target app (usually dev, test, or prod)
  team: "DEMO TEAM"                 # THe name of the (test-)team
```

NOTE: it is recommended that you **_dynamically_** populate log fields like `browser` and `env_target`.

## Instrumenting your test scripts

To use the client, import it like you would with any python module:

```python
from timingsclient import Perf
```

Then, you can initiate the client, along with the location of your config file, as follows:

```python
# Setup custom config
CONFIG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)),'', 'custom.yaml')
PERF = Perf(CONFIG_FILE)
```

With the client initiated, you can now call the different methods from your script.

### Example test script

Here is an example of a complete test 'navtiming' script:

```python
"""
Selenium Grid with Hub and Node test
"""
import os
import platform
from selenium import webdriver
from timingsclient import Perf

BROWSER = webdriver.Chrome(
    '/Users/mverkerk/selenium/chromedriver_2.34.exe')
BROWSER.get('http://www.seleniumconf.de/test?test=strip_this')

# Perform functional assert
try:
    BROWSER.find_element_by_class_name('section__heading')
    print("FUNCTIONAL: Page looks good!")
except:
    print("FUNCTIONAL: Page not working!")

# Setup custom config for PERF
CONFIG_FILE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '', 'config.yaml')

# Initiate client
PERF = Perf(CONFIG_FILE)

# Collect inject code from API (strip query string = True)
INJECT_CODE = PERF.injectjs(inject_type='navtiming', mark='visual_complete', strip_qs=True)

# Set API parameters
API_PARAMS = PERF.getapiparams(es_create=False, log={
    'browser': BROWSER.name, 'env_tester': platform.system()})

if INJECT_CODE is not False:
    # Collect perf data from browser
    TIMING = BROWSER.execute_script(INJECT_CODE)
    # Send perf data with parameters to API
    NAV_RESP = PERF.navtiming(TIMING, API_PARAMS)

    # Assert perf
    if NAV_RESP is not False:
        print(
            'PERFORMANCE of [' + NAV_RESP["export"]["dl"] + '] was ',
            ('GOOD' if NAV_RESP['assert'] is True else "BAD") + '! - ',
            str(NAV_RESP['export']['perf']['measured']),
            '/ ' + str(NAV_RESP['export']['perf']['threshold'])
        )
    else:
        print("NAV_RESP problem!")
else:
    print("INJECT_CODE problem!")

BROWSER.close()

```

## Client methods

### `getapiparams( sla, debug, es_trace, es_create, days, perc, padding, search_url, log )`

Collect or overwrite the default parameters (see above) to be send to the API. None of the parameters are required. If you don't submit any arguments, the defaults will be used. All arguments have to be 'keyed' arguments.

|param|type|default|description|
|-|-|-|-|
|sla|dict|-|Overwrite the default `sla` settings
|debug|boolean|`false`|Receive extra debug information from the API
|esTrace|boolean|`false`|Request Elasticsearch query information from the API
|esCreate|boolean|`true`|Save the result to elasticsearch
|days|number|`7`|Number of days to calculate the baseline for
|perc|number|`75`|Percentile of the baseline to be calculated
|padding|number|`1.2`|Multiplier to calculate extra padding on top of the baseline
|searchUrl|string|`''`|Wildcard to use for baseline (instead of using the submitted URL)
|log|dict|-|Object that holds the keys to be logged. Can be used to overwrite the defaults or add extra keys!

Example:

```python
getapiparams(es_create=False, debug=True, log={'browser': BROWSER.name, 'env_tester': platform.system()})
```

Returns:

```json
{
    "sla": {
        "pageLoadTime": 2000
    },
    "baseline": {
        "days": 7,
        "perc": 75,
        "padding": 1.2
    },
    "flags": {
        "assertBaseline": true,
        "debug": true,
        "esTrace": false,
        "esCreate": false,
        "passOnFailedAssert": false
    },
    "log": {
        "test_info": "Sample test_info",
        "env_tester": "Windows",
        "browser": "firefox",
        "env_target": "Sample target",
        "team": "SAMPLE TEAM"
    }
}
```

Notice that the `flags.debug`, `log.browser` and the `log.env_tester` keys were changed when compared to the defaults!

### `injectjs(inject_type, mark, strip_query_string)`

Get the "inject code" from the API

|param|type|required|default|description|
|-|-|-|-|-|
|inject_type|string|Yes|-|The type of measurement you are performing. Valid options are `navtiming` and `usertiming`|
|mark|No|string|`false`|The name of the visual complete mark|
|strip_query_string|No|boolean|`false`|Indicates whether you want to strip the querystring from the URL you are testing|

Example:

```python
injectjs( inject_type="navtiming", mark="visual_complete", strip_query_string=True )
```

Returns:

```json
{
    "status": 200,
    "inject_code": "var%20visualCompleteTime%20%3D%200%3B%0Aif%20(performance.getEntriesByName('visual_complete').length)%20%7B%0A%20%20visualCompleteTime%20%3D%20parseInt(performance.getEntriesByName('visual_complete')%5B0%5D.startTime)%3B%0A%20%20window.performance.clearMarks()%3B%0A%7D%3B%0Areturn%20%7Btime%3Anew%20Date().getTime()%2C%20timing%3Awindow.performance.timing%2C%20visualCompleteTime%3A%20visualCompleteTime%2C%20url%3A%20document.location.href.split(%22%3F%22)%5B0%5D%2C%20resources%3A%20window.performance.getEntriesByType('resource')%7D%3B"
}
```

### `navtiming(inject_js, api_params)`

Post navtiming performance data to the API

|param|type|required|default|description|
|-|-|-|-|-|
|inject_js|dict|Yes|-|Contains the full response that you received from the browser after injecting the `injectjs` code|
|api_params|dict|Yes|-|Contains the API params that you retrieved from the `getapiparams()` method|

### `usertiming(inject_js, api_params)`

Post usertiming performance data to the API

|param|type|required|default|description|
|-|-|-|-|-|
|inject_js|dict|Yes|-|Contains the full response that you received from the browser after injecting the `injectjs` code|
|api_params|dict|Yes|-|Contains the API params that you retrieved from the `getapiparams()` method|

### `apitiming(timing, url, api_params)`

Post apitiming performance data to the API

|param|type|required|default|description|
|-|-|-|-|-|
|timing|dict|Yes|-|Contains the start/stop timestamps that you set before and after running your API call. Example: `{"startTime": 1515443109031, "endTime": 1515443109046}` |
|url|string|Yes|-|The URL of the API you're testing|
|api_params|dict|Yes|-|Contains the API params that you retrieved from the `getapiparams()` method|

For more information about the API: [https://github.com/godaddy/timings](https://github.com/godaddy/timings/blob/master/README.md)
