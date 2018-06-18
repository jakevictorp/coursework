#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 12:51:31 2017

@author: s1680791
"""

import sys,re
import nltk
from collections import defaultdict
import cfg_fix
from cfg_fix import parse_grammar, CFG
from pprint import pprint
# The printing and tracing functionality is in a separate file in order
#  to make this file easier to read
from cky_print import CKY_pprint, CKY_log, Cell__str__, Cell_str, Cell_log

class CKY:
    """An implementation of the Cocke-Kasami-Younger (bottom-up) CFG recogniser.

    Goes beyond strict CKY's insistance on Chomsky Normal Form.
    It allows arbitrary unary productions, not just NT->T
    ones, that is X -> Y with either Y -> A B or Y -> Z .
    It also allows mixed binary productions, that is NT -> NT T or -> T NT"""

    def __init__(self,grammar):
        '''Create an extended CKY processor for a particular grammar

        Grammar is an NLTK CFG
        consisting of unary and binary rules (no empty rules,
        no more than two symbols on the right-hand side

        (We use "symbol" throughout this code to refer to _either_ a string or
        an nltk.grammar.Nonterminal, that is, the two thinegs we find in
        nltk.grammar.Production)

        :type grammar: nltk.grammar.CFG, as fixed by cfg_fix
        :param grammar: A context-free grammar
        :return: none'''

        self.verbose=False
        assert(isinstance(grammar,CFG))
        self.grammar=grammar
        # split and index the grammar
        self.buildIndices(grammar.productions())

    def buildIndices(self,productions):
        ''' Postcondition: The "defaultdict"s (subclasses of dictionaries that
        call a factory function attribute) ‘unary’ and ‘binary’ are created and
        populated with unary and binary productions from NLTK. The defaultdict 
        subclass is an optimal data structure because it can create a 
        dictionary, as in this case, where the values are stored as lists. 
        When populating the CKY matrix, the left-hand-side rules need to be 
        looked up quickly to see what right-hand-side rule(s) they map to. 
        So the keys are RHSs because looking up a dictionary key is extremely 
        fast. 

        How: 

        Create two specialised container datatypes i.e defaultdicts to store 
        the production rules, one for unary rules and one for binary rules. 
        Ensure the “rhs” has a length of one or two. If the length of “rhs”
        for a production is equal to one, append it as the key with it’s 
        associated “lhs” symbol as the value in the dictionary self.unary. 
        If the length of “rhs” for a production is equal to two, append it as 
        the key with its “lhs” symbol as the value in the dictionary 
        self.binary.

        :type productions: nltk.grammar.Production
        :param productions: A binary or unary CFG rule
        :return: none        
               
        '''
        
        self.unary=defaultdict(list)
        self.binary=defaultdict(list)
        for production in productions:
            rhs=production.rhs()
            lhs=production.lhs()
            assert(len(rhs)>0 and len(rhs)<=2)
            if len(rhs)==1:
                self.unary[rhs[0]].append(lhs)
            else:
                self.binary[rhs].append(lhs)

    def parse(self,tokens,verbose=False):
        '''Postcondition: A matrix has been initialized and filled using the
        CKY algorithm and a complete parse has been generated. 
        
        How: Define "words" as the list of tokens in the input string. Define 
        "n" as the number of tokens plus 1. Initialize an empty matrix and 
        iteratively add n-1 rows and n columns. Call unaryFill() to fill the
        cells with all possible unary productions. Call binaryScan() to fill
        the cells with all possible binary productions. Return whether or not 
        the starting symbol (the first listed rule in the grammar) is in the
        matrix, indicating that the input string can be parsed according to 
        the grammar.
        
        :type tokens: list(str)
        :param tokens: The list of tokens (as strings) used to build the 
            matrix.
        :type verbose: bool
        :param verbose: show debugging output if True, defaults to False
        :rtype: bool
        :return: True if the CKY recognizer recognizes some valid parse for 
            the input string, otherwise False

        '''
        
        self.verbose=verbose
        self.words = tokens
        self.n = len(self.words)+1
        self.matrix = []
        # We index by row, then column
        #  So Y below is 1,2 and Z is 0,3
        #    1   2   3  ...
        # 0  .   .   Z
        # 1      Y   .
        # 2          .
        # ...
        for r in range(self.n-1):
             # rows
             row=[]
             for c in range(self.n):
                 # columns
                 if c>r:
                     # This is one we care about, add a cell
                     row.append(Cell(r,c,self))
                 else:
                     # just a filler
                     row.append(None)
             self.matrix.append(row)
        self.unaryFill()
        self.binaryScan()
        self.firstTree()
        start_sym_in_matrix = self.grammar.start() in self.matrix[0][self.n-1].labels()
        if start_sym_in_matrix == True:
            print('Number of successful analyses: ', len(self.matrix[0][self.n-1].labels()), '\n')
        else:
            return False

    def unaryFill(self):
        ''' Postcondition: The middle cells of the matrix are filled moving 
        along the diagonal from the top left to the bottom right with words 
        and corresponding unary non-terminals.
      
        How: Iterate over the length of the input string. Add word 
        corresponding to cell. Add the non-terminal symbol associated with the
        word to the cell by looking up the word in the self.unary dictionary.

         '''
         
        for r in range(self.n-1):
            cell=self.matrix[r][r+1]
            word=self.words[r]
            cell.addLabel(word)

    def binaryScan(self):
        '''(The heart of the implementation.)

Postcondition: the matrix has been filled with all constituents that
can be built from the input words and grammar.

How: Starting with constituents of length 2 (because length 1 has been
done already), proceed across the upper-right diagonals from left to
right and in increasing order of constituent length. Call maybeBuild
for each possible choice of (start, mid, end) positions to try to
build something at those positions.

        '''
        for span in range(2, self.n):
            for start in range(self.n-span):
                end = start + span
                for mid in range(start+1, end):
                    self.maybeBuild(start, mid, end)
                    
                    
                    
    def firstTree(self):
        
         '''Postcondition: A complete parse tree is printed based on the traces 
             derived from the CKY parser
        
        How: Convert the last cell (containing a start symbol 'S') in the matrix to a string.
            Process and clean the string to extract only the string in bracket form that nltk.tree.Tree.fromstring() 
            will accept to build a parse tree. Pass the string to the nltk.tree.Tree.fromstring() tool and then,
            optionally, use the tree.draw() tool from NLTK to draw the parse tree.
        
        '''
         #isolate the final cell of the CKY matrix as a string
         lastcell=self.matrix[0][self.n-1]
         strls = str(Cell.labels(lastcell))

         #extract only the first parse string
         lift_ps = strls.split('(S, \'', 3)
         just_ps_with_extra_comma = lift_ps[1]
         just_ps = just_ps_with_extra_comma[:-2]

         #clean up the parse string of excess punctuation and ensure it has the correct number of parentheses
         clean_ps = just_ps.replace("'",'').replace('"','').replace(',','').replace('\\','')

         openbrac = 0
         closedbrac = 0
         for letter in clean_ps:
             if letter == '(':
                 openbrac += 1
             if letter == ')':
                 closedbrac += 1

         cleanlist = clean_ps.split()
         while closedbrac > openbrac:
             openbrac += 1
             cleanlist.insert(0,'(')
    
         while openbrac > closedbrac:
             closedbrac += 1
             cleanlist.insert(-1,')')
         final_clean_ps = ''.join(cleanlist)

         #print out the derived parse
         tree = nltk.tree.Tree.fromstring(final_clean_ps)
         #To display full parse trees in a separate window, uncomment the line below
         #tree.draw()
         print(tree.pprint())
         return tree
         
         



    def maybeBuild(self, start, mid, end):
        '''Postcondition: The matrix has been populated with all possible 
        binary productions and a sub-tree and a Label.tracetup instance have been generated
        
        How: Set s1 to the Label.tracetup in cell (start, mid). Set s2 to the 
        Label.tracetup in cell (mid, end). If there is a RHS (s1[0], s2[0]) in the
        binary dictionary, add the corresponding LHS nonterminal to cell 
        (start, end). If s is the RHS of a unary rule, call the unaryUpdate() 
        function to add the corresponding LHS to cell (start, end).
        Generate a new sub-tree 'parse_string_bin' and combine it with the RHS non-terminal 's' to
        create a new Label.tracetup instance 'newLabel'.
        
        :type start: int
        :param start: the beginning position of the token span in question
        :type mid: int
        :param mid: some position in the token span in question between start 
            and end
        :type end: int
        :param end: the final position of the token span in question
        :return: none
        
        '''
        
        self.log("%s--%s--%s:",start, mid, end)
        cell=self.matrix[start][end]
        for s1 in self.matrix[start][mid].labels():
            for s2 in self.matrix[mid][end].labels():
                if (s1[0],s2[0]) in self.binary:
                    for s in self.binary[(s1[0],s2[0])]:
                        self.log("%s -> %s %s", s, s1, s2, indent=1)
                        
                        #derive sub-tree (in bracket form) for current rule expansion
                        parse_string_bin = ('(' + str(s) +'(' + str(s1[-1]) + ')(' + str(s2[-1]) + '))')
                        #create new Label.tracetup object from generated non-terminal and current sub-tree
                        newLabel = Label.tracetup(s, parse_string_bin)
                        #pass the Label.tracetup instance 'newLabel' to addLabel() to append the whole tuple to the cell
                        cell.addLabel(newLabel)
                        

# helper methods from cky_print
CKY.pprint=CKY_pprint
CKY.log=CKY_log

class Cell:
    '''A cell in a CKY matrix'''
    def __init__(self,row,column,matrix):
        self._row=row
        self._column=column
        self.matrix=matrix
        self._labels=[]

    def addLabel(self,label):
        if label in self._labels:
            pass
        else: 
            self._labels.append(label)
            self.unaryUpdate(label)
        

    def labels(self):
        return self._labels


    def unaryUpdate(self,symbol,depth=0,recursive=False):
        ''' Postcondition: Cells in the matrix containing either words
        or Label.tracetup instances that are RHSs of a unary rule are expanded and the
        corresponding LHS are added to the cell.

        How: Add word (terminal symbol) to cell. If the word is in the 
        dictionary self.unary, add the corresponding LHS (parent symbol) as a Label.tracetup instance to 
        the cell. If the parent symbol is in the dictionary self.unary, add
        its respective parent symbol and Label.tracetup instance to the cell, recursively.

        :type symbol: str OR Label.tracetup
        :param symbol: the word or Label.tracetup that will be passed through to find the
                related unary rule(s)
        :return: none
       
        '''
        if not recursive:
            self.log(str(symbol),indent=depth)
        #this section applied to words (terminal symbols) because the symbol will be passed  to the function in the first stage
        #of filling in the matrix
        if symbol in self.matrix.unary:
            parse_string = ('(' + str(self.matrix.unary[symbol]).strip('[').strip(']') + '(' + str(symbol) + '))')
            for parentsym in self.matrix.unary[symbol]:
                parent = Label.tracetup(parentsym,parse_string)
                #maybe come back and address the symbol argument below
                self.matrix.log("%s -> %s",parent,symbol,indent=depth+1)
                self.addLabel(parent)
                #MAYBE CHANGE BELOW TO parent[0]
                self.unaryUpdate(parent,depth+1,True)
        #this section deals with non-terminals because now 'symbol' is being pass in as the complex tuple Label.tracetup
        #so the first element of symbol (symbol[0]) is the actual non-terminal symbol, which is used to generate the parentsym,
        #which is ONE of the non-terminals in the lhs of the rule. The whole 'symbol' is used to construct the sub-tree at this
        #stage. The the parentsym and the current sub-tree are used to construct the 'parent' instance of Label.tracetup, which
        #is passed back into the unaryUpdate method as well as the addLabel method.
        elif symbol[0] in self.matrix.unary:
            if ',' in str(self.matrix.unary[symbol[0]]).strip('[').strip(']'):
                no_comma_in_lhs = str(self.matrix.unary[symbol[0]]).strip('[').strip(']').split(',')
                for non_term in no_comma_in_lhs:
                    parse_string = ('(' + str(non_term) + '(' + str(symbol) + '))')
                    for parentsym in self.matrix.unary[symbol[0]]:
                        parent = Label.tracetup(parentsym,parse_string)
                        self.matrix.log("%s -> %s",parent,symbol,indent=depth+1)
                        self.addLabel(parent)
                        self.unaryUpdate(parent,depth+1,True)
            else:
                parse_string = ('(' + str(self.matrix.unary[symbol[0]]).strip('[').strip(']') + '(' + str(symbol) + '))')
                for parentsym in self.matrix.unary[symbol[0]]:
                    parent = Label.tracetup(parentsym,parse_string)
                    self.matrix.log("%s -> %s",parent,symbol,indent=depth+1)
                    self.addLabel(parent)
                    self.unaryUpdate(parent,depth+1,True)

# helper methods from cky_print
Cell.__str__=Cell__str__
Cell.str=Cell_str
Cell.log=Cell_log

class Label:
    '''A label for a substring in a CKY chart Cell

    Includes a terminal symbol, non-terminal symbol, or tracetup, which is a tuple
    containing a non-terminal symbol and a trace in the form of a sub-tree.
    '''
    def __init__(self,symbol, trace=None):
        '''Create a label from a symbol and its child nodes
        :type symbol: a string (for terminals) or an nltk.grammar.Nonterminal
        :param symbol: a terminal or non-terminal
        '''
        self._symbol=symbol


    def __str__(self):
        return str(self._symbol)

    def __eq__(self,other):
        '''How to test for equality -- other must be a label,
        and symbols have to be equal'''
        assert isinstance(other,Label)
        return self._symbol==other._symbol

    def tracetup(symbol, trace):
        '''Postcondition: A tuple object has been created with prespecified elements. 
        
        How: Take two arguments, store as a tuple.
        
        :type symbol: str OR nltk.grammar.nonTerminal
        :param symbol: The highest node in the subtree at some point in parsing
        :type trace: str
        :param trace: a string that represents the bracket form of a sub-tree
        :rtype: tuple(str OR nltk.grammar.nonTerminal, str)
        :return: a tuple that logs the highest node at some stage in parsing and the most developed sub-tree

        '''
        tracetup = (symbol, trace)
        
        return tracetup