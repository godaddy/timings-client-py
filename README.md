# timings-client-py

Python client for the `timings` API - [https://github.com/godaddy/timings](https://github.com/godaddy/timings)  

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

After installation you first need to copy the configuration file and change it to your needs. The client includes a sample config file that can be found here: `https://github.com/godaddy/timings-client-py/blob/master/timingsclient/default.yaml`. You will pass the location of this config file when you initiate the client (see example below).

These settings will become the **default** parameters for your tests! You can overwrite parameters for individual tests by using the `getapiparams` method (see example below).

```yaml
PERF_API_URL: "http://{your API host}/v2/api/cicd/"
api_params: 
 sla: 
  pageLoadTime: 2000
 baseline: 
  days: 7
  perc: 75
  padding: 1.2
 flags: 
  assertBaseline: true
  debug: false
  esTrace: false
  esCreate: true
  passOnFailedAssert: false
 log: 
  test_info: "Sample test_info"
  env_tester: "Sample tester"
  browser: "Sample browser"
  env_target: "Sample target"
  team: "SAMPLE TEAM"
```

You can find a list of all the 'common' parameters here: https://github.com/godaddy/timings#common-parameters-navtiming-usertiming-and-apitiming

## Usage

To use the client, import the client like this:

```python
from timingsclient import Perf
```

Now you can initiate the client, along with the location of your config file, as follows:

```python
# Setup custom config
CONFIG_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)),'', 'custom.yaml')
PERF = Perf(CONFIG_FILE)
```

With the client initiated, you can start adding perf calls to your tests!

### Calling the `injectjs` endpoint

It is recommended that you do this **only once** at the top of your test and store the response in a variable:

```python
INJECT_CODE = PERF.injectjs('navtiming', 'visual_complete')
```

### Injecting JavaScript into your webdriver

The `INJECT_CODE` variable holds the JavaScript that you inject into your webdriver object to collect performance data. Usually the following command will do the trick:

```python
BROWSER.execute_script(INJECT_CODE)
```

### Setting parameters for the API endpoints

All of the performance methods require parameters to be included in the POST body. You can set the parameters before every test step or, like the injectjs call, do it once at the top of your test (if the parameters are always the same). The following line of code will do the trick:

```python
API_PARAMS = PERF.getapiparams(days=15, debug=True, es_create=False, log={'something': 'extra'})
```

Notice that the above example is using "named arguments". The following named arguments are valid:

|argument|type|example|default|description|
|-|-|-|-|-|
|sla|dict|`{'pageLoadTime': 3000}`|`{'pageLoadTime':2000}`|The metric to assert on along with the (static) threshold value|
|debug|boolean|`True`|`False`|Turn on/off extra debug data in the API's response|
|es_trace|boolean|`True`|`False`|Turn on/off extra ElasticSearch trace info in the API's response|
|es_create|boolean|`False`|`True`|Store data in ElasticSearch or not|
|days|int|`14`|`7`|The number of days to be used to collect the baseline|
|perc|int|`80`|`75`|The percentile value to be used for the baseline|
|padding|int|`1.4`|`1.2`|The amount of 'padding' to be used for the assert threshold (1.2 = add 20%)|
|search_url|string|`'*mydomain*subpage*'`|`''`|Wildcard that will be used to filter the baseline by URL|
|log|dict|`{'something': 'extra'}`|none|You can use this to submit extra 'meta data' to the API. This will be stored in Elasticsearch and can be used to slide & dice the data in Kibana!|

## Example test script

Here is an example of a complete test 'navtiming' script:

```python
"""
Selenium Grid with Hub and Node test
"""
import os
import platform
from selenium import webdriver
from timingsclient import Perf

BROWSER = webdriver.Firefox(
    executable_path=r'~/selenium/geckodriver')
BROWSER.get('http://www.seleniumconf.de')

try:
    BROWSER.find_element_by_class_name('section__heading')
    print("FUNCTIONAL: Page looks good!")
except:
    print("FUNCTIONAL: Page not working!")

# Setup custom config for PERF
CONFIG_FILE = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '', 'custom.yaml')
PERF = Perf(CONFIG_FILE)
INJECT_CODE = PERF.injectjs('navtiming')
API_PARAMS = PERF.getapiparams(es_create=True, log={
    'browser': BROWSER.name, 'env_tester': platform.system()})

if INJECT_CODE is not False:
    TIMING = BROWSER.execute_script(INJECT_CODE)
    NAV_RESP = PERF.navtiming(TIMING, API_PARAMS)

    if NAV_RESP is not False:
        print(
            'PERFORMANCE was',
            ('GOOD' if NAV_RESP['assert'] is True else "BAD") + '! - ',
            str(NAV_RESP['export']['perf']['measured']),
            '/ ' + str(NAV_RESP['export']['perf']['threshold'])
        )

BROWSER.close()

```

For more information about the API: [https://github.com/godaddy/perf-api](https://github.com/godaddy/perf-api/blob/master/README.md)
