import copy
import json
import spacy
import unidecode

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

text = ("Albert Einstein, (born March 14, 1879, Ulm, Württemberg, Germany—died April 18, 1955, "
    "Princeton, New Jersey, U.S.), German-born physicist who developed the special and "
    "general theories of relativity and won the Nobel Prize for Physics in 1921 for his "
    "explanation of the photoelectric effect. Einstein is generally considered the most "
    "influential physicist of the 20th century.")

# convert unicode characters to ascii
text = unidecode.unidecode(text)

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
            for i in range(len(sentence.ents)):
                for j in range(len(sentence.ents)):
                    if i != j:
                        jsonSentence["subj_start"] = sentence.ents[i].start
                        jsonSentence["subj_end"] = sentence.ents[i].end - 1
                        jsonSentence["obj_start"] = sentence.ents[j].start
                        jsonSentence["obj_end"] = sentence.ents[j].end - 1
                        jsonSentence["subj_type"] = __self__.convertNER(sentence.ents[i].label_)
                        jsonSentence["obj_type"] = __self__.convertNER(sentence.ents[j].label_)
                        jsonifiedSentences.append(copy.deepcopy(jsonSentence))

        with open(__self__.filename, 'w') as json_file:
            json.dump(jsonifiedSentences, json_file)

## testing ##
temp = Generator(text, 'dataset/generated_data/temp.json')
temp.generate()
