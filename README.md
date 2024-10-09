# Beneficient Risk Developer Coding Test #
This repo contains a coding test for potential risk developers.
We do not expect you to know [Dash](https://dash.plotly.com/) but expect you to be able to 
quickly learn whatever you need in order to finish the project through online resources yourself. 
Please feel free to add any comments in the code. After you are done, please zip the project folder and email the zip file 
to your recruiter who will send to us.

### How do I get set up? ###
1. Create a clean python environment with whatever environment manager you prefer (virtualenv, conda, etc.)
2. Activate environment created in step 1 
3. Execute ``pip install dash pandas`` to install dash and pandas
4. Launch app by running ``python app.py``

### Tasks for Candidate to Perform ###
The following tasks should be completed by the candidate in their preferred order:

* Complete the ``Observation.delete_matching`` method in cpi.py which contains detailed instructions.
* When the "Delete Matching Observations" button is clicked, the ``Observation.delete_matching`` method is called and the database table, front-end table, and front-end graph are updated accordingly.
* When the "Graph Type" drop-down is set to "Item Price Over Time", multiple observations for the 
  same item that have the same price causes the point size to scale proportionately to the number of matching observations
* Implement the "Average Item Price by City" graph type so that when it is selected, it changes the graph to a grouped bar graph where the height of a bar is the average price of an item in a city for the date in the "Date" field. The bars should be grouped together by item type and the color of each bar should correspond to the city that the average item price applies to. [Example of a grouped bar graph](https://chartio.com/assets/24e451/tutorials/charts/grouped-bar-charts/c1fde6017511bbef7ba9bb245a113c07f8ff32173a7c0d742a4e1eac1930a3c5/grouped-bar-example-1.png)

### Bonus Tasks ###
* Please feel free to add any enhancements to the code that will make it production-level quality including:
  - Improving the layout, look, and feel of the app
  - Add data validations which make sense for the business logic
  - Improve the data formatting for cleanliness and to be inline with American business conventions
  - You are encouraged to refactor existing code if doing so will improve readability, extendability, performance, etc.
  - Add tests to verify the behavior and impact of code changes
* Any enhancements that you have added should be documented in the README.md section below called ``Enhancements``

### Grading Criteria ###
* Completion of the tasks specified and the bonus tasks
* Maintainability and readability of code written
* Thoughtful comments and descriptive variable names
* Code execution performance (there should be no noticeable delay to the user when changing graphs or deleting points)

### Who do I talk to? ###
* recruiting@beneficient.com

### Enhancements ###
Author: Ziyu Chen
Please list any enhancements made here

### Screen Notes ###
1. [] Price should be rounded to 2 decimal places
2. [DONE] City 'Los Angelos' seems a typo, may need check the database
3. [] Same date with different price (for eggs) may need check if something is wrong
4. [] Plain html with no style, need css or more to make it look better
5. [] After selecting a category, items should be limited to only in that category
6. [] Similarly, State shoule constraint the city selection
7. [DONE] Inconsistency of SQL notation, e.g. "WHERE" vs "where", most of the time it is "where", should adhere to lower case
8. [DONE] Task 1: Complete the ``Observation.delete_matching`` method in cpi.py
9. [DONE] Task 2: Integrate the delete_matching method into the app, allow user to delete observations
10. [DONE] Task 3: Solve the "Average Item Price by City" graph point scale problem
  -> point size is larger when  there are more observations with the same price
  -> point size is smaller when there are less observations with the same price
11. [] Task 4: Implement the "Average Item Price by City" as grouped bar graph
12. [Done] Add Observation should forbid None price value while delete Observation should allow None price value, need to modify the app frame to correctly handle this
13. [] Data table in app is not sorted, making it hard to find an observation, consider to add ranking by columns
14. [DONE] More restraints should be applied on the Price field, e.g. string should not be allowed
15. [DONE] Date column contain hour-minute-second, which is not necessary and not consistent with add and delete methods, should be removed
16. [] Consider add a delete successful message: how many observations are deleted or no mathch
17. [] Consider add an add successful message: e.g. 'The provided observation has been added'
18. [] In scatter plot, the point size with only one data is very small to see, need to fix it

### Overall Application Description ###
- Support 2 graph types: 1. Item Price Over Time 2. Average Item Price by City
- Support manually enter an observation
- Support manually delete an observation

