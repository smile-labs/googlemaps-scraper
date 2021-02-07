# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv
from termcolor import colored
import time
import json
import mysql.connector

ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }
HEADER = ['id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']
HEADER_W_SOURCE = ['id_review', 'caption', 'relative_date','retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'url_source']

def csv_writer(source_field, ind_sort_by, path='data/'):
    outfile= ind_sort_by + '_gm_reviews.csv'
    targetfile = open(path + outfile, mode='w', encoding='utf-8', newline='\n')
    writer = csv.writer(targetfile, quoting=csv.QUOTE_MINIMAL)

    if source_field:
        h = HEADER_W_SOURCE
    else:
        h = HEADER
    writer.writerow(h)

    return writer

def exist_review(review, mysql_data):
    cursor = connection.cursor()
    sql = 'SELECT * FROM ' + mysql_data['table'] + ' WHERE id = "' + review['id_review'] + '"'
    cursor.execute(sql)
    return cursor.fetchone()

def insert_review(review, mysql_data):
    find = exist_review(review, mysql_data)
    if (find == None):
        cursor = connection.cursor()
        sql = 'INSERT INTO ' + mysql_data['table'] + ' (url, id, data) VALUES (%s, %s, %s)'
        cursor.execute(sql, (mysql_data['url'], review['id_review'], json.dumps(review)))

        connection.commit()
        print(review)
        return True
    else:
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--sort_by', type=str, default='newest', help='sort by most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file (for multiple urls in a single file)')
    parser.add_argument('--output', dest='output', default='csv', help='set mysql database as output for data')
    parser.add_argument('--mysql_host', dest='mysql_host', default='localhost')
    parser.add_argument('--mysql_user', dest='mysql_user', default='root')
    parser.add_argument('--mysql_password', dest='mysql_password', default='')
    parser.add_argument('--mysql_database', dest='mysql_database', default='scrapper')
    parser.add_argument('--mysql_table', dest='mysql_table', default='google_places_reviews')

    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()

    writer = None

    # mysql connection
    if (args.output == 'mysql'):
        mysql_data = {
            'table': args.mysql_table
        }
        connection = mysql.connector.connect(
            host=args.mysql_host,
            user=args.mysql_user,
            password=args.mysql_password,
            database=args.mysql_database
        )

    # store reviews in CSV file
    if (args.output == 'csv'):
        writer = csv_writer(args.source, args.sort_by)

    with GoogleMapsScraper(debug=args.debug) as scraper:
        with open(args.i, 'r') as urls_file:
            for url in urls_file:
                print(url)
                mysql_data['url'] = url
                if args.place:
                    print(scraper.get_account(url))
                else:
                    error = scraper.sort_by(url, ind[args.sort_by])
                    print(error)

                print(args)
                if error == 0:

                    n = 0

                    # if ind[args.sort_by] == 0:
                    #     scraper.more_reviews()
                        
                    print(n)
                    while n < args.N:
                        print(colored('[Review ' + str(n) + ']', 'cyan'))
                        reviews = scraper.get_reviews(n)
                        if (len(reviews) == 0):
                            break
                        result = True

                        for r in reviews:
                            if (args.output == 'mysql'):
                                result = insert_review(r, mysql_data)
                                if (result == False):
                                    print('Rewview found, stopping URL')
                                    break 
                            if (writer != None):
                                row_data = list(r.values())
                                if args.source:
                                    row_data.append(url[:-1])

                                writer.writerow(row_data)
                        if (result == False):
                            break
                        n += len(reviews)
