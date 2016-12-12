import matplotlib.pyplot as pl
import json
import requests
import base64
import time
import operator
import os
from sopel.module import commands, example, rule

# Data is from https://www.ssa.gov/oact/babynames/limits.html

image_folder = "images/"
male_dict, female_dict = {}, {}
names_dir = os.path.join(os.path.dirname(__file__), 'names')

# Create dictionaries with recorded birth totals for each gender in each year

with open(os.path.join(names_dir, "totalbirths.txt")) as births:
    for line in births:
        line = line.split()
        male_dict[line[0]] = line[1].replace(',', '')
        female_dict[line[0]] = line[2].replace(',', '')


@commands("names")
@example(".names Thomas M")
def name_search(bot, trigger):
    """Return lists of years in range and the counts of the name and gender for each year."""
    raw = trigger.group(2).split() if trigger.group(2) else ()
    # Determine if input fits parameters
    if len(raw) not in (2, 3):
        bot.say("Usage: .names Thomas M or .names Thomas M 1985")
        return
    # Length is plausible, let's load some variables
    elif len(raw) == 2:
        name, gender = raw
        year = None
    else:
        name, gender, year = raw

    # Format and verify name
    name = name.capitalize()
    if len(name) == 1:
        bot.say("Please provide a valid name.")
        return
    # Format and verify gender
    gender = gender.upper()
    if gender not in ('M', 'F'):
        bot.say("Invalid gender: please use either M or F.")
        return
    # Format and verify year
    if year:
        try:
            year = int(year)
        except ValueError:
            bot.say("Please supply a valid year.")
            return
        if year == 2525:
            bot.say("Is man still alive?")
            return
        if 1880 > year > 2015:
            bot.say("Please provide a year between 1880 and 2015.")
            return

    # Create list of all valid years, as strings
    years = [str(x) for x in range(1880, 2015)]

    # If they provided a specific year, just give the number and quit
    if year:
        bot.say(name_year(name, gender, year))
        return

    name_counts = []
    # Create list of file names for each year of name data
    name_files = os.listdir(path=names_dir)
    name_files.remove("totalbirths.txt")
    name_files.sort()
    # Search for the provided name and gender in each file, add count to list
    for year_file in name_files:
        with open(os.path.join(names_dir, year_file)) as f:
            for line in f:
                if name + "," + gender in line:
                    line_list = line.split(",")
                    name_counts.append(int(line_list[2]))
                    break
            else:
                name_counts.append(0)
    # If all years have counts of 0, return a message. Otherwise, plot the data.
    if all([n == 0 for n in name_counts]):
        bot.say("No babies with that name.")
    else:
        return plotter(bot, years, name_counts, name, gender)


def plotter(bot, years, name_counts, name, gender):
    """Plot the data in a graph."""
    # Clear any possible existing plot
    pl.clf()
    # Calculate percent of gender births that the name makes up for each year
    if gender == 'M':
        name_percents = [(y/float(male_dict.get(x))*100) for x, y in zip(years, name_counts)]
    else:
        name_percents = [(y/float(female_dict.get(x))*100) for x, y in zip(years, name_counts)]
    # Set graph details
    pl.plot(years, name_percents)
    pl.title("Popularity of the Baby Name %s (%s) Over Time" % (name, gender))
    pl.ylim(ymin=0)
    pl.xlim(xmin=1880, xmax=2014)
    pl.xlabel("Year")
    pl.ylabel("Percent of Babies")
    # Find the year with the highest count of the given name, and the count
    max_index, max_value = max(enumerate(name_counts), key=operator.itemgetter(1))
    # Find the year with the highest percentage of the given name, and the percentage
    max_pindex, max_pvalue = max(enumerate(name_percents), key=operator.itemgetter(1))
    # Label the year with the highest count of the given name
    # Note: This is slightly bugged in that the label gets cut off when near the edge of the graph.
    pl.annotate(s="%s in year %s" % (max_value, years[max_pindex]), xy=(years[max_pindex], max_pvalue), size='small')
    # Name and save the graph created by savefig
    location = image_folder + name + gender + time.strftime("-%Y-%m-%d-%H-%M-%S") + ".png"
    pl.savefig(location)
    # Clear the plot
    pl.clf()
    # Upload the graph image to imgur
    return upload(bot, location)


def upload(bot, file_location):
    """Use the imgur API to upload the graph image."""
    # Return error if no imgur API key in the bot config file.
    if not hasattr(bot.config.apikeys, 'imgur'):
        return bot.say("Please supply an API key for imgur.")
    # Get API key from bot config file
    client_id = bot.config.apikeys.imgur
    # Do the uploading
    with open(file_location, "rb") as image:
        b64image = base64.b64encode(image.read())
        headers = {'Authorization': 'Client-ID ' + client_id}
        data = {'image': b64image}
        r = requests.post(url="https://api.imgur.com/3/upload.json", data=data, headers=headers)
        lol = json.loads(r.text)  # get the json...
        bot.say(lol['data']['link'])  # print the link


def name_year(name, gender, year):
    """Return name data for a specific year."""
    if gender == "M":
        gender_long = "male"
    else:
        gender_long = "female"
    # Search the file for the given year for the count of name+gender combo, and return it
    with open(os.path.join(names_dir, "yob" + str(year) + ".txt")) as names_for_year:
        for line in names_for_year:
            if name + "," + gender in line:
                line_list = line.split(",")
                return "There were {} {} babies named {} born in {}.".format(line_list[2], gender_long, name, year)
        # Searched the whole file, didn't find the name
        return "There were fewer than 5 {} babies, if any, named {} born in {}.".format(gender_long, name, year)
