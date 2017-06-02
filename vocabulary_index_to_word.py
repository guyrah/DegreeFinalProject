import NLP_Utils
import json

a = raw_input('function:')

if str(1) == a:
    voc = NLP_Utils.read_vocabulary('text_to_vector_vocabulary.txt')

    voc_list = [None] * len(voc)
    for k,v in voc.iteritems():
        voc_list[v.get_index()] = k

    while True:
        print voc_list[int(input("index: "))]
elif str(2) == a:
    src_path = 'tagged_data.json'
    target_field = 'quality_of_service_rank'
    category = '1'


    with open(src_path, 'r') as src_file:
        data_dict = {}

        filtered_count = 0
        data = list()
        target = list()
        # Runns on each line - which supposed to be a doc
        for line in src_file:
            add_line = False
            current_json = json.loads(line)
            if current_json.has_key(target_field):
                if str(current_json[target_field]) == str(category):
                    print current_json['text']

                    raw_input('')
