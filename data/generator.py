import copy
import json
import spacy
import unidecode
import wikipedia
from preprocessing import preprocessing

# {
#   "id": "098f6fb926eb676a14fd", "relation": "per:title",
#   "token": ["Youth", "minister", "and", "``", "Street", "General", "''", "Charles", "Ble", "Goude", ",", "who", "is", "under", "UN", "sanctions", "for", "``", "acts", "of", "violence", "by", "street", "militias", ",", "including", "beatings", ",", "rapes", "and", "extrajudicial", "killings", "''", ",", "vows", "to", "fight", "for", "Ivory", "Coast", "'s", "sovereignty", "."],
#   "subj_start": 7, "subj_end": 9, "obj_start": 1, "obj_end": 1, "subj_type": "PERSON", "obj_type": "TITLE",
#   "stanford_pos": ["NN", "NN", "CC", "``", "NNP", "NNP", "''", "NNP", "NNP", "NNP", ",", "WP", "VBZ", "IN", "NNP", "NNS", "IN", "``", "NNS", "IN", "NN", "IN", "NN", "NNS", ",", "VBG", "NNS", ",", "NNS", "CC", "JJ", "NNS", "''", ",", "VBZ", "TO", "VB", "IN", "NNP", "NNP", "POS", "NN", "."],
#   "stanford_ner": ["O", "O", "O", "O", "O", "O", "O", "PERSON", "PERSON", "PERSON", "O", "O", "O", "O", "ORGANIZATION", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "O", "LOCATION", "LOCATION", "O", "O", "O"],
#   "stanford_head": ["2", "35", "2", "10", "10", "10", "10", "10", "10", "2", "10", "16", "16", "16", "16", "10", "19", "19", "16", "21", "19", "24", "24", "19", "24", "27", "24", "27", "27", "27", "32", "27", "19", "10", "0", "37", "35", "42", "40", "42", "40", "37", "35"],
#   "stanford_deprel": ["compound", "nsubj", "cc", "punct", "compound", "compound", "punct", "compound", "compound", "conj", "punct", "nsubj", "cop", "case", "compound", "acl:relcl", "case", "punct", "nmod", "case", "nmod", "case", "compound", "nmod", "punct", "case", "nmod", "punct", "conj", "cc", "amod", "conj", "punct", "punct", "ROOT", "mark", "xcomp", "case", "compound", "nmod:poss", "case", "nmod", "punct"]
# }
nlp = spacy.load("en_core_web_sm")
#page = wikipedia.page("Albert Einstein")
#page = wikipedia.page("Nikola Tesla")
#page = wikipedia.page("Isaac Newton")

class temp(object):
    def __init__ (self, text, title):
        self.content = text
        self.title = title

with open('temp.txt', 'r') as file:
    page = temp(file.read().replace('\n', ' '), 'Albert Einstein')

# convert unicode characters to ascii
text = unidecode.unidecode(text)

text = preprocessing(page)

#text = ("Albert Einstein, (born March 14, 1879, Ulm, Württemberg, Germany—died April 18, 1955, "
#    "Princeton, New Jersey, U.S.), German-born physicist who developed the special and "
#    "general theories of relativity and won the Nobel Prize for Physics in 1921 for his "
#    "explanation of the photoelectric effect. Einstein is generally considered the most "
#    "influential physicist of the 20th century.")

#text = "Youth minister and \"Street General\" Charles Ble Goude, who is under UN sanctions for \"acts of violence by street militias, including beatings, rapes and extrajudicial killings\", vows to fight for Ivory Coast's sovereignty."
#text = "Taiwan's Chunghwa Telecom Co plans to spend 129 billion New Taiwan dollars -LRB- US$ 397 billion; euro3 billion -RRB- over the next five years to upgrade its telecommunications networks and build a new undersea cable system, Chairman Ho Chen Tan said Wednesday."


class Generator(object):

    def __init__ (__self__, text, filename):
        __self__.text = text
        __self__.filename = filename

    def convertNER(__self__, ner):
        if ner == '':
            return 'O'
        if ner == 'ORG':
            return 'ORGANIZATION'
        if ner == 'GPE':
            return 'LOCATION'
        else:
            return ner

    def generate(__self__):
        parsed = nlp(__self__.text)
        jsonifiedSentences = []
        entity_variations = [page.title, *page.title.split()]

        for raw_sentence in parsed.sents:
            # reparsing sentence here so that the entity start and end positions are relative to
            # the beginning of the sentence instead of the beginning of the entire text
            sentence = nlp(raw_sentence.text)
            jsonSentence = {
            #    "id": "none",
                "relation": "no_relation",
                "token": [],
            #    "subj_start": -1, "subj_end": -1, "obj_start": -1, "obj_end": -1, "subj_type": "", "obj_type": "",
                "stanford_pos": [],
                "stanford_ner": [],
                "stanford_head": [],
                "stanford_deprel": []
            }

            for word in sentence:
                jsonSentence["token"].append(word.text)
                jsonSentence["stanford_pos"].append(word.tag_)
                jsonSentence["stanford_ner"].append(__self__.convertNER(word.ent_type_))
                jsonSentence["stanford_head"].append(word.head.i + 1)
                jsonSentence["stanford_deprel"].append(word.dep_)
            for subject in sentence.ents:
                if  subject.text in entity_variations:
                    for noun in sentence.ents: # sentence.noun_chunks:
                        print(set(subject.text.split()).intersection(set(entity_variations)))
                        if len(set(subject.text.split()).intersection(set(entity_variations))) == 0:
                            jsonSentence["subj_start"] = subject.start
                            jsonSentence["subj_end"] = subject.end - 1
                            jsonSentence["obj_start"] = noun.start
                            jsonSentence["obj_end"] = noun.end - 1
                            # TODO: We probably don't want to use entity extraction for comparing elements of the document
                            # i.e. spacy does not recognize "physicist" as an entity, and so the relationship
                            # (per:title Albert_Einstein Physisist) can never be extracted. As an alternative, it might be
                            # best to use noun chunk extraction or something similar.
                            # Another option might be to traverse the spacy parse tree to get complete nouns
                            jsonSentence["subj_type"] = __self__.convertNER(subject.label_)
                            jsonSentence["obj_type"] = __self__.convertNER(noun.label_)
                            jsonifiedSentences.append(copy.deepcopy(jsonSentence))

            
        with open(__self__.filename, 'w') as json_file:
            json.dump(jsonifiedSentences, json_file)

## testing ##
generator = Generator(text, 'dataset/generated_data/out.json')
generator.generate()
