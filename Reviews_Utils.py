import simplejson as json
import os
import NLP_Utils


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


def create_vocabulary(src_file_path, dst_file_path):
    exceptions = 0

    with open(src_file_path,'r') as file:
        word_counter = dict()

        counter = 1
        #
        for line in file:
            line_contents = json.loads(line)

            try:
                for word in str(NLP_Utils.remove_non_letters(line_contents['text'])).split():
                    word = NLP_Utils.stem_word(word)
                    word_counter[word] = word_counter.get(word, 0) + 1
            except Exception as e:
                print e
                exceptions += 1

            counter += 1

            if counter > 1000:
                break

    with open(dst_file_path, 'w') as file:
        for k, v in word_counter.items():
            file.write(k + ',' + str(v) + '\n')

    print 'number of exceptions: ', exceptions


restaurant_business_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_business.json'
restaurant_reviews_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_review.json'
restaurant_business_ids_path = '/home/osboxes/Desktop/yelp_dataset/resturant_business_ids.txt'
restaurant_reviews_sample_file = 'reviews_sample.txt'


create_vocabulary(restaurant_reviews_file, 'vocabulary.txt')

restaurant_ids = get_restaurant_business_id(restaurant_business_file,restaurant_business_ids_path)
count_restaurant_reviews(restaurant_reviews_file, restaurant_ids)

