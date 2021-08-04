# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv
from termcolor import colored
import time
import json

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--url', type=str, default='', help='URL to parse')
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
    if (args.output == 'csv'):
        writer = csv_writer(args.source, args.sort_by)

    urls = []
    
    if (args.url != ''):
        urls = [args.url]


    output_reviews = []

    with GoogleMapsScraper(debug=args.debug) as scraper:
        for url in urls:

            if args.place:
                None
            else:
                error = scraper.sort_by(url, ind[args.sort_by])

            if error == 0:
                n = 0
                while n < args.N:
                    reviews = scraper.get_reviews(n)
                    if (len(reviews) == 0):
                        break
                    result = True

                    output_reviews = output_reviews + reviews
                    n += len(reviews)
    print(json.dumps(output_reviews))
