# -*- coding: utf-8 -*-
from googlemaps import GoogleMapsScraper
from datetime import datetime, timedelta
import argparse
import csv
from termcolor import colored
import time
import json

from utils import array_find_index, array_slice_from, array_slice_to

ind = {'most_relevant' : 0 , 'newest' : 1, 'highest_rating' : 2, 'lowest_rating' : 3 }
HEADER = ['id_review', 'caption', 'relative_date', 'retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user']
HEADER_W_SOURCE = ['id_review', 'caption', 'relative_date','retrieval_date', 'rating', 'username', 'n_review_user', 'n_photo_user', 'url_user', 'url_source']

def get_reviews(n):
    return json.loads('[{"review_id": "ChZDSUhNMG9nS0VJQ0FnSUM2eVpyTmJBEAE"},{"review_id": "ChdDSUhNMG9nS0VJQ0FnSUM2NXFycDVBRRAB"},{"review_id": "ChdDSUhNMG9nS0VJQ0FnSURhNXZmTm1BRRAB"}]')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Maps reviews scraper.')
    parser.add_argument('--N', type=int, default=100, help='Number of reviews to scrape')
    parser.add_argument('--i', type=str, default='urls.txt', help='target URLs file')
    parser.add_argument('--url', type=str, default='', help='URL to parse')
    parser.add_argument('--driver_host', type=str, default='http://localhost:4444', help='Driver host')
    parser.add_argument('--sort_by', type=str, default='newest', help='sort by most_relevant, newest, highest_rating or lowest_rating')
    parser.add_argument('--place', dest='place', action='store_true', help='Scrape place metadata')
    parser.add_argument('--debug', dest='debug', action='store_true', help='Run scraper using browser graphical interface')
    parser.add_argument('--source', dest='source', action='store_true', help='Add source url to CSV file (for multiple urls in a single file)')
    parser.add_argument('--start', type=str, default='', help='Start scraping when this review is found')
    parser.add_argument('--end', type=str, default='', help='Stop scraping when this review is found')

    parser.set_defaults(place=False, debug=False, source=False)

    args = parser.parse_args()

    writer = None
    urls = []
    
    if (args.url != ''):
        urls = [args.url]


    output_reviews = []
    can_start = False
    if (args.start == ''):
        can_start = True

    with GoogleMapsScraper(debug=args.debug, driver_host = args.driver_host) as scraper:
        for url in urls:

            if args.place:
                None
            else:
                error = scraper.sort_by(url, ind[args.sort_by])

            if error == 0:
                n = 0
                def match_review_id(item):
                    if (args.start == item['review_id']):
                        return True
                    return False
                while len(output_reviews) < args.N:
                    reviews = scraper.get_reviews(n)
                    if (args.end != ''):
                        foundIndex = array_find_index(reviews, match_review_id)
                        if (foundIndex > -1):
                            sliced = array_slice_to(reviews, foundIndex)
                            output_reviews = output_reviews + sliced
                            break
                    n += len(reviews)

                    if (len(reviews) == 0):
                        break
                    result = True
                    if (not can_start):

                        foundIndex = array_find_index(reviews, match_review_id)
                        if (foundIndex > -1):
                            can_start = True
                            sliced = array_slice_from(reviews, foundIndex)
                            output_reviews = output_reviews + sliced
                    else:
                        output_reviews = output_reviews + reviews
    print(json.dumps(output_reviews))
