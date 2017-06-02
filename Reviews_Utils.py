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


def count_restaurant_fields(json_file_path, restaurant_ids):
    counters = dict()
    counters['stats'] = dict()

    with open(json_file_path, 'r') as file:
        for i, line in enumerate(file):
            line_contents = json.loads(line)
            try:
                if str(line_contents['business_id']) in restaurant_ids:
                    counters['stats']['restaurants'] = counters['stats'].get('restaurants', 0) + 1

                    for att in line_contents['attributes'].keys():
                        if not counters.has_key('attributes'):
                            counters['attributes'] = dict()

                        counters['attributes'][att] = '1'
                    for field in ['Noise Level', 'Music', 'Attire', 'Ambience', 'Good for Kids', 'Price Range', 'Good For', 'Wheelchair Accessible']:
                        if line_contents['attributes'].has_key(field):
                            if not counters.has_key(field):
                                counters[field] = dict()

                            if isinstance(line_contents['attributes'][field], dict):
                                did_true = False
                                for k in line_contents['attributes'][field].keys():
                                    if line_contents['attributes'][field][k]:
                                        if did_true:
                                            counters['stats']['more_than_2_true_in_key'] = counters['stats'].get('more_than_2_true_in_key', 0) + 1
                                        else:
                                            did_true = True

                                    counters[field][k] = '1'
                            else:
                                counters[field][line_contents['attributes'][field]] = '1'
                else:
                    counters['stats']['non_restaurants'] = counters['stats'].get('non_restaurants', 0) + 1

            except Exception as e:
                counters['stats']['exceptions'] = counters['stats'].get('exceptions', 0) + 1
                #print e

            print i


            #if i > 1000:
            #   break


    for k1 in counters.keys():
        if k1 != 'stats':
            print k1 + ':'
            for i, k2 in enumerate(counters[k1].keys()):
                print str(i) + '. ', k2

            print

    print 'general stats:'
    for k,v in counters['stats'].iteritems():
        print str(k) + ': ' + str(v)
    #print counters['attributes'].keys()


def noise_level_to_number(noise_level, fields_dict):
    if noise_level == 'very_loud':
        fields_dict['noise_level'] = 1
    elif noise_level == 'loud':
        fields_dict['noise_level'] = 2
    elif noise_level == 'average':
        fields_dict['noise_level'] = 3
    elif noise_level == 'quiet':
        fields_dict['noise_level'] = 4
    else:
        raise 'unknown noise level'


def ambience_to_number(ambience, fields_dict):
    for k, v in ambience.iteritems():
        if k == 'romantic':
            if v:
                fields_dict['romantic'] = 1
            else:
                fields_dict['romantic'] = 0
        if k == 'casual':
            if v:
                fields_dict['casual'] = 1
            else:
                fields_dict['casual'] = 0
        if k == 'upscale':
            if v:
                fields_dict['upscale'] = 1
            else:
                fields_dict['upscale'] = 0

def wheelchair_to_number(wheelchair, fields_dict):
    if wheelchair:
        fields_dict['wheelchair'] = 1
    else:
        fields_dict['wheelchair'] = 0


def good_for_kids_to_number(good_for_kids, fields_dict):
    if good_for_kids:
        fields_dict['good_for_kids'] = 1
    else:
        fields_dict['good_for_kids'] = 0


def price_level_to_number(price_level, fields_dict):
    if price_level == 1:
        fields_dict['cheap'] = 4
    elif price_level == 2:
        fields_dict['cheap'] = 3
    elif price_level == 3:
        fields_dict['cheap'] = 2
    elif price_level == 4:
        fields_dict['cheap'] = 1
    else:
        raise 'unknown cheap'


def get_business_json(json_file_path, restaurant_ids):
    business_json = dict()

    with open(json_file_path, 'r') as file:
        for i, line in enumerate(file):
            line_contents = json.loads(line)
            try:
                if str(line_contents['business_id']) in restaurant_ids:
                    business_json[line_contents['business_id']] = dict()
                    business_json[line_contents['business_id']]['full_address'] = line_contents['full_address']
                    business_json[line_contents['business_id']]['name'] = line_contents['name']
                    business_json[line_contents['business_id']]['hours'] = line_contents['hours']
                    #business_json[line_contents['business_id']]['neighborhood'] = line_contents['neighborhood']
                    business_json[line_contents['business_id']]['city'] = line_contents['city']
                    business_json[line_contents['business_id']]['stars'] = line_contents['stars']
                    business_json[line_contents['business_id']]['open'] = line_contents['open']


                    if line_contents['attributes'].has_key('Price Range'):
                        price_level_to_number(line_contents['attributes']['Price Range'], business_json[line_contents['business_id']])
                    if line_contents['attributes'].has_key('Good for Kids'):
                        good_for_kids_to_number(line_contents['attributes']['Good for Kids'], business_json[line_contents['business_id']])
                    if line_contents['attributes'].has_key('Wheelchair Accessible'):
                        wheelchair_to_number(line_contents['attributes']['Wheelchair Accessible'], business_json[line_contents['business_id']])
                    if line_contents['attributes'].has_key('Ambience'):
                        ambience_to_number(line_contents['attributes']['Ambience'], business_json[line_contents['business_id']])
                    if line_contents['attributes'].has_key('Noise Level'):
                        noise_level_to_number(line_contents['attributes']['Noise Level'], business_json[line_contents['business_id']])

            except Exception as e:
                #counters['stats']['exceptions'] = counters['stats'].get('exceptions', 0) + 1
                print e

        return business_json


restaurant_business_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_business.json'
restaurant_reviews_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_review.json'
restaurant_business_ids_path = '/home/osboxes/Desktop/yelp_dataset/resturant_business_ids.txt'
restaurant_reviews_sample_file = 'reviews_sample.txt'


restaurant_ids = get_restaurant_business_id(restaurant_business_file,restaurant_business_ids_path)
#count_restaurant_reviews(restaurant_reviews_file, restaurant_ids)
get_business_json('/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_business.json', restaurant_ids)


