# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python37_app]
from flask import Flask
import cambio_rates
from datetime import datetime, timedelta
from google.cloud import storage

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
storage_client = storage.Client()
bucket = storage_client.bucket('{bucket_details}')
#url = ''
@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    url = cambio_rates.get_sheet()

    return 'Welcome to Cambio Rates!<br/> <a href="'+url+'">'+str(datetime.date(datetime.now()))+' Rates Sheet</a>'

@app.route('/daily')
def get_daily_rates():
    print('Calling cambio_rates.get_daily_rates()')
    cambio_rates.get_daily_rates()
    print('Exiting cambio_rates.get_daily_rates() function')
    return 'Daily!'
    #return render_template('tweets.html', times=events)
    #return render_template('posts_data.html', posts=ig_posts)
    #return

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python37_app]
