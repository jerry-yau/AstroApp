# AstroApp
#### Video Demo: https://youtu.be/R2k-cY4xH40
#### Description:
##### Introduction

AstroApp aims to make life easier for both ameteur and seasoned people looking to stargaze. The application allows the user to access sky condition information, calculate target altitude and make note of their targets.

AstroApp is a web application built on Python Flask with the help of Bootstrap v5.3, sqlite3 and others. This application contains 9 html pages alongside 2 Python files, 1 database file, 1 JavaScript file and other accompanying files, all of which will be explained in due time.

##### Unmentioned files
main.js, site.css are stored in static folder. data.sql contains SQL statements for the creation of tables. notes.txt contains rough notes, including the NASA and OpenWeather API keys for this project.

##### app.py (+ more.py)

app.py contains the backend functions of this application. The app is initialised and checks for API keys and database. The location is also initialised to default. The details will be explained in their respective sections. more.py contains additional functions which are mainly API calls used in the home page (index.html). It also defines the 'login required' decorator.

##### data.db

The SQLite3 database contains 3 tables: contact, accounts and bookmarks. The contact table is responsible for the contact form in contact.html. The accounts table handles the accounts in the application. The bookmarks table handles the information in logbook.html.

##### layout.html (+ main.js)

This is the template used across this application, which encompasses almost everything but the content of the webpage. Bootstrap, CSS and JavaScript are linked here. The title of the webpage is responsive to the user's current page. In the static folder, it contains the shooting star favicon which was selected on [favicon.io](favicon.io/emoji-favicons/shooting-star/).

The main component in this HTML file is the navigation bar based on Bootstrap. This bar will turn into a collapsible list in a mobile resolution. On the left, there is a clickable icon which directs to the home page (index.html) and serves as the website's icon. The bar links to the files of index.html, calculate.html, logbook.html and contact.html. If there is a login, the account (account.html) and logout links will be displayed. Otherwise, the login.html page will be there to direct user to login or register for an account.

There is also a theme button that toggles the light or dark theme, which is a new addition to Bootstrap v5.3 using the 'data-bs-theme' parameter on the html tag. The JavaScript file (main.js) only serves to make the theme switch function as intended with the use of a 'dark' item. On dark mode, the 'dark' item is created on local storage and removed on light mode. On the load of each page, the JavaScript checks the item and sets the theme. (Without this, it will default to light mode as written on html tag when switching/reloading page.) Since it is very difficult to incoorporate custom designs for both modes, it is decided that CSS will not be used. Dark mode is an extremely useful feature given the purpose of this application.

##### index.html

This is the home page of the web application. There are four headings: Weather, Moon Phase, Sidereal time and Key Times Today. By default, the location is set to London when not logged in. London's coordinates are then used to update these four sections with API calls. Weather section used OpenWeather's API for a round-the-world coverage. Moon phase, sidereal time and the moon data in Key Times Today used the Astronomical Applications API from the U.S. Naval Observatory. Finally, twilight information is provided by sunrise-sunset.org's API. The results from the calls are processed within app.py and more.py, which relays these information to the web page. There is also a carousel near the bottom which displays the latest space weather events by NASA DONKI through NASA's API service.

There is an input for location, which searches the user input through OpenWeather's API to turn into coordinates. The country selection is optional but results may not be as accurate. Upon searching, the page will refresh and new API calls will be made using this new set of coordinates. The coordinates used is displayed within the weather section, along with the update time in Universal Time.

##### account.html

This page is unvisible in the navigation bar to users that are not logged in. For logged-in users, you are allowed to change all your details which all require your current password to submit successfully. For changing password, a new password confirmation is required.

Having thought of using local storage to save the user's location input for future use, I came to the conclusion that saving location as part of the account is the best for simplicity and reliability.

##### calculate.html

This page allows the user to perform a calculation on the altitude of a celestial target. There are four boxes in a single row which are all required. Inputs of up to 4 decimal places are allowed. An explanation section is below to describe the calculation that will be conducted, and a link to an academic source. In app.py, the calculation will start once the form is submitted.

Upon submission, the user will be directed to calculated.html with the results from this calculation. There are more brief notes at the bottom of calculated.html.

##### contact.html

This page is a form to contact the owner of the website. If you are currently logged in, the username entry is automatically filled and disabled for changes. If you are not logged in, the username entry is not required but available to be filled. The form requires the usual text entries as well as a message purpose and two check boxes. The first box must be checked in order to submit the form. This data will then be inserted into the database's contact table. After submitting, the user will be directed to contact_submitted.html with a message of confirmation.

##### logbook.html

Without login, this page will display a message that shows its unavailability and links to the login.html page.

If logged in, you will be greeted with 4 input boxes in a row where your targets can be saved. For RA and Dec, inputs of up to 4 decimal places are allowed. Items are saved in the bookmarks table in the data.db database. Once you have at least 1 item saved, a drop-down list and a table will appear under the save button. The drop-down list allows you to delete one of your saved items at a time. The table shows the entries belonging to the user.

##### login.html

This page is inaccessible to logged-in users, and allows the user to log in and register to the website, on the left and right respectively. I intended to use password hashing instead of saving original passwords on the database, but in this version I refrained from sending these data to third-parties. If log in is unsuccessful, it will be redirected to the home page but the navigation bar will still display the login link, meaning user is not yet logged in.

To register, all entries are required, including the city. Once registered and logged in, the city will be used on the home page to provide relevant information for convenience.

##### Logging out

Logging out will reset locations set by the logged in user. When back at home page, it can be noticed that the location is London (and not the account's custom location).

##### Conclusion

Thank you for reading and using AstroApp. Feedback is of course welcomed. The app will hopefully continue to develop.