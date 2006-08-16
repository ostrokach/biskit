##
## Biskit, a toolkit for the manipulation of macromolecular structures
## Copyright (C) 2004-2005 Raik Gruenberg & Johan Leckner
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You find a copy of the GNU General Public License in the file
## license.txt along with this program; if not, write to the Free
## Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##
##
## $Revision$
## last $Author$
## last $Date$

"""
PDBModel with attached Xplor topology (PSF).
"""

## PCRModel:
## collect and manage information about a ligand or receptor conformation
## generated by (PCR)MD

import os.path

import tools as t
from PDBModel import PDBModel


class PCRModel( PDBModel ):
    """
    PDBModel with attached Xplor topology (PSF).
    Creates more problems than it solves...
    """

    def __init__(self, fPsf=None, source=None, pdbCode=None, **params):
        """
        @param fPsf: file name of psf
        @type  fPsf: str
        @param source: file name of pdb OR PDBModel instance
        @type  source: str | PDBModel
        @param pdbCode: if None, first 4 letters of filename will be used
        @type  pdbCode: str
        """
        PDBModel.__init__( self, source=source, pdbCode=pdbCode, **params )

        if fPsf: fPsf = t.absfile( fPsf )

        ## in case given fPDB is already a PCRModel, keep psfFileName
        self.psfFileName = fPsf or getattr( source, 'psfFileName', None)

        ## version as of creation of this object
        self.initVersion = self.version()


    def version( self ):
        return PDBModel.version(self) + '; PCRModel $Revision$'


    def getPsfFile(self):
        """
        @return: file name
        @rtype: str
        """
        return self.psfFileName


    def take(self, i, deepcopy=0 ):
        r = PDBModel.take( self, i, deepcopy )
        r.psfFileName = self.psfFileName
        r.initVersion = self.initVersion
        return r


    def concat(self, *models ):
        r = PDBModel.concat( self, *models )
        r.psfFileName = self.psfFileName
        r.initVersion = self.initVersion
        return r


#############
##  TESTING        
#############
        
class Test:
    """
    Test class
    """
    

    def run( self ):
        """
        run function test

        @return: rmsd value
        @rtype:  float
        """
        print "Loading PDB..."

        m_com = PCRModel( t.testRoot() + "/com/1BGS.psf",
                          t.testRoot() + "/com/1BGS.pdb" )

        m_rec = PCRModel( t.testRoot() + "/rec/1A2P.psf",
                          t.testRoot() + "/rec/1A2P.pdb" )

        ## remove waters
        m_com = m_com.compress( m_com.maskProtein() )
        m_rec = m_rec.compress( m_rec.maskProtein() )

        ## fit the complex structure to the free receptor
        m_com_fit = m_com.magicFit( m_rec )

        ## calculate the rmsd between the original complex and the
        ## one fitted to the free receptor
        rms = m_com_fit.rms(m_com, fit=0)

        print 'Rmsd between the two complex structures: %.2f Angstrom'%rms
    
        return rms


    def expected_result( self ):
        """
        Precalculated result to check for consistent performance.

        @return: rmsd value
        @rtype:  float
        """
        return 58.784401345508634
    
        
if __name__ == '__main__':

    test = Test()

    assert abs( test.run() - test.expected_result() ) < 1e-8







