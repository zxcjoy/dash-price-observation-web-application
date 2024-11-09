### Enhancements ###
  Author: Ziyu Chen
  Date: 10/9/2024
  Contact: zychen025@gmail.com

* Data Validation: 
1. Implemented constraint check for Price field.
- allow negative values and zero value for Price field;
- allow None value for delete Observation as this will allow deleting all records indicated by Date, Category, Item, State, City with no restriction on Price field;
- disallow None value and non-numeric values for add Observation; 
- disallow non-numeric values for delete Observation;
2. Added constraints on selecting Item and City: the dropdown menu will only show the items within the speciffied category. Similarly, this is applied on City dropdown menu.
3. No restriction on Date field: this may not be a best practice for a real-world application (should forbid future date), as the use cases for the app is not clearly stated, I decided to allow future date for now. This feature may help testers to add data points to any date and have a better visulization of the data. The restrictions can be easily added by comparing the input date to the current time.

* Data Formatting:
1. Convert date format to YYYY-MM-DD as I think recording the datetime is not necessary for the purpose of this project.
2. Change the way to indicate the unit in the item. For example, using USDA Grade-A eggs (Dozen) instead of USDA Grade-A eggs, Dozen. The updated format is more widely used in the US.
3. Convert price to 4 decimal places. 
- Explanation: though most of the American merchandize price has only two decimal accuracy, and the gas price usually has up to three deciaml accuracy, as far as I know, some financial products may have up to 4 decimal accuracy (e.g. price for foreign exchange). 
- More details should be considered given the specific use cases of this project. As for now, I decided to use 4 decimal places for a balance of system scalability and American business conventions.
- Implemented a function ``custom_rounding`` in cpi.py(utils.py) to round the prices (generated by ``get_test_data``) according to the type of Item.
4. Fix typos in the City names (Los Angelos -> Los Angeles).

* Improvements of the Interface:
- General consideration: This application seems like an internal test tool, or as a prototype for a business analtics tool. So, the interface does not need to be too fancy, i.e. not too many colors, various fonts. It needs to be simple and user-friendly. The interface should remain neat and intuitive to use. With this in mind, the following improvements are made:

- A neat and nice look of the app:
1. Use bootstrap to add styles of the app, redesign the framework of Dash layout
2. Utilized theme provided by dash-bootstrap-components to make the app having a better look
3. Setting minimum point size on the scatter plot: when enabling point size scaling on the ``Item Prices Over Time`` graph, the point size with 1 data point is too small to be seen. 

- User-friendly designs:
1. Enable intuitive color on the save and delete buttons, blue for a relatively safe action, red for a relatively dangerous action (delete from database)
2. Allow multi-column sorting for the table, making it easier to filter data to find a specific observation
3. Set a page size limit for the table, avoiding the page from being too long
4. Allow seperate scrolling for the table and the graph. Now users can roll down the right part of the app to the data table, and select the observation to be deleted.
5. Status notifications with intuitive color and labels for save/delete actions are enabled. 
- For delete action, it supports succesful messages displaying how many matching observations are deleted, or warning message displaying no matching observations are found, or a danger message if there is unexpected error. 
- For save action, it supports succesful messages to assure the user that the data is saved successfully, or danger message if Price is not valid, or danger message if there is unexpected I/O error when writing to the database.
6. A ``!`` sign is added to the Price input box to provide information on the required format for the input in a pop-up text.

* Refactoring the Project Code:
1. Added a ``requirements.txt`` file to specify the required packages of the project.
2. Use a configuration file ``config.py`` to store the constants like ``db_file``, and the app supported ranges stated in ``CATEGORY_ITEM_MAP``. We can easily add more supported items in the constants in the configuration file. By utilizing the configuration file, the app is easier for future development.
3. Use a utils file ``utils.py`` for helper functions like ``sqlize`` and ``custom_rounding``. These functions serve a general purpose and can be reused in other projects.
4. Enabling git version control for the project for better code management and tracking.

* Testing:
1. Implemented unit tests for ``Observation.delete_matching`` in test_cpi.py.
2. Multiple manual functionality tests are implemented on the web application.
3. Detect and fix several bugs as indicated in the NOTES section below.


* Further Improvements:
1. Add import/export features as needed: batch data import from csv files could be very helpful. In the same sense, the app may support exporting data to csv files.
2. Enableing logging for the app: logging is a good way to track the running status of the app. As time is limited, I only utilize print statements for debugging. 
3. Robust Testing: As limited by time and resources, the testing for this project is not comprehensive. For example, the layout may not work well on different screen sizes or resolutions.
4. More data visualization: given the data, more grpahs of different types can be added to the app.
5. Analytics and Machine Learning: Given the data, more analytics can be done on the data, e.g. using machine learning to build predictive models and displaying trends.
6. Improve Security and Authentication: as the app is designed to show data directly from the database, the security of data is not a concern. If a business purpose is cleared for this app, I would consider improve some methods used in this project which may have potential security issues.
- For example, using string interpolation to build SQL queries may have potential security issues like SQL injection.
7. Performance concern: The app is now designed for a relatively small amount of data. That is, each adding or deleting operation will result in calculating the average price or count. Pandas provides high efficieny for this kind of calculation on a relatively small dataset. However, if the data size is getting large, calculation and I/O operations are not optimized. Querying the database may also be slow, which requires us to consider indexing. In all, we may need to redesign some features to improve the performance to support a large amount of data.

### Notes ###
The following notes are used as a purpose to track the progress of the project by myself.
Tasks timeline breakdown: 
- 10/7: Overview of the project, screen for problems, understand the infrastructure, learn basic dash
- 10/8: Complete 4 basic tasks
- 10/9: Add improvements as instructed in the bonus tasks
List of tasks to do:
1. [DONE] Price should be rounded to 2 decimal places -> after consideration, using 4 decimal places
2. [DONE] City 'Los Angelos' seems a typo, may need check the database
3. [IGNORE] Same date with different price may need check if something is wrong ->  this is how the system designed for
4. [DONE] Plain html with no style, need css or more to make it look better 
5. [DONE] After selecting a category, items should be limited to only in that category
6. [DONE] Similarly, State shoule constraint the city selection
7. [DONE] Inconsistency of SQL notation, e.g. "WHERE" vs "where", most of the time it is "where", should adhere to lower case
8. [DONE] Task 1: Complete the ``Observation.delete_matching`` method in cpi.py
9. [DONE] Task 2: Integrate the delete_matching method into the app, allow user to delete observations
10. [DONE] Task 3: Solve the "Average Item Price by City" graph point scale problem
  -> point size is larger when  there are more observations with the same price
  -> point size is smaller when there are less observations with the same price
11. [DONE] Task 4: Implement the "Average Item Price by City" as grouped bar graph
12. [Done] Add Observation should forbid None price value while delete Observation should allow None price value, need to modify the app frame to correctly handle this
13. [DONE] Data table in app is not sorted, making it hard to find an observation, consider to add ranking by columns
14. [DONE] More restraints should be applied on the Price field, e.g. string should not be allowed
15. [DONE] Date column contain hour-minute-second, which is not necessary and not consistent with add and delete methods, should be removed
16. [DONE] Consider add a delete successful message: how many observations are deleted or no mathch
17. [DONE] Consider add an add successful message: e.g. 'The provided observation has been added'
18. [DONE] In scatter plot, the point size with only one data is very small to see, need to fix it
19. [DONE] As the `Average Item Price by City` graph supports different date, when changing date, the graph should be updated, the date is set as a State which does not trigger callback,  need to fix it
20. [DONE] Enable two separate scrolling areas so that we can target data on the right, and enter it on the left for deletion
21. [DONE] Modify the position of each web component, e.g. not always on the left which is not a nice interface
22. [DONE] Adding color to the interface, e.g. color of the button
23. [DONE] Add icons to enhance the application (as recommended by the bootstrap documentation!)
24. [DONE] BUG #1: When click 'x' to clear the selection of a state, error occurs as try to get a None value from a dict; similarly the category
25. [DONE] BUG #2: When the number of observations to delete is not set and you click 'Delete', error occurs.






