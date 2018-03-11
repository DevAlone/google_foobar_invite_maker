# google_foobar_invite_maker

Want to participate in Google's foobar challenge but don't have
an invite? You're in the right place! This program provides about 20
invites per minute without proxies(can be more, but risky to
get captcha)

## How to run?

* Clone this repository

`git clone https://github.com/DevAlone/google_foobar_invite_maker.git`

* go to repo directory

`cd google_foobar_invite_maker`

* create virtual environment

`python3 -m venv env`

* go to it

`source env/bin/activate`

* install dependencies

`pip3 install -r requirements.txt`

* run

`python3 main.py >> invites`

* Enjoy!

Errors are shown on the screen, you can redirect them like this:

``python3 main.py 2> errors >> invites``

Also this program can work with proxies, just specify it:

`python3 main.py --use-proxies true >> invites`
