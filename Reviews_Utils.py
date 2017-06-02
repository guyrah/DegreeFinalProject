import simplejson as json
import os


def count_restaurant_reviews(json_file_path, restaurant_ids):
    restaurant_counter = 0
    not_restaurant_counter = 0
    counters = dict()

    with open(json_file_path, 'r') as file:
        for i, line in enumerate(file):
            line_contents = json.loads(line)
            try:
                if str(line_contents['business_id']) in restaurant_ids:
                    counters['restaurant_reviews'] = counters.get('restaurant_reviews', 0) + 1
                    if len(str(line_contents['text']).split()) < 150:
                        counters['reviews_shorter_than_150'] = counters.get('reviews_shorter_than_150', 0) + 1
                    if len(str(line_contents['text']).split()) < 100:
                        counters['reviews_shorter_than_100'] = counters.get('reviews_shorter_than_100', 0) + 1
                    if any(x in str(line_contents['text']) for x in ['dirty', 'clean']):
                        counters['clean'] = counters.get('clean', 0) + 1
                    if any(x in str(line_contents['text']) for x in ['fast', 'slow']):
                        counters['speed'] = counters.get('speed', 0) + 1
                    if any(x in str(line_contents['text']) for x in ['big', 'small']):
                        counters['size'] = counters.get('size', 0) + 1
            except Exception as e:
                counters['exceptions'] = counters.get('exceptions', 0) + 1
                #print e

            print i


    for k,v in counters.iteritems():
        print str(k) + ': ' + str(v)


def get_restaurant_reviews(json_file_path, restaurant_ids):
    restaurant_counter = 0
    not_restaurant_counter = 0
    reviews = dict()

    with open(json_file_path, 'r') as file:
        for i, line in enumerate(file):
            line_contents = json.loads(line)

            if str(line_contents['business_id']) in restaurant_ids:
                if not reviews.has_key(line_contents['business_id']):
                    try:
                        reviews[line_contents['business _id']] = str(line_contents['text'])
                    except Exception as e:
                        print e


            print i


    with open('reviews.txt', 'w') as file:
        for line in reviews.values():
            file.write(line + '\n----------------------\n')

    print restaurant_counter
    print not_restaurant_counter


def get_restaurant_business_id(json_file_path, ids_path=None, overwrite=False):

    """Read in the json dataset file and return the superset of column names."""
    resturant_ids =  list()

    # If file already exists and not to overwrite
    if os.path.isfile(ids_path) and overwrite == False:
        with open(ids_path, 'r') as fin:
            resturant_ids = fin.read().splitlines()
    else:
        with open(json_file_path) as fin:
            for i, line in enumerate(fin):
                print i
                line_contents = json.loads(line)

                if 'Restaurants' in line_contents['categories']:
                    resturant_ids.append(str(line_contents['business_id']))

        if ids_path != None:
            with open(ids_path, 'w') as output_file:
                output_file.write('\n'.join(resturant_ids))

    return resturant_ids


def json_to_csv(src_path, tgt_path):
    fields = ['review_id', 'qualityrank','quality_of_service_rank',\
              'fast_rank','price_rank','big_dish_rank',\
              'value_for_money_rank','clean_rank',\
              'good_for_vegan_rank','good_for_meat_rank']

    with open(src_path,'r') as src_file:
        with open(tgt_path, 'w') as tgt_file:
            tgt_file.write(','.join(fields) + '\n')

            # Runns on each line - which supposed to be a doc
            for line in src_file:
                current_json = json.loads(line)
                current_fields = list()
                for f in fields:
                    current_fields.append(str(current_json.get(f,'')))

                tgt_file.write(','.join(current_fields) + '\n')


def json_stats_counter(src_path):
    fields = ['qualityrank','quality_of_service_rank',\
              'fast_rank','price_rank','big_dish_rank',\
              'value_for_money_rank','clean_rank',\
              'good_for_vegan_rank','good_for_meat_rank']
    stats_counter = dict()

    for f in fields:
        stats_counter[f] = [0] * 4


    with open(src_path,'r') as src_file:
        for line in src_file:
            current_json = json.loads(line)
            for f in fields:
                if current_json.has_key(f):
                    stats_counter[f][int(current_json[f])] = int(stats_counter.get(f,[0,0,0,0])[int(current_json[f])]) + 1

    for k,v in stats_counter.iteritems():
        print k, v



restaurant_business_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_business.json'
restaurant_reviews_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_review.json'
restaurant_business_ids_path = '/home/osboxes/Desktop/yelp_dataset/resturant_business_ids.txt'
restaurant_reviews_sample_file = 'reviews_sample.txt'




restaurant_ids = get_restaurant_business_id(restaurant_business_file,restaurant_business_ids_path)
count_restaurant_reviews(restaurant_reviews_file, restaurant_ids)

