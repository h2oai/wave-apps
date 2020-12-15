# Guess The Number

If you followed the instructions in the `README` to run the app but noticed that the Player name is always `Default-User` and there is no option to login, the following instructions will fix that.

### Setup Authentication using Keycloak

Before we begin,

> Please DO NOT use these instructions for a production environment. These are strictly for the purpose of development on a local machine ONLY.

- Make sure Docker is installed and is running.

#### Table Of Contents
- [1. Run Keycloak Container](#1-run-keycloak-container)
- [2. Login to Keycloak](#2-login-to-keycloak)
- [3. Create a new Client](#3-create-a-new-client)
- [3. Save Client Secret](#3-save-client-secret)
- [4. Create New User](#4-create-new-user)
- [5. Logout of Admin on Keycloak](#5-logout-of-admin-on-keycloak)
- [6. Start `waved` with authentication](#6-start-waved-with-authentication)
- [7. Start the App](#7-start-the-app)
- [8. Login to Wave app](#8-login-to-wave-app)

#### 1. Run Keycloak Container

```console
$ docker run \
-p 8080:8080 \
-e KEYCLOAK_USER=admin \
-e KEYCLOAK_PASSWORD=admin \
quay.io/keycloak/keycloak:11.0.3
```

[Top](#table-of-contents)

#### 2. Login to Keycloak

- Goto `http://localhost:8080` to connect to keycloak

![keycloak-home]

[Top](#table-of-contents)

- Click on `Administration Console` and login as User: `admin` with Password: `admin`

![keycloak-admin-login]

[Top](#table-of-contents)

#### 3. Create a new Client

- Click on `Clients` in the left menu

![keycloak-admin-console]

[Top](#table-of-contents)

- Click `Create` button in the top right corner to create new client

![keycloak-clients]

[Top](#table-of-contents)

- Enter a **Client ID**, for example: `wave`
- Select **Client Protocol** to be `openid-connect`
- Press `Save`

![keycloak-new-client-save]

[Top](#table-of-contents)

- Right after the page is saved, new settings appear on the same page
- Set **Access Type** as `confidential`
- Set **Valid Redirect URIs** as `*`
- Press `Save`

![keycloak-client-access-type]

[Top](#table-of-contents)

#### 3. Save Client Secret

- Goto the `Credentials` tab for the newly created client
- Save the **Secret** code to use later when starting the Wave Server.
- The code shown in this example is `76344ea2-f64d-43a1-b150-725e385b2fee`

![keycloak-credentials]

[Top](#table-of-contents)

#### 4. Create New User

- Click on `Users` in the left menu under `Manage`
- Click on `Add User` in the top right corner to add a new user

![keycloak-add-user]

[Top](#table-of-contents)

- Enter an email, for example `john.smith@aol.com` as **Username**
- Press `Save`

![keycloak-save-new-user]

[Top](#table-of-contents)

- After saving, goto the `Credentials` tab for the newly created user
- Enter a new password for the user
- Set **Temporary** field to `OFF`
- Press `Set Password`
- Create as many users as needed in this way

![keycloak-new-user-set-password]

[Top](#table-of-contents)

- To see all the users, click on `Users` under `Manage` in the left menu
- Click on `View all users` button

![keycloak-view-all-users]

[Top](#table-of-contents)

#### 5. Logout of Admin on Keycloak

- After all required users are created, logout as `admin` and close the browser window so that we can login as one of the newly created users while using the Wave app.

![keycloak-admin-logout]

[Top](#table-of-contents)

#### 6. Start `waved` with authentication

- Find the previously saved `Client Secret` in Step 3
- In the next command, replace the value of `oidc-client-secret` with your `Client Secret`
- Use the following command to start the Wave Server

```console
 ./waved -oidc-client-id wave \
  -oidc-client-secret 76344ea2-f64d-43a1-b150-725e385b2fee \
  -oidc-end-session-url http://localhost:8080/auth/realms/master/protocol/openid-connect/logout \
  -oidc-provider-url http://localhost:8080/auth/realms/master \
  -oidc-redirect-url http://localhost:10101/_auth/callback
```

[Top](#table-of-contents)

#### 7. Start the App

- Assuming that the python environment for the wave app is already setup, and make sure you are in the right directory and start the app using

```console
$ wave run guess_the_number/guess.py
```

[Top](#table-of-contents)

#### 8. Login to Wave app

- In a new `incognito` browser window, goto `http://localhost:10101` to launch the app
- The app will require you to login now

![wave-app-login]

[Top](#table-of-contents)

- Login as one of the newly created users. Logging in as `jane.smith@aol.com` in this example.

![wave-app-user-login]

[Top](#table-of-contents)

- Once logged in, we can see the Player's name displayed on top.

![jane-smith-logged-in]

[Top](#table-of-contents)

- Use a different browser, for example `chrome/firefox` to login simultaneously as a different user
- Play a few games while logged in as each player

![john-smith-all-games]

[Top](#table-of-contents)

- Private games include games that are abandoned by selecting `Quit` and games that are not selected to be shared publicly

![john-smith-private-games]

[Top](#table-of-contents)

[keycloak-home]: ./static/keycloak_home.png
[keycloak-admin-login]: ./static/keycloak_admin_login.png
[keycloak-admin-console]: ./static/keycloak_admin_console.png
[keycloak-clients]: ./static/keycloak_clients.png
[keycloak-new-client-save]: ./static/keycloak_new_client_save.png
[keycloak-new-client-save]: ./static/keycloak_new_client_save.png
[keycloak-client-access-type]: ./static/keycloak_client_access_type.png
[keycloak-credentials]: ./static/keycloak_credentials.png
[keycloak-add-user]: ./static/keycloak_add_user.png
[keycloak-save-new-user]: ./static/keycloak_save_new_user.png
[keycloak-new-user-set-password]: ./static/keycloak_new_user_set_password.png
[keycloak-view-all-users]: ./static/keycloak_view_all_users.png
[keycloak-admin-logout]: ./static/keycloak_admin_logout.png
[wave-app-login]: ./static/wave_app_login.png
[wave-app-user-login]: ./static/wave_app_user_login.png
[jane-smith-logged-in]: ./static/jane_smith_logged_in.png
[john-smith-all-games]: ./static/john_smith_all_games.png
[john-smith-private-games]: ./static/john_smith_private_games.png