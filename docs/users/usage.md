# Usage
This section will guide you through to finish setting up Web Portal. It assumes you have gone through the install wizard and have the app running.

After finishing the install wizard you will either be met by the public dashboard or a login screen, this will depend on what you set the "Public Portal" setting to.

> This guide will not show any setup of plugins other than the "Core" plugin.


## Logging In
First you will need to login. To login click on the "Log In" button at the top navigation bar. Use the admin credentials you setup earlier.


## The Dashboard
After logging in you will be met with the dashboard, which will fill up with your widgets. At the movement this should be blank.


## Accessing User Settings
Now you are logged in you should navigate to the user settings page. Click on the cog icon in the top navigation bar.

Once loaded you should see the page welcoming you by your username.

From this page you can access the following:

- Dashboard Settings
- Administrations (if logged in as a admin)
- Plugin Settings

If you want to override the public dashboard for the current user click on the "Create Custom" button which will then allow the currently logged in user to create their own dashboard.

If you have a dashboard this button will be called "Editor" instead. You can reset back to the public dashboard by clicking "Restore To Defaults".

As we want to access the public account, which will allow us to set a global dashboard for any user click on the "Administration" button.


## Accessing Administration Settings
Once at the "Administration" page. We have the following options:

- Plugin Settings - Takes you to the same as the standard plugin settings button
- Switch To Public - Switch to the Web Portal virtual public account, this can also be accessed in the user management page under "Force Login".
- Users - Takes you into a manage users page; allowing for you to add new users, modify existing ones and force login to standard account users. It also display a table of all users currently registered with their corresponding management buttons.
- Import V1 Widgets - Import links from Web Portal V1 (only works when Core plugin is installed)

As we want to access the public account, we can click on "Switch To Public". This will now login to the virtual public account. From there we can go into settings and create our shared public dashboard.


## Dashboard Editor
Inside the dashboard editor we can add new widgets and manage our currently placed ones.

### Add Widget
Depending on what plugins you have installed you may have more options. However You can add a widget to the dashboard by selecting the widget type and giving it a name (this will show up in the widgets header if enabled).

### Manage Placed Widget
Once a widget has been placed, in the dashboard editor you will see the widgets and their corresponding management buttons (Edit, Delete).

Clicking on the "Edit" button will take you to the widgets edit page, depending on how the plugin is implemented it may look different to the Web Portal theme.

## Plugin - Core
The Core plugin which is built-in to Web Portal (unless you removed it). Provides several widgets which are listed below:

- Digital Clock - A digital clock which also displays the date
- Links - The links widget allows for placement of customisable links
- Web Search - Add your own search engine to search the internet
- Embed HTML - Embed some custom HTML code (also known as injection)
- Embed Website - Embed a website by providing its url, uses an iframe so may not work with all sites

### Administration Settings
This plugin also has a management page, which is accessed from the "Plugin Settings" page. It has the following sub pages:

- Search Engines - Allows admin to add search engines which can be selected from the search widget
- Links Management - Allows admin to add links which can be selected from the links widget
- Upload Icons - Allows admin to upload icons which can be used in the links widget for a app icon

This is the end of the usage tutorial for Web Portal, maybe checkout the upgrading and migrating guide next [here](upgrading.md)
