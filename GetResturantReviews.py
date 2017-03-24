import simplejson as json
import os
#

def get_restaurant_reviews(json_file_path, restaurant_ids):
    restaurant_counter = 0
    not_restaurant_counter = 0
    with open(json_file_path, 'r') as file:
        for line in file:
            line_contents = json.loads(line)
            if str(line_contents['business_id']) in restaurant_ids:
                restaurant_counter = restaurant_counter + 1
            else:
                not_restaurant_counter = not_restaurant_counter + 1

            print restaurant_counter + not_restaurant_counter



    print restaurant_counter
    print not_restaurant_counter


def get_restaurant_business_id(json_file_path, ids_path=None, overwrite=False):

    """Read in the json dataset file and return the superset of column names."""
    column_names = set()
    categories = set()
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


restaurant_business_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_business.json'
restaurant_reviews_file = '/home/osboxes/Desktop/yelp_dataset/yelp_academic_dataset_review.json'
restaurant_business_ids_path = '/home/osboxes/Desktop/yelp_dataset/resturant_business_ids.txt'

restaurant_ids = get_restaurant_business_id(restaurant_business_file,restaurant_business_ids_path)
get_restaurant_reviews(restaurant_reviews_file, restaurant_ids)
