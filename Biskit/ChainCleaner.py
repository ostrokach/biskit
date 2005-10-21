##
## Biskit, a toolkit for the manipulation of macromolecular structures
## Copyright (C) 2004-2005 Raik Gruenberg & Johan Leckner; All rights reserved
##
## $Revision$
## last $Date$
## last $Author$
"""Fill in missing atoms, and report low occupancies"""

from ChainSeparator import ChainSeparator
from Scientific.IO.PDB import *
import tools as T

class ChainCleaner:
    """
    Take with each call to next() one chain from ChainSeparator;
    Return this chain with completed residues.
    """

    def __init__(self, chainSeparator):
        """
        Clean up separate chains.
        chainSeparator - ChainSeparator
        """
        self.reader = chainSeparator
        self.pdbname = self.reader.pdbname()   # take over pdb name
        self.log = self.reader.log             # take over log file
        
        self.aminoAcidDict = {'GLY':['N','CA','C','O'],
        'ALA':['N','CA','C','O','CB'],
        'VAL':['N','CA','C','O','CB','CG1','CG2'],
        'LEU':['N','CA','C','O','CB','CG','CD1','CD2'],
        'ILE':['N','CA','C','O','CB','CG1','CG2','CD1'],
        'MET':['N','CA','C','O','CB','CG','SD','CE'],
        'PRO':['N','CA','C','O','CB','CG','CD'],
        'PHE':['N','CA','C','O','CB','CG','CD1','CD2','CE1','CE2','CZ'],
        'TRP':['N','CA','C','O','CB','CG','CD1','CD2','NE1','CE2','CE3',
               'CZ2','CZ3','CH2'],
        'SER':['N','CA','C','O','CB','OG'],
        'THR':['N','CA','C','O','CB','OG1','CG2'],
        'ASN':['N','CA','C','O','CB','CG','OD1','ND2'],
        'GLN':['N','CA','C','O','CB','CG','CD','OE1','NE2'],
        'TYR':['N','CA','C','O','CB','CG','CD1','CD2','CE1','CE2','CZ','OH'],
        'CYS':['N','CA','C','O','CB','SG'],
        'LYS':['N','CA','C','O','CB','CG','CD','CE','NZ'],
        'ARG':['N','CA','C','O','CB','CG','CD','NE','CZ','NH1','NH2'],
        'HIS':['N','CA','C','O','CB','CG','ND1','CD2','CE1','NE2'],
        'ASP':['N','CA','C','O','CB','CG','OD1','OD2'],
        'GLU':['N','CA','C','O','CB','CG','CD','OE1','OE2'],
        'ACE':['CA', 'C', 'O'],
        'NME':['N', 'CA'] }


    def _res2Terminal(self, aName_list):
        """
        Tweak list of allowed atom names to one expected for a
        C-terminal residue.
        aName_list - list of strings, e.g. ['N','CA','C','O','CB']
        -> e.g. ['N','CA','C','OT1','CB','OT2']
        """
        result = []         # make local copy instead of taking reference
        result += aName_list
        try:
            result[result.index('O')] = 'OT1'
            result += ['OT2']
        except:
            pass  ## skip for CBX (Methyl amine)
        return result

    
    def _addMissing(self, residue, atom_name):
        """
        Add atom with given name to residue.
        residue - Scientific.IO.PDB.Residue
        atom_name - string
        """
        if len(atom_name) < 2:
            # Atom.__init__ complaints about 1-char names
            atom_name = atom_name + ' '
        # new atom, element property needed for correct alignment in file
        residue.atom_list.append( Atom(atom_name, Vector(0,0,0),\
                                      element=atom_name[0] ) )


    def _completeResidues(self, chain):
        """
        Look for missing or unknown atom names, add missing atoms,
        report unknown atoms.
        chain - Scientific.IO.PDB.PeptideChain
        -> Scientific.IO.PDB.PeptideChain
        """
        chain.deleteHydrogens() ## delete all hydrogens
        i = 0
        self.log.add("Checking atoms of chain "+chain.segment_id)

        for res in chain:
            try:
                if i < len(chain)-1:            # normal residue
                    alowed = self.aminoAcidDict[res.name]
                else:                           # c-terminal residue
                    alowed = self._res2Terminal(self.aminoAcidDict[res.name])

                name_list = []

                for atom in res.atom_list:      # check for unknown atom names
                    # store for missing atom check
                    name_list = name_list + [atom.name]
                    if not (atom.name in alowed):
                        self.log.add('\tunknown atom: ' + atom.name + ' : '+\
                                     res.name+ str(res.number))

                for name in alowed:              # check for missing atoms
                    if not (name in name_list):
                        # add missing atom with 0 xyz
                        self._addMissing(res, name)  
                        self.log.add('\tadded missing atom -> '+ name+ ' : '+\
                                     res.name+ str(res.number))
            
            except:
               s = "\ncompleteResidues(): Error while checking atoms.\n"
               s = s + "residue " + str(i)+ " :"+ str(res) + "\n"
               s = s + T.lastError()
               T.errWriteln(
                   "Error while completing residues, check log for details.")
               self.log.add(s)

            i = i+1
            
        return chain


    def _checkOccupancy(self, chain):
        """Check and report atoms with ocupancies that is not 100% 
        Scientific.PDB.IO will only take one of the atoms even if there are
        alternate locations indicated in the PDB-file. The code below does only
        check for none 100% occupancies and report them to the log-file."""
        self.log.add("Checking atom occupancies of chain "+chain.segment_id)
        for res in chain:
            for atom in res:
                if atom.properties.get('occupancy',1.0) != 1.0:
                    self.log.add('\tOccupancy: '+\
                                 str(atom.properties['occupancy']) \
                                 + ' : ' + atom.name + ' : '+ res.name+ ' ' +\
                                 str(res.number))
        return chain

    
    def _find_and_change(self, chain, oldAtomName, residueNum, newAtomName):
        """Change name of atoms in specified residue"""
        changeRes = chain.residues[residueNum]
        if changeRes.atoms.has_key(oldAtomName) == 1:
            changeRes.atoms[oldAtomName].name = newAtomName
        return chain

    
    def _correct_Cterm(self, chain):
        """Terminal amino acid can't have atom type O and OXT - have to be
        OT1 and OT2"""
        self._find_and_change(chain, 'O', -1, 'OT1')
        self._find_and_change(chain, 'OXT', -1, 'OT2')
        return chain


    def next(self):
        """
        Obtain next chain from ChainSeparator; Add missing atoms.
        -> Scientific.IO.PDB.PeptideChain, completed chain
        -> None, if no chain is left
        """
        chain = self.reader.next()
        if (chain == None):
            ## extract all waters into separate pdb
            self.reader.extractWaters( )

            return None
        self.log.add("\nCleaning up chain "+chain.segment_id+": ")

        # check for atoms that don't have 100% occupancy
        chain = self._checkOccupancy(chain) 

        # change OXT to OT2 and O to OT2 for C terminal
        chain = self._correct_Cterm(chain)  
        chain = self._completeResidues(chain)

        return chain

####################################
## TESTING
####################################

if __name__ == '__main__':

    
    fname =   T.testRoot() + '/com_wet/1BGS_original.pdb'
    outPath = T.testRoot() + '/com_wet'
    
    cleaner = ChainCleaner (ChainSeparator(fname, outPath) )

    print cleaner.next()
    
    print 'Wrote log: %s'%(cleaner.log.fname)
