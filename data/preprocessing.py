from pycorenlp import StanfordCoreNLP
import wikipedia
import re
import gender_guesser.detector as gender


"""
nlp = StanfordCoreNLP('http://localhost:8000')


def resolve(corenlp_output):
    #Transfer the word form of the antecedent to its associated pronominal anaphor(s)
    long_references = []
    for coref in corenlp_output['corefs']:
        mentions = corenlp_output['corefs'][coref]
        antecedent = mentions[0]
        if len(antecedent['text'].split(' ')) > 3:
            long_references.append(coref)
    for ref in long_references:
        corenlp_output['corefs'].pop(ref)
    for coref in corenlp_output['corefs']:
        mentions = corenlp_output['corefs'][coref]
        antecedent = mentions[0]  # the antecedent is the first mention in the coreference chain
        for j in range(1, len(mentions)):
            mention = mentions[j]
            if mention['type'] == 'PRONOMINAL':
                # get the attributes of the target mention in the corresponding sentence
                target_sentence = mention['sentNum']
                target_token = mention['startIndex'] - 1
                # transfer the antecedent's word form to the appropriate token in the sentence
                corenlp_output['sentences'][target_sentence - 1]['tokens'][target_token]['word'] = antecedent['text']


def print_resolved(corenlp_output):
    #Print the "resolved" output 
    possessives = ['hers', 'his', 'their', 'theirs']
    all_text = ''
    for sentence in corenlp_output['sentences']:
        for token in sentence['tokens']:
            output_word = token['word']
            # check lemmas as well as tags for possessive pronouns in case of tagging errors
            if token['lemma'] in possessives or token['pos'] == 'PRP$':
                output_word += "'s"  # add the possessive morpheme
            output_word += token['after']
            all_text += output_word
    return all_text


page = wikipedia.page("Albert Einstein")

#text = ("Albert Einstein, (born March 14, 1879, Ulm, Württemberg, Germany—died April 18, 1955, "
#    "Princeton, New Jersey, U.S.), German-born physicist who developed the special and "
#    "general theories of relativity and won the Nobel Prize for Physics in 1921 for his "
#    "explanation of the photoelectric effect. Einstein is generally considered the most "
#    "influential physicist of the 20th century.")



text = page.content.split('== References ==')[0]
text = re.sub(r'\((?:[^)(]|\((?:[^)(]|\([^)(]*\))*\))*\)', '', text)
text = re.sub(r'\====[^)]*\====', '', text)
text = re.sub(r'\===[^)]*\===', '', text)
text = re.sub(r'\==[^)]*\==', '', text)

new_text = re.sub(r'[.]+', "\\n", text);

with open("original.txt","w+") as f1:
    f1.write(new_text)

output = nlp.annotate(text, properties= {'annotators':'dcoref','outputFormat':'json','ner.useSUTime':'false'})

resolve(output)

print('Original:', text)
print('Resolved: ', end='')
resolved = print_resolved(output)

if gender.Detector().get_gender(page.title.split()[0]) == 'male':
    resolved = re.sub(r'\b[hH]e\b|\b[hH]im\b',page.title, resolved)
    resolved = re.sub(r'\b[hH]is\b',page.title+'\'s', resolved)
elif gender.Detector().get_gender(page.title.split()[0]) == 'female':
    resolved = re.sub(r'\b[Ss]he\b',page.title, resolved)
    resolved = re.sub(r'\b[Hh]ers\b',page.title+'\'s', resolved)

new_resolved = re.sub(r'[.]+', "\\n", resolved)

with open("resolved.txt","w+") as f2:
    f2.write(new_resolved)

"""

def preprocessing(page):

    def resolve(corenlp_output):
        """ Transfer the word form of the antecedent to its associated pronominal anaphor(s) """
        long_references = []
        for coref in corenlp_output['corefs']:
            mentions = corenlp_output['corefs'][coref]
            antecedent = mentions[0]
            if len(antecedent['text'].split(' ')) > 3:
                long_references.append(coref)
        for ref in long_references:
            corenlp_output['corefs'].pop(ref)
        for coref in corenlp_output['corefs']:
            mentions = corenlp_output['corefs'][coref]
            antecedent = mentions[0]  # the antecedent is the first mention in the coreference chain
            for j in range(1, len(mentions)):
                mention = mentions[j]
                if mention['type'] == 'PRONOMINAL':
                    # get the attributes of the target mention in the corresponding sentence
                    target_sentence = mention['sentNum']
                    target_token = mention['startIndex'] - 1
                    # transfer the antecedent's word form to the appropriate token in the sentence
                    corenlp_output['sentences'][target_sentence - 1]['tokens'][target_token]['word'] = antecedent['text']


    def print_resolved(corenlp_output):
        """ Print the "resolved" output """
        possessives = ['hers', 'his', 'their', 'theirs']
        all_text = ''
        for sentence in corenlp_output['sentences']:
            for token in sentence['tokens']:
                output_word = token['word']
                # check lemmas as well as tags for possessive pronouns in case of tagging errors
                if token['lemma'] in possessives or token['pos'] == 'PRP$':
                    output_word += "'s"  # add the possessive morpheme
                output_word += token['after']
                all_text += output_word
        return all_text

    def article_cleanup(text):
        text = page.content.split('== References ==')[0]
        text = re.sub(r'\((?:[^)(]|\((?:[^)(]|\([^)(]*\))*\))*\)', '', text)
        text = re.sub(r'\====[^)]*\====', '', text)
        text = re.sub(r'\===[^)]*\===', '', text)
        text = re.sub(r'\==[^)]*\==', '', text)
        return text

    def remaining_pronoun_cleanup(resolved, gender):
        if gender == 'male':
            resolved = re.sub(r'\b[hH]e\b|\b[hH]im\b',page.title, resolved)
            resolved = re.sub(r'\b[hH]is\b',page.title+'\'s', resolved)
        elif gender == 'female':
            resolved = re.sub(r'\b[Ss]he\b',page.title, resolved)
            resolved = re.sub(r'\b[Hh]ers\b',page.title+'\'s', resolved)
        return resolved
    

    nlp = StanfordCoreNLP('http://localhost:8000')
    text = page.content.split('== References ==')[0]
    text = article_cleanup(text)

    output = nlp.annotate(text, properties= {'annotators':'dcoref','outputFormat':'json','ner.useSUTime':'false'})
    resolve(output)
    resolved_text = print_resolved(output)
    resolved_text = remaining_pronoun_cleanup(resolved_text, gender.Detector().get_gender(page.title.split()[0]))

    new_resolved = re.sub(r'[.]+', "\\n", resolved_text)

    with open("resolved.txt","w+") as f2:
        f2.write(new_resolved)

    return resolved_text

preprocessed_text = preprocessing(wikipedia.page('Isaac Newton'))