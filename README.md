# CS50 Final Project

## About the website
This is a website that serves two functions:
1. **Affirmation provider**: Provides a certain number (chosen by the user) of affirmations in a chosen category. This function does not require log-in from the user. Getting the lists of requested affirmation requires choosing the number of affirmations that should be displayed as well as choosing a category from lists of dropdowns. Without these two data, there will be specific error messages. Upon choosing a value for the two fields, the user gets to a `/generate` page which enlists the affirmations as well as a *refresh* and a *done* button.  
The *refresh* button randomly loads more affirmations as requested while the *done* button returns the user back to the homepage.

2. **A journal**: In order to use this function, a login is rquired. This function allows the user to write journal inputs, view all journal inputs sorted by date and time from latest to oldest. Journal inputs can be deleted and favorited. Favorited journal inputs can be viewed on a separate page. Users can also search for keywords in their journals or numbers to search based on the date or time of input upload.

## How the website works
1. The affirmation provider works by retrieving data from a database of tables using SQL queries. Since this function does not require login details, a random number between 0 and 10000 is randomly generated and assigned on each visit to the webpage. The unique number and the inputs of the users are inserted into a table to be used in creating the list of affirmations. More SQL queries are used to retrieve the requested category. The affirmations are provided using a for loop restricted by the number of affirmations that the user requests. 

2. Access to the journal requires logging in with a pre-registered username and a password. Writing into journal requires submitting the journal through a form which is inserted into a *journal* table. Displaying the journal requires using a for loop to  display each row of the *journal* table. A javascript function called *journal_cleaning* is created to label each div that encloses a journal input has a unique id. So, the bottom-most div is given the id - *journal_li_1* while the one above it is *journal_li_2* and so on. This makes each div identifiable using *this.id* when marking a journal input  to be favorited or to be deleted.

### Marking an input as 'favorite'
Each journal input has a star by its side, so, in order to mark an input as a favorite, the star corresponding to the input has to be double clicked.
By double clicking this star, a javascript function is run that retrieves the innerHTML of the previousSibling, previousSibling node which is the div containing the journal input.
With this journal input saved as a variable, it is then set as the value of a form which is hidden using css `display: none` style format. This forrm helps connect the 
favorited journal input back to Flask where the information is inserted into a new table called *favorites*.
This table is used to save the favorites and SQL queries are used to retrieve data from to be displayed on a different webpage. On each attempt to access `/favorites`, two things are checked:
* The journal input must not already exist in *favorites*
* The journal input must exist in the *journal* table i.e it must not have been deleted

If the *favorites* webpage is opened when there are no favorites, a page is displayed that makes this clear and gives an instruction on how to mark favorites.

### Deleting an input as favorite
Each journal input has a trashcan underneath it, so, in order to delete a journal input, the trash can corresponding to the input has to be double clicked.
By clicking this trash can, a javascript function is ran that retrieves the innerHTML of the previousSibling, previousSibling, previousSibling node which is the div 
containing the journal input. With this journal input saved as a variable, it is then set as the value of a form which is hidden using css `display: none` style format. 
This form helps connect the to-be-deleted journal input back to Flask where a SQL query is made to delete the journal input from the *journal* table.

### Searching through the journals
The item or keyword to be searched is sent to Flask through a form, and is compared with the dates, times and content of each journal input using a LIKE operator. 

## Proposed Improvements
* Favoriting journal inputs. There should be a constant indicator of the favorited inouts on the general journal display page.
* Allow the composition of journal inputs that are duplicates of previously saved inputs.

## How to Use
Run this:
```
$ flask run
```
