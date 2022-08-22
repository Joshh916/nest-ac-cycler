This is a Nest Thermostat API control integration application written in python. The main method runs a loop which cycles the AC system waiting at certain intervals so as to give the system a break when it is running constantly. There is a manual mode which can enable heat, cool, or turn off the system. More features can easily be added through the API calls. 

This application runs as a script on linux and requires python and python-dotenv installed to run.

A .env file is required to run the program and contains the following variables:

PROJECT_ID
OAUTH2_CLIENT_ID
OAUTH2_CLIENT_SECRET
OAUTH2_REFRESH_TOKEN

The project id correlates to a project in the google device access console. https://console.nest.google.com/device-access

Why am I not including this? 

I haven't published this app so I would need to add any new users as test users and would need access to your nest as an authorized user.

The Oauth2 variables need to be retrieved from your account which has access to your nest. Instructions for setting that up can be found here. 

Once the .env file is configure the application can be run with ./ac-cycler.py, there is a --help command for using manual mode.

I plan on adding features to make this more fully functional over time and may eventually publish the app in a way in which it does not require you to setup your own project to use.