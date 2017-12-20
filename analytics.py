#!/usr/bin/python3

import psycopg2
import argparse

DBNAME = 'news'


def top3articles():
    """Print a list with the name and amount of views for the top 3 articles"""
    db = psycopg2.connect(database=DBNAME, user='postgres')
    c = db.cursor()
    c.execute('''
        select art.title, count(lo.path) as views
        from "public".articles as art join "public"."log" as lo
            on lo.path like '%' || art.slug
        group by  art.title
        order by views desc
        limit 3;
    ''')
    items = c.fetchall()

    print('\033[94mWhat are the most popular three articles of all '
          'time?\033[0m')
    for item in items:
        print(' - "' + item[0] + '" - ' + str(item[1]) + ' views.')
    db.close()
    return items


def topauthors():
    """Print a list with the name of the most popular authors and amount of
    views for their articles"""
    db = psycopg2.connect(database=DBNAME, user='postgres')
    c = db.cursor()
    c.execute('''
        select auth.name, count(lo.path) as views
        from "public".articles as art
            join "public"."log" as lo
        on lo.path like '%' || art.slug
            join "public".authors as auth
        on auth.id = art.author
        group by auth.name
        order by views desc;
    ''')
    items = c.fetchall()

    print('\033[94mWho are the most popular article authors of all '
          'time?\033[0m')
    for item in items:
        print(' - ' + item[0] + ' - ' + str(item[1]) + ' views.')
    db.close()
    return items


def erroneousday():
    """Print a list with the dates the news site had more that 1% of the
    total requests leaded to an error """
    db = psycopg2.connect(database=DBNAME, user='postgres')
    c = db.cursor()
    try:
        c.execute('''
            select totals.day, totals.erroneous_requests /
             totals.total_requests::float * 100 as error_rate
            from requests_per_day as totals
            where (totals.erroneous_requests / totals.total_requests::float *
             100) > 1
            group by totals.day, error_rate
            order by error_rate desc;
        ''')
        items = c.fetchall()
        print('\033[94mOn which days did more than 1% of requests lead to '
              'errors?\033[0m')
        for item in items:
            print(
                ' - ' + item[0].strftime('%B %d, %Y') + ' - ' + '\033[31m'
                '{0:.2f}'.format(item[1]) + '% errors.\033[0m')
    except psycopg2.ProgrammingError as error:
        if '"requests_per_day" does not exist' in str(error):
            print('\033[31mView "requests_per_day" does not exists! Re-run '
                  'this with the --reloadviews arg.\033[0m')
        else:
            print('\033[31m' + error + '\033[0m')
        items = []

    db.close()
    return items


def reloadviews():
    """Drop the views for this program and create them anew."""
    db = psycopg2.connect(database=DBNAME, user='postgres')
    c = db.cursor()
    c.execute('''
        create or replace view requests_per_day as
            (select tl.datet as day, count(lo.id) as erroneous_requests, tl.c
             as total_requests
                from "public"."log" as lo
                join (select date_trunc('day', time) as datet, count(time) as
                c from "public".log group by datet) as tl
                    on date_trunc('day', lo.time) = tl.datet
                where lo.status not like '2%'
                group by tl.datet, tl.c
                order by tl.datet);
        ''')
    db.commit()
    print('\033[93mViews reloaded successfully!\033[0m')
    db.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''
            Run the program with the desired report you want to see.

            - \033[94mtop3articles\033[0m: What are the most popular three
             articles of all time?
            - \033[94mtopauthors\033[0m: Who are the most popular article
             authors of all time?
            - \033[94merroneousday\033[0m: On which days did more than 1% of
             requests lead to errors?
            - \033[94mall\033[0m: Run all of the reports. This is the default
             option.

            \033[93mThe \033[94mall\033[93m option might take some time to
             load.\033[0m
        ''')
    parser.add_argument('operation', nargs='?', default='all',
                        choices=['top3articles', 'topauthors', 'erroneousday',
                                 'all'])
    parser.add_argument('--reloadviews',
                        action='store_true',
                        help='Create anew the views required for this program')

    args = parser.parse_args()

    if args.reloadviews:
        reloadviews()

    if args.operation == 'top3articles':
        top3articles()
    elif args.operation == 'topauthors':
        topauthors()
    elif args.operation == 'erroneousday':
        erroneousday()
    elif args.operation == 'all':
        top3articles()
        topauthors()
        erroneousday()
