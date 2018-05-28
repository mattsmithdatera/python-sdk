API loading process
===================

1. Config structure
    ```json
    {
        "mgmt_ip": "X.X.X.X",
        "username": "some_username",
        "password": "some_password",
        "tenant": "some_tenant",
        "api_version": 2.2
    }
    ```

2. User executes script
    A. User provides credentials via CLI
    B. User provides credentials via config file (.datera-config/datera-config)
        a. local directory
        b. $HOME folder
        c. $HOME/.config/datera folder
        d. /etc/datera folder
    C. User provides credentials via /etc/cinder/cinder.conf

    ```
    # This means load priority is
    # 1. CLI opts
    # 2. local folder config file
    # 3. $HOME folder config file
    # 4. $HOME/.config/datera folder config file
    # 5. /etc/datera config file
    # 6. /etc/cinder/cinder.conf
    ```

3. Config is loaded
4. API object is created from config
