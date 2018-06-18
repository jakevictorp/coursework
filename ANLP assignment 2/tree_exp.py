#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 15:04:22 2017

@author: s1680791
"""
import nltk




ps = '''


(S((Simp((VP, \'(VP((VPt, \\\'(VPt((Vt(Book)))((NP((NP0, \\\\\\\'(NP0((NP0((NP1, "(NP1((Det(a)))((N2sc((Nsc, \\\\\\\\\\\\\\\'(Nsc(flight))\\\\\\\\\\\\\\\')))))"))))((PP((Prep(to)))((NP((PropN, \\\\\\\\\\\\\\\'(PropN(NYC))\\\\\\\\\\\\\\\')))))))\\\\\\\')))))\\\')))\'))))(.))')


'''

clean_ps = ps.replace("'",'').replace('"','').replace(',','').replace('\\','')
print('The cleaned up string is: \n', clean_ps)

openbrac = 0
closedbrac = 0
for letter in clean_ps:
    if letter == '(':
        openbrac += 1
    if letter == ')':
        closedbrac += 1
print('The numer of ( is: ', openbrac)
print('The numer of ) is: ', closedbrac)


cleanlist = clean_ps.split()
while closedbrac > openbrac:
    openbrac += 1
    cleanlist.insert(0,'(')
    
    
while openbrac > closedbrac:
    closedbrac += 1
    cleanlist.insert(-1,')')

final_clean_ps = ''.join(cleanlist)

print('The FINAL cleaned up string is: \n', final_clean_ps)



tree = nltk.tree.Tree.fromstring('''
                                 ((S ((Sdecl ((NP ( (PropN (PropN (John ))))))((VP ((VPdt (VPdt ((VPio ((VtVdt (gave )))((NP ( (PropN (PropN (Mary ))))))))((NP ((NP0 (NP0 ((NP1 (NP1 ((Det (a )))((N2sc ((Adj (nice )))((N2sc ((N3 ((N (N2sc ((Nsc (NscAdj (drawing )))))))))((NscVt (book ))))))))))))))))))))))(. )))
''')
tree.draw()
