# timings-client-py

Python client for the `timings` API - [https://github.com/godaddy/timings](https://github.com/godaddy/timings)

## Installation

Installation of the client can be done with `pip` or `easy_install`:

```python
pip install timingsclient
```

## Configuration

After installation you first need to copy the configuration file and change it to your needs. The client includes a sample config file that can be found here: `https://github.com/godaddy/timings-client-py/blob/master/timingsclient/default.yaml`. You will pass the location of this config file when you initiate the client (see below)

Important keys to update are:

|key|value|description|
|-|-|-|
|PERF_API_URL|`http://perfapi.mydomain.com/v2/api/cicd`|The full URL to the API|
|log.test_info|`my test`|Description of the test step|
|log.env_tester|`local`|The test machine's environment|
|log.browser|`Chrome`|The test browser|
|log.env_target|`prod`|The test target environment|
|log.team|`MY_TEAM`|The product team performing the test. This can be handy to separate results in the Kibana dashboards|

## Usage

To use the client, import the client like this:

```python
from timingsclient import perf
from timingsclient.perf import Perf
```

Now you can initiate the client, along with the location of your config file, as follows:

```python
# Setup custom config
config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), '', 'my_config.yaml')
PC = Perf(perf.get_config(config_file))
```

With the client initiated, you can start adding perf calls to your tests!

### Calling the `injectjs` endpoint

It is recommended that you do this **only once** at the top of your test and store the response in a variable:

```python
INJECT_CODE = PC.injectjs('navtiming', 'visual_complete')
```

### Injecting JavaScript into your webdriver

The `INJECT_CODE` variable holds the JavaScript that you inject into your webdriver object to collect performance data. Usually the following command will do the trick:

```python
BROWSER.execute_script(INJECT_CODE)
```

### Setting parameters for the performance endpoints

All of the performance methods require parameters to be included in the POST body. You can set the parameters before every test step or, like the injectjs call, do it once at the top of your test (if the parameters are always the same). The following line of code will do the trick:

```python
API_PARAMS = PC.getapiparams(days=15, debug=True, es_create=False, log={'something': 'extra'})
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
from selenium import webdriver

from timingsclient import Perf

PERF = Perf()
INJECT_CODE = PERF.injectjs('navtiming')

CHROMEDRIVER = "/Users/mverkerk/selenium/chromedriver.exe"

BROWSER = webdriver.Chrome(CHROMEDRIVER)
BROWSER.implicitly_wait(10)
BROWSER.get('http://seleniumhq.org/')

try:
    BROWSER.find_element_by_id("mainContent")
except:
    print("FAIL! - Functional error!")

TIMING = BROWSER.execute_script(INJECT_CODE)
NAV_RESP = PERF.navtiming(TIMING, PERF.getapiparams())
print('PERF was below threshold: ' + str(NAV_RESP['assert']) + ' ',
      str(NAV_RESP['export']['perf']['measured']),
      '/' + str(NAV_RESP['export']['perf']['threshold']))
BROWSER.quit()

```