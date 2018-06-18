from __future__ import division
from math import log,sqrt
import operator
from nltk.stem import *
from nltk.stem.porter import *
import matplotlib.pyplot as plt
from scipy import stats

STEMMER = PorterStemmer()

# Define the data structures used to store the counts:
o_counts = {}; # Occurrence counts
co_counts = {}; # Co-occurrence counts




# helper function to get the count of a word (string)
def w_count(word):
  return o_counts[word2wid[word]]

def tw_stemmer(word):
  '''Stems the word using Porter stemmer, unless it is a 
  username (starts with @).  If so, returns the word unchanged.

  :type word: str
  :param word: the word to be stemmed
  :rtype: str
  :return: the stemmed word

  '''
  if word[0] == '@': #don't stem these
    return word
  else:
    return STEMMER.stem(word)


def make_t_test(c_xy, c_x, c_y, N):
    root_of_indep_prob = sqrt(c_x*c_y)
    first_chunk = c_xy/root_of_indep_prob
    second_chunk = root_of_indep_prob/N
    t_test = first_chunk - second_chunk
    return t_test
    

#Do a simple error check using value computed by hand
if(make_t_test(2,4,3,12) != 0.288675134594813): # these numbers are from our y,z example
    print("Warning: make_t_test is incorrectly defined")
else:
    print("t-test check passed")

def cos_sim(v0,v1):
    
    '''
    Compute the cosine similarity between two sparse vectors.

  :type v0: dict
  :type v1: dict
  :param v0: first sparse vector
  :param v1: second sparse vector
  :rtype: float
  :return: cosine between v0 and v1
  '''
    unrooted0 = 0
    unrooted1 = 0
    vsum = 0  
    keys=v0.keys()&v1.keys()
 
    for id in keys:
        dot_product = (v0[id])*(v1[id])
        vsum += dot_product
    for id in v0:
        unrooted0 += v0[id]*v0[id]
    for id in v1:
        unrooted1 += v1[id]*v1[id]

    vlength = sqrt(unrooted0)*sqrt(unrooted1)
    normalised_cos_sim = vsum/(vlength)
    return normalised_cos_sim
   
        
        
        
        

def create_t_vectors(wids, o_counts, co_counts, tot_count):
    '''Creates context vectors for the words in wids, using PPMI.
    These should be sparse vectors.

    :type wids: list of int
    :type o_counts: dict
    :type co_counts: dict of dict
    :type tot_count: int
    :param wids: the ids of the words to make vectors for
    :param o_counts: the counts of each word (indexed by id)
    :param co_counts: the cooccurrence counts of each word pair (indexed by ids)
    :param tot_count: the total number of observations
    :rtype: dict
    :return: the context vectors, indexed by word id
    '''
    
    vectors = {}
    for targetid in wids:
        current_vector = {}
        targ_count = o_counts[targetid]
        keys = co_counts[targetid].keys()
        for other_wid in keys:
            other_count = o_counts[other_wid]

            cc = co_counts[targetid][other_wid]
            current_pmi = (make_t_test(cc,targ_count,other_count,tot_count))
            #this is excluding all negative and zero PMI values from our PPMI vector
            if current_pmi <= 0:
                pass
            else:
                current_vector[other_wid] = (make_t_test(cc,targ_count,other_count, tot_count))
            vectors[targetid] = current_vector


        
            
    return vectors

def read_counts(filename, wids):
  '''Reads the counts from file. It returns counts for all words, but to
  save memory it only returns cooccurrence counts for the words
  whose ids are listed in wids.

  :type filename: string
  :type wids: list
  :param filename: where to read info from
  :param wids: a list of word ids
  :returns: occurence counts, cooccurence counts, and tot number of observations
  '''
  o_counts = {} # Occurence counts
  co_counts = {} # Cooccurence counts
  fp = open(filename)
  N = float(next(fp))
  for line in fp:
    line = line.strip().split("\t")
    wid0 = int(line[0])
    o_counts[wid0] = int(line[1])
    if(wid0 in wids):
        co_counts[wid0] = dict([int(y) for y in x.split(" ")] for x in line[2:])
  return (o_counts, co_counts, N)

def get_spearman(x,y):
    return stats.spearmanr(x,y)

def print_sorted_pairs(similarities, o_counts, first=0, last=100):
  '''Sorts the pairs of words by their similarity scores and prints
  out the sorted list from index first to last, along with the
  counts of each word in each pair.

  :type similarities: dict 
  :type o_counts: dict
  :type first: int
  :type last: int
  :param similarities: the word id pairs (keys) with similarity scores (values)
  :param o_counts: the counts of each word id
  :param first: index to start printing from
  :param last: index to stop printing
  :return: none
  '''
  if first < 0: last = len(similarities)
  with open('c_sims_t_test.txt', 'w') as f:
      pair_freq = []
      word1_freq = []
      word2_freq = []
      pair_similarities = []
      f.write("The results of the cosine similarity computations are:")
      for pair in sorted(similarities.keys(), key=lambda x: similarities[x], reverse = True)[first:last]:
          
          word_pair = (wid2word[pair[0]], wid2word[pair[1]])
          #append the co-ocurrence of each word in the given pair
          pair_freq.append(co_counts[pair[0]][pair[1]])
          #append the corresponding similarity measure
          pair_similarities.append(similarities[pair])
          #append first word frequency
          word1_freq.append(o_counts[pair[0]])
          #append second word frequency
          word2_freq.append(o_counts[pair[1]])
          f.write("\n"+"{:.5f}\t{:30}\t{}\t{}\t{}".format(similarities[pair],str(word_pair),
                                             o_counts[pair[0]],o_counts[pair[1]], co_counts[pair[0]][pair[1]]))
          print("{:.5f}\t{:30}\t{}\t{}\t{}".format(similarities[pair],str(word_pair),
                                             o_counts[pair[0]],o_counts[pair[1]], co_counts[pair[0]][pair[1]]))
        
      f.write("\n\nThe Spearman correlation coefficient (and p-value) of the co-occurrence and similarities are: \n")
      f.write(str(get_spearman(pair_freq, pair_similarities)))
      f.write("\n\nThe Spearman correlation coefficient (and p-value) of the frequencies of the first words in the pairs and similarities are: \n")
      f.write(str(get_spearman(word1_freq, pair_similarities)))
      f.write("\n\nThe Spearman correlation coefficient (and p-value) of the frequencies of the second words in the pairs and similarities are: \n")
      f.write(str(get_spearman(word2_freq, pair_similarities)))

def min_freq_v_sim(sims):
  xs = []
  ys = []
  for pair in sims.items():
    ys.append(pair[1])
    c0 = o_counts[pair[0][0]]
    c1 = o_counts[pair[0][1]]
    xs.append(min(c0,c1))
  plt.clf() # clear previous plots (if any)
  ourplot = plt.figure()
  plt.xscale('log') #set x axis to log scale. Must do *before* creating plot
  plt.plot(xs, ys, 'k.') # create the scatter plot
  plt.xlabel('Min Freq')
  plt.ylabel('Similarity')
  plt.title('Minimum Frequency vs Similarity\n'+"Freq vs Similarity Spearman correlation = {:.2f}".format(stats.spearmanr(xs,ys)[0]))
  plt.show() #display the set of plots
  ourplot.savefig('T_test_c_sim_min.pdf')
  return ("\nFreq vs Similarity Spearman correlation = {:.2f}".format(stats.spearmanr(xs,ys)[0]))

  
  
def max_freq_v_sim(sims):
  xs = []
  ys = []
  for pair in sims.items():
    ys.append(pair[1])
    c0 = o_counts[pair[0][0]]
    c1 = o_counts[pair[0][1]]
    xs.append(max(c0,c1))
  plt.clf() # clear previous plots (if any)
  ourplot = plt.figure()
  plt.xscale('log') #set x axis to log scale. Must do *before* creating plot
  plt.plot(xs, ys, 'k.') # create the scatter plot
  plt.xlabel('Max Freq')
  plt.ylabel('Similarity')
  plt.title('Maximum Frequency vs Similarity\n'+"Freq vs Similarity Spearman correlation = {:.2f}".format(stats.spearmanr(xs,ys)[0])) 
  plt.show() #display the set of plots
  ourplot.savefig('T_test_c_sim_max.pdf')
  return ("\nFreq vs Similarity Spearman correlation = {:.2f}".format(stats.spearmanr(xs,ys)[0]))
  
  
  
def diff_in_freq_v_sim(sims):
  xs = []
  ys = []
  for pair in sims.items():
    ys.append(pair[1])
    c0 = o_counts[pair[0][0]]
    c1 = o_counts[pair[0][1]]
    xs.append(abs(c0 - c1))
  plt.clf() # clear previous plots (if any)
  ourplot = plt.figure()
  plt.xscale('log') #set x axis to log scale. Must do *before* creating plot
  plt.plot(xs, ys, 'k.') # create the scatter plot
  plt.xlabel('Difference in Frequency')
  plt.ylabel('Similarity')
  plt.title('Difference in Frequency vs Similarity\n'+"Freq vs Similarity Spearman correlation = {:.2f}".format(stats.spearmanr(xs,ys)[0]))
  plt.show() #display the set of plots
  ourplot.savefig('T_test_c_sim_diff.pdf')
  return ("\nDifference in Frequency vs Similarity Spearman correlation = {:.2f}".format(stats.spearmanr(xs,ys)[0]))


def make_pairs(items):
  '''Takes a list of items and creates a list of the unique pairs
  with each pair sorted, so that if (a, b) is a pair, (b, a) is not
  also included. Self-pairs (a, a) are also not included.

  :type items: list
  :param items: the list to pair up
  :return: list of pairs

  '''
  pair_list = []
  for x in items:
      for y in items:
          if x < y:
              if x in co_counts:
                  if y in co_counts[x]:
                      pair_list.append((x, y))
                  else:
                      pass
              else:
                  pass
          else:
              pass

  return pair_list

test_words = ['red', 'yellow', 'blue', 'green', 'orange', 'purple', 'pink', 'magenta', 'beige', 'crimson', 'fuchsia', 'amber', 'puce', 'black', 'white', 'grey', 'gray', 'indigo']
#test_words = ['cat', 'dog', 'computer', 'mouse', '@justinbieber']
#test_words = ['@britneyspears', 'aguilera', 'beyonc', 'rihanna', 'good', 'bad', 'excel', 'terribl', 'obama', 'biden']
stemmed_words = [tw_stemmer(w) for w in test_words]
all_wids = set([word2wid[x] for x in stemmed_words]) #stemming might create duplicates; remove them

# Load the data:
fp = open("/afs/inf.ed.ac.uk/group/teaching/anlp/lab8/counts", "r");
lines = fp.readlines();
N = float(lines[0]); # First line contains the number of observations.
for line in lines[1:]:
    line = line.strip().split("\t");
    wid0 = int(line[0]);
    if(wid0 in all_wids): # Only get/store counts for words we are interested in
        o_counts[wid0] = int(line[1]); # Store occurence counts
        co_counts[wid0] = dict([[int(y) for y in x.split(" ")] for x in line[2:]]); # Store co-occurence counts



# you could choose to just select some pairs and add them by hand instead
# but here we automatically create all pairs 
wid_pairs = make_pairs(all_wids)


#read in the count information
(o_counts, co_counts, N) = read_counts("/afs/inf.ed.ac.uk/group/teaching/anlp/asgn3/counts", all_wids)

#make the word vectors
vectors = create_t_vectors(all_wids, o_counts, co_counts, N)


# compute cosine similarites for all pairs we consider
c_sims = {(wid0,wid1): cos_sim(vectors[wid0],vectors[wid1]) for (wid0,wid1) in wid_pairs}


min_freq_v_sim(c_sims)
max_freq_v_sim(c_sims)
diff_in_freq_v_sim(c_sims)
print("Sort by cosine similarity")
print_sorted_pairs(c_sims, o_counts)

#with open('c_sims.txt', 'w') as f:
#    f.write(print_sorted_pairs(c_sims, o_counts))
#    print('Results from cosine similarity test:', file=f)
#    print_sorted_pairs(c_sims, o_counts)

