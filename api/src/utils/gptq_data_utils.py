'''
From https://github.com/IST-DASLab/gptq/blob/main/datautils.py
'''

import numpy as np
import torch
from functools import lru_cache

def set_seed(seed):
    np.random.seed(seed)
    torch.random.manual_seed(seed)

@lru_cache
def get_wikitext2(nsamples, seed, seqlen, model):
    from datasets import load_dataset
    traindata = load_dataset('wikitext', 'wikitext-2-raw-v1', split='train')
    testdata = load_dataset('wikitext', 'wikitext-2-raw-v1', split='test')

    from transformers import AutoTokenizer 
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)
    trainenc = tokenizer("\n\n".join(traindata['text']), return_tensors='pt')
    testenc = tokenizer("\n\n".join(testdata['text']), return_tensors='pt')

    import random
    random.seed(seed)
    trainloader = []
    for _ in range(nsamples):
        i = random.randint(0, trainenc.input_ids.shape[1] - seqlen - 1)
        j = i + seqlen
        inp = trainenc.input_ids[:, i:j]
        tar = inp.clone()
        tar[:, :-1] = -100
        trainloader.append((inp, tar))
    return trainloader, testenc

@lru_cache
def get_ptb(nsamples, seed, seqlen, model):
    from datasets import load_dataset
    traindata = load_dataset('ptb_text_only', 'penn_treebank', split='train')
    valdata = load_dataset('ptb_text_only', 'penn_treebank', split='validation')

    from transformers import AutoTokenizer 
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)
    trainenc = tokenizer("\n\n".join(traindata['sentence']), return_tensors='pt')
    testenc = tokenizer("\n\n".join(valdata['sentence']), return_tensors='pt')

    import random
    random.seed(seed)
    trainloader = []
    for _ in range(nsamples):
        i = random.randint(0, trainenc.input_ids.shape[1] - seqlen - 1)
        j = i + seqlen
        inp = trainenc.input_ids[:, i:j]
        tar = inp.clone()
        tar[:, :-1] = -100
        trainloader.append((inp, tar))
    return trainloader, testenc

@lru_cache
def get_c4(nsamples, seed, seqlen, model):
    from datasets import load_dataset
    traindata = load_dataset(
        'allenai/c4', 'allenai--c4', data_files={'train': 'en/c4-train.00000-of-01024.json.gz'}, split='train'
    )
    valdata = load_dataset(
        'allenai/c4', 'allenai--c4', data_files={'validation': 'en/c4-validation.00000-of-00008.json.gz'}, split='validation'
    )

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)

    import random
    random.seed(seed)
    trainloader = []
    for _ in range(nsamples):
        while True:
            i = random.randint(0, len(traindata) - 1)
            trainenc = tokenizer(traindata[i]['text'], return_tensors='pt')
            if trainenc.input_ids.shape[1] >= seqlen:
                break
        i = random.randint(0, trainenc.input_ids.shape[1] - seqlen - 1)
        j = i + seqlen
        inp = trainenc.input_ids[:, i:j]
        tar = inp.clone()
        tar[:, :-1] = -100
        trainloader.append((inp, tar))

    import random
    random.seed(0)
    valenc = []
    for _ in range(256):
        while True:
            i = random.randint(0, len(valdata) - 1)
            tmp = tokenizer(valdata[i]['text'], return_tensors='pt')
            if tmp.input_ids.shape[1] >= seqlen:
                break
        i = random.randint(0, tmp.input_ids.shape[1] - seqlen - 1)
        j = i + seqlen
        valenc.append(tmp.input_ids[:, i:j])
    valenc = torch.hstack(valenc)
    class TokenizerWrapper:
        def __init__(self, input_ids):
            self.input_ids = input_ids
    valenc = TokenizerWrapper(valenc)

    return trainloader, valenc 

@lru_cache
def get_ptb_new(nsamples, seed, seqlen, model):
    from datasets import load_dataset
    traindata = load_dataset('ptb_text_only', 'penn_treebank', split='train')
    testdata = load_dataset('ptb_text_only', 'penn_treebank', split='test')

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)
    trainenc = tokenizer(" ".join(traindata['sentence']), return_tensors='pt')
    testenc = tokenizer(" ".join(testdata['sentence']), return_tensors='pt')

    import random
    random.seed(seed)
    trainloader = []
    for _ in range(nsamples):
        i = random.randint(0, trainenc.input_ids.shape[1] - seqlen - 1)
        j = i + seqlen
        inp = trainenc.input_ids[:, i:j]
        tar = inp.clone()
        tar[:, :-1] = -100
        trainloader.append((inp, tar))
    return trainloader, testenc

@lru_cache
def get_c4_new(nsamples, seed, seqlen, model):
    from datasets import load_dataset
    traindata = load_dataset(
        'allenai/c4', 'allenai--c4', data_files={'train': 'en/c4-train.00000-of-01024.json.gz'}, split='train'
    )
    valdata = load_dataset(
        'allenai/c4', 'allenai--c4', data_files={'validation': 'en/c4-validation.00000-of-00008.json.gz'}, split='validation'
    )

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)

    import random
    random.seed(seed)
    trainloader = []
    for _ in range(nsamples):
        while True:
            i = random.randint(0, len(traindata) - 1)
            trainenc = tokenizer(traindata[i]['text'], return_tensors='pt')
            if trainenc.input_ids.shape[1] >= seqlen:
                break
        i = random.randint(0, trainenc.input_ids.shape[1] - seqlen - 1)
        j = i + seqlen
        inp = trainenc.input_ids[:, i:j]
        tar = inp.clone()
        tar[:, :-1] = -100
        trainloader.append((inp, tar))

    valenc = tokenizer(' '.join(valdata[:1100]['text']), return_tensors='pt')
    valenc = valenc.input_ids[:, :(256 * seqlen)]

    class TokenizerWrapper:
        def __init__(self, input_ids):
            self.input_ids = input_ids
    valenc = TokenizerWrapper(valenc)

    return trainloader, valenc

@lru_cache
def get_gsm8k(nsamples, seed, seqlen, model):
    from datasets import load_dataset
    from transformers import AutoTokenizer
    import random

    # load gsm8k dataset
    traindata = load_dataset('gsm8k', 'main', split='train')
    testdata = load_dataset('gsm8k', 'main', split='test')

    # initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # set seed
    random.seed(seed)

    # prepare dataset for training
    trainloader = []
    for _ in range(nsamples):
        i = random.randint(0, len(traindata) - 1)
        encoded = tokenizer(traindata[i]['question'], return_tensors='pt', padding="max_length", truncation=True, max_length=seqlen)
        inp = encoded.input_ids
        tar = inp.clone()
        tar[:, :-1] = -100
        trainloader.append((inp, tar))

    # prepare dataset for test
    test_tokens = []
    for i in range(len(testdata)):
        encoded = tokenizer(testdata[i]['question'], return_tensors='pt', padding="max_length", truncation=True, max_length=seqlen)
        test_tokens.append(encoded.input_ids)

    # converting the list of tensors into a single tensor and wrapping it in a dictionary
    test_tokens_tensor = torch.cat(test_tokens, dim=0)
    test_data_dict = {'input_ids': test_tokens_tensor}

    return trainloader, test_data_dict

@lru_cache
def get_mmlu(nsamples, seed, seqlen, model):
    from datasets import load_dataset
    from transformers import AutoTokenizer
    import random

    # load mmlu dataset
    traindata = load_dataset('mmlu', 'main', split='train')
    testdata = load_dataset('mmlu', 'main', split='test')

    # initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # set seed
    random.seed(seed)

    # prepare dataset for training
    trainloader = []
    for _ in range(nsamples):
        i = random.randint(0, len(traindata) - 1)
        encoded = tokenizer(traindata[i]['question'], return_tensors='pt', padding="max_length", truncation=True, max_length=seqlen)
        inp = encoded.input_ids
        tar = inp.clone()
        tar[:, :-1] = -100
        trainloader.append((inp, tar))

    # prepare dataset for test
    test_tokens = []
    for i in range(len(testdata)):
        encoded = tokenizer(testdata[i]['question'], return_tensors='pt', padding="max_length", truncation=True, max_length=seqlen)
        test_tokens.append(encoded.input_ids)

    # converting the list of tensors into a single tensor and wrapping it in a dictionary
    test_tokens_tensor = torch.cat(test_tokens, dim=0)
    test_data_dict = {'input_ids': test_tokens_tensor}

    return trainloader, test_data_dict

@lru_cache
def get_loaders(
    name, nsamples=128, seed=0, seqlen=2048, model=''
):
    if 'wikitext2' in name:
        return get_wikitext2(nsamples, seed, seqlen, model)
    if name == 'mmlu':
        return get_mmlu(nsamples, seed, seqlen, model)[1]['input_ids']
    if name == 'gsm8k':
        return get_gsm8k(nsamples, seed, seqlen, model)[1]['input_ids']
    if 'ptb' in name:
        if 'new' in name:
            return get_ptb_new(nsamples, seed, seqlen, model)
        return get_ptb(nsamples, seed, seqlen, model)
    if 'c4' in name:
        if 'new' in name:
            return get_c4_new(nsamples, seed, seqlen, model)
        return get_c4(nsamples, seed, seqlen, model)


@lru_cache
def get_test_tokens(
    name, seed=0, seqlen=2048, model=''
):
    train_samples = 0
    if name == 'wikitext2':
        return get_wikitext2(train_samples, seed, seqlen, model)[1]['input_ids']
    elif name == 'gsm8k':
        return get_gsm8k(train_samples, seed, seqlen, model)[1]['input_ids']
    elif name == 'ptb':
        return get_ptb_new(train_samples, seed, seqlen, model)[1].input_ids
    elif name == 'c4':
        return get_c4_new(train_samples, seed, seqlen, model)[1].input_ids
    else:
        raise Exception
