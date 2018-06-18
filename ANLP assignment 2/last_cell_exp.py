#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  4 15:55:13 2017

@author: s1680791
"""



wholecell = '''

[(S, '(S((Sq((Swhadv, \'(Swhadv((WhAdv(Why)))((Sqyn((Aux(did)))((Sdecl((NP((PropN, \\\'(PropN(John))\\\'))))((VP((VPt, \\\'(VPt((Nsc, Vt(book)))((NP((NP0, \\\\\\\'(NP0((NP1, "(NP1((Det(the)))((N2sc((Nsc, \\\\\\\\\\\\\\\'(Nsc(flight))\\\\\\\\\\\\\\\')))))")))\\\\\\\')))))\\\')))))))))\'))))(?))'), (S, '(S((Sq((Swhadv, \'(Swhadv((WhAdv(Why)))((Sqyn((Aux(did)))((Sdecl((NP((PropN, \\\'(PropN(John))\\\'))))((VP((VPt, \\\'(VPt((Nsc, Vt(book)))((NP((NP0, \\\\\\\'(NP0((NP1, "(NP1((Det(the)))(( N((Nsc, \\\\\\\\\\\\\\\'(Nsc(flight))\\\\\\\\\\\\\\\')))))")))\\\\\\\')))))\\\')))))))))\'))))(?))')] 


'''

lift_ps = wholecell.split('(S, \'', 3)

just_ps_with_extra_comma = lift_ps[1]
just_ps = just_ps_with_extra_comma[:-2]


print(lift_ps)

print('\n', just_ps)



#
#just_ps = re.compile(r'                  [\(S, \'(?P<parsestring>\(S\(\(.*)(?P<notneeded>[\(, \(S, \'\(S\()*.*])')
#g = just_ps.search(wholecell)
