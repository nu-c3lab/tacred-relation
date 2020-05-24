"""
Run evaluation with saved models.
"""

import os
import random
import argparse
import pickle
import torch
import torch.nn as nn
import torch.optim as optim

from data.loader import DataLoader
from model.rnn import RelationModel
from utils import torch_utils, scorer, constant, helper
from utils.vocab import Vocab

parser = argparse.ArgumentParser()
parser.add_argument('model_dir', type=str, help='Directory of the model.')
parser.add_argument('--model', type=str, default='best_model.pt', help='Name of the model file.')
parser.add_argument('--data_dir', type=str, default='dataset/generated_data')
parser.add_argument('--dataset', type=str, default='test', help="Evaluate on dev or test.")
parser.add_argument('--out', type=str, default='', help="Save model predictions to this dir.")

parser.add_argument('--seed', type=int, default=1234)
parser.add_argument('--cuda', type=bool, default=torch.cuda.is_available())
parser.add_argument('--cpu', action='store_true')
args = parser.parse_args()

torch.manual_seed(args.seed)
random.seed(1234)
if args.cpu:
    args.cuda = False
elif args.cuda:
    torch.cuda.manual_seed(args.seed)

# load opt
model_file = args.model_dir + '/' + args.model
print("Loading model from {}".format(model_file))
opt = torch_utils.load_config(model_file)
model = RelationModel(opt)
model.load(model_file)

# load vocab
vocab_file = args.model_dir + '/vocab.pkl'
vocab = Vocab(vocab_file, load=True)
assert opt['vocab_size'] == vocab.size, "Vocab size must match that in the saved model."

# load data
data_file = args.data_dir + '/{}.json'.format(args.dataset)
print("Loading data from {} with batch size {}...".format(data_file, opt['batch_size']))
batch = DataLoader(data_file, opt['batch_size'], opt, vocab, evaluation=True)

helper.print_config(opt)
id2label = dict([(v,k) for k,v in constant.LABEL_TO_ID.items()])

predictions = []
all_probs = []
for i, b in enumerate(batch):
    preds, probs = model.predictUnseen(b)
    predictions += preds
    all_probs += probs
relations = ['(' + id2label[predictions[idx]] + ' ' + batch.entities[idx][0] + ' ' + batch.entities[idx][1] + ') ' + str(max(all_probs[idx])) \
                for idx in range(len(predictions)) \
                if predictions[idx] != 0 and max(all_probs[idx]) > 0.75]
#for idx in range(len(relations)):


# save probability scores
if len(args.out) > 0:
    helper.ensure_dir(os.path.dirname(args.out))
    with open(args.out + '/out.txt', 'w') as outfile:
        outfile.writelines("{}\n".format(relation) for relation in relations)
    print("Predictions saved to {}.".format(args.out))

print("Generation finished.")

