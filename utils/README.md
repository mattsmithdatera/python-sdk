Utility Usage
=============

Create a virtualenv
```
$ virtualenv .sdk-utils
```

Activate virtualenv
```
$ source .sdk-utils/bin/activate
```

Install requirements
```
$ pip install -r utils-requirements.txt
```

Utilities in this folder are now usable.  Most assume you have a valid
cinder.conf file on this node with a correctly configured [datera] section
