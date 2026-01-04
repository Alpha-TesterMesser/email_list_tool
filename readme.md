# Project Description:
### Thank you for taking interest in this project! A quick summary would be an email tool that can manage subscriptions, unsubscribes, verification, and confirmation email sending (containing the verification code).
#### A bit more of a technical note:
#### Flask backend SQL data handling with regular expression checking of emails, duplicate denial, and emails staying in memory but with a send attribute ("YES" or "NO"), concurrent CSV logic mimicing SQL state, hashing of verification codes, code timeout, and a GUI for a quick overview of the database.  

---  

# Setup Tutorial:

## Requirements:

1. A computer (maybe?)
2. An IDE capable of installing flask with a virtual environment (it's quite easy, look it up)
3. Electricity
4. A brain
###### (Alright, that's it)

## Setup:

#### First, we'll do the file structure within your project folder (shown here as python_website):
python_website\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--Templates\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--subscribe.html\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--unsubscribe.html\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--verify.html\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--Static\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--bg.jpg (import this yourself)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--style.css\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|--script.js (currently empty, maybe you'll find some use)\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--app.py\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--db.py\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--email_utils.py\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--emails.csv\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--emails.db\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--main.py\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--subscriptions.py\
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;      |--unsubscribe.py
##### After setting this up, copy all the code to their respective files, or just download them. Whatever works.

#### Next, there are a few things that need to be set up to work correctly:
### 1. Email credentials:
To actually set this up, create an app password for the account that you want to send emails from. *(another "look it up" moment, maybe I'll add the explanation here later)*

### 2. The environement variables
You may notice that the `email_utils.py` file pulls constants from the os. We'll set that up here:
Go to powershell and run these two commands:
> setx GMAIL_USER "your_email@gmail.com"

> setx GMAIL_APP_PASSWORD "abcd efgh ijkl mnop"
##### GMAIL_USER should be the email you set up the app password for,
##### GMAIL_APP_PASSWORD would be the App Password you generated earlier.

### Um... I think that should work. Run `python app.py` with Flask installed. 
1. It should set up the server
2. Navigate to the link, e.g. `127.0.0.1:5000/signup`
3. Enter your email address
4. Be redirected to /verify
5. Check your email
6. Enter the code
NOTE: Make sure to check your databse at each step in order to watch the magic happen!

### Thanks for reading and taking part in this. Any bugs I'll be happy to fix, just start an issue!
