# Logs Analysis Project

You've been hired onto a team working on a newspaper site. The user-facing newspaper site frontend itself, and the database behind it, are already built and running. You've been asked to build an internal reporting tool that will use information from the database to discover what kind of articles the site's readers like.

The database contains newspaper articles, as well as the web server log for the site. The log has a database row for each time a reader loaded a web page. Using that information, your code will answer questions about the site's user activity.

The program you write in this project will run from the command line. It won't take any input from the user. Instead, it will connect to that database, use SQL queries to analyze the log data, and print out the answers to some questions.

## Installation

This program uses DB views but it can create them by itself. If it's the first time you're running it, make sure to run it with the `--reloadviews` arg or create it manually with the query below. It shows a nice error message otherwise though. :)

```
    create or replace view requests_per_day as
        (select tl.datet as day, count(lo.id) as erroneous_requests, tl.c as total_requests
            from "public"."log" as lo
            join (select date_trunc('day', time) as datet, count(time) as
            c from "public".log group by datet) as tl
                on date_trunc('day', lo.time) = tl.datet
            where lo.status not like '2%'
            group by tl.datet, tl.c
            order by tl.datet);
```

## Usage

`$ python3 analytics.py [-h] [--reloadviews] [top3articles,topauthors,erroneousday,all]`

    Run the program with the desired report you want to see.

    - top3articles: What are the most popular three articles of all time?
    - topauthors: Who are the most popular article authors of all time?
    - erroneousday: On which days did more than 1% of requests lead to errors?
    - all: Run all of the reports. This is the default option.
        
    optional arguments:
      -h, --help            show this help message and exit
      --reloadviews         Create anew the views required for this program


