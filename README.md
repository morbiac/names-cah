## Synopsis

"names" is a module for the [Sopel IRC bot](https://sopel.chat/) that allows users in the chat to obtain mildly interesting information on the popularity of a given baby name in the US. Track the trend of your name, your friends' names, or bizarre names.

The data is taken from the [United States Social Security website](https://www.ssa.gov/oact/babynames/limits.html)

## Installation

If you are already using the [Sopel IRC bot](https://sopel.chat/), installation is simple: put the names.py file in the modules directory. Next, [register an application on imgur](https://api.imgur.com/oauth2/addclient) in order for the module to create and upload graphs. The api key you get should be added to your sopel config file as follows:

`[apikeys]
imgur = codegoeshere`


## Command format

`.names NAME GENDER` (example: `.names Michael M`): This is the main command, and will create and upload a graph showing the relative popularity of this name from the year 1880 to 2015.

Example output: http://i.imgur.com/eY25cAW.png

`.names NAME GENDER YEAR` (example: `.names Michael M 1976`): This command will not provide a graph, but simply data on the given name and gender combination for a specific year. If no data is found, that means there were fewer than 5 babies matching the input, and thus weren't included in the source data.
 
Example output: "There were 66966 male babies named Michael born in 1976."