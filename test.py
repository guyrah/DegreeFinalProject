import actions

import Mongo_Access


def test():
    '''
    voc = NLP_Utils.read_vocabulary('vocabulary.txt')
    
    text = "I blablabla like like this place a lot. It's a good toasted hoagie.\n\nI actually don't like a my bun exploding with meat, but as a previous poster mentioned if you do maybe you wouldn't like this place.\n\nThe inside badly needs updated though. \n\nThe staff is friendly."
    
    NLP_Utils.text_to_hot_vector(text, voc)
    '''
    '''
    a = list()
    with open('tagged_data.txt', 'r') as file:
        for line in file:
            a.append(loads(line))
    '''

    #actions.refresh_vocabulary()

    #Mongo_Access.get_sequences('mongodb://193.106.55.77:27017')