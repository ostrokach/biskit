#!/usr/bin/env python
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
## last $Author$
## last $Date$
## $Revision$

"""
List that blocks any modifications
"""

class FixedListError( Exception ):
    pass

class FixedList( list ):
    """
    List that blocks any modifications. Implementing lists must override
    fixed() to allow adding of items under some circumstances (like during
    creation of the list).
    """

    def fixed(self):
        """
        @return: if list is fixed and modifications are prohibited
        @rtype: true
        """
        return 1


    def __stop(self):
        """
        @raise FixedListError: if attempt to modify fixed list
        """
        if self.fixed():
            raise FixedListError("Attempt to modify fixed list.")

    def __setitem__(self, i, v ):
        self.__stop()
        super( FixedList, self).__setitem__( i, v )

    def __setslice__(self, i, j, v ):
        self.__stop()
        super( FixedList, self).__setslice__( i, j, v )

    def __add__( self, lst ):
        self.__stop()
        super( FixedList, self).__add__( lst )

    def __iadd__( self, lst ):
        self.__stop()
        super( GuardedList, self).__iadd__( lst )        

    def extend( self, lst ):
        self.__stop()
        super( FixedList, self).extend( lst )        

    def append( self, v ):
        self.__stop()
        super( FixedList, self).append( v )        

    def __delitem__(self, i ):
        self.__stop()
        super( FixedList, self).__delitem__( i )



#############
##  TESTING        
#############
        
class Test:
    """
    Test class
    """
    
    def run( self, raiseErr=0 ):
        """
        run function test

        @return: something
        @rtype:  float
        """
        list = range(10)

        f = FixedList( list )

        print 'f.fixed() is %i for a FixedList'% f.fixed()
        
        if raiseErr:
            f.append(6)
                
        return 1


    def expected_result( self ):
        """
        Precalculated result to check for consistent performance.

        @return: something
        @rtype:  float
        """
        return 1
    
        
if __name__ == '__main__':

    test = Test()

    assert  test.run( raiseErr=1 ) == test.expected_result()
    
