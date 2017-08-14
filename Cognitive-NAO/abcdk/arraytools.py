# -*- coding: utf-8 -*-

###########################################################
# Aldebaran Behavior Complementary Development Kit
# Arraytools tools
# Aldebaran Robotics (c) 2010 All Rights Reserved - This file is confidential.
###########################################################

"Array tools"

# renammed from array to arraytools, to be more explicit.

print( "importing abcdk.arraytools" );

import random

import typetools


def dup( value ):
    """
    duplicate an array.
    The array won't be a copy of any other source value.
    No sub array will share data, it's different than copy.deepcopy ! (see below)
    """
    
    # end of recursivity
    if( not typetools.isArray( value ) ):
        # print( "value is not an array: %s" % str( value ) );
        return value;
        
    # in case of an array, we need to recreate a new one, and not a pointer on origin.
    newArray = [];
    for v in value:
        newArray.append( dup(v) );
    return newArray;
# dup - end

#~ val = [[[0,1,2],3,4],5,6];
#~ val2 = dup( val );
#~ val[0][0][0] = 153;
#~ val[2] = 154;
#~ print( "test dup: %s => %s" % ( str( val ), str( val2 ) ) );

#~ import copy
#~ aCorner = copy.deepcopy( [[0]*2]*4 );
#~ aCorner[0][1] = 3;
#~ print aCorner; # bad: 3 are copied in the four sub array! ouin!

#~ aCorner2 = dup( [[0]*2]*4 );
#~ aCorner2[0][1] = 3;
#~ print aCorner2; # good: 3 are copied only in the first array! yes!


def arrayCreate( nNewSize, value = 0 ):
    "create an array of size nNewSize by inserting some value (default 0)"
    "The array won't be a copy of any other source value"
    newArray = [];
    for i in range( nNewSize ):
        newArray.append( dup( value ) );
    return newArray;
# arrayCreate - end

#~ val = [[1,2,3],4,5];
#~ val2 =arrayCreate( 3, val );
#~ val[0][0] = 153;
#~ val[2] = 154;
#~ print( "test arrayCreate: %s => %s" % ( str( val ), str( val2 ) ) );

def convertToArray( value ):
    "convert any type of value to array"
    "eg: convertToArray( (0,1,3,(0,1,2)) ) => [0,1,3,[0,1,2] ]"
    newValue = [];
    for v in value:
        if( typetools.isIterable( v ) ): # will work even with exotic type <type 'numpy.ndarray'>
            newValue.append( convertToArray( v ) );
        else:
            newValue.append( v );
    return newValue;
# convertToArray - end

#~ val = (0,1,2,(3,4,(5,6,7)));
#~ val2 = convertToArray( val );
#~ print( "%s => %s" % ( str( val ), str( val2 ) ) );

def arraySum( anArray ):
    "compute the sum of an array"
    "assume all element of the array could be added each others"
    sum = 0;
    for val in anArray:
        sum += val;
    return sum;
# arraySum - end


def chooseOneElem( aList ):
    "Pick randomly an element in a list "
    "each list contains elements, and optionnal probability ratio (default is 1)"
    "exemple of valid list:"
    "     'hello' (a non list with only one element)"
    "     ['hello', 'goodbye']"
    "     ['sometimes', ['often',10] ] often will appears 10x more often than sometimes (statistically)"
    
    # simple case
    if( not typetools.isArray( aList ) ):
        return aList;
        
    # generate statistic repartition
    listProba = [];
    nSum = 0;
    for elem in aList:
        if( typetools.isArray( elem ) and len( elem ) > 1 ):
            nVal = elem[1];        
        else:
            nVal = 1; # default value        
        listProba.append( nVal );
        nSum += nVal;
    nChoosen = random.randint( 0, nSum - 1 );
#    logToChoregraphe( "nChoosen: %d / total: %d / total different: %d (list:%s)" % ( nChoosen, nSum, len( aList ) , aList ) );
    nSum = 0;
    nIdx = 0;
    for val in listProba:
        nSum += val;
        if( nSum > nChoosen ):
            elem = aList[nIdx];
            if( typetools.isArray( elem ) ):
                return elem[0];
            return elem;
        nIdx += 1;
        
    return "not found or error";
# chooseOneElem - end

def constructFromNamedArray(obj, aNamedArray ):
    "construct a python object from an array of couple [attr_name,attr_value]"
    "reverse of stringtools.dictionnaryToString ???"
    for attr_name, attr_value in aNamedArray:
        try:
            attr = getattr( obj, attr_name );
            if( attr != None ):
                # eval( "obj." + attr_name + " = '" + attr_value + "'" );
                setattr( obj, attr_name, attr_value );
        except BaseException, err:
            print( "WRN: constructFromNamedArray: ??? (err:%s)" % ( str( err ) ) );
            pass
  # for
#   print( dump( obj ) );
    return obj;
# constructFromNamedArray - end

def dictToArray( dico, bSort = False ):
    """
    Convert a dictionnary to an array [ [k1,value1], [k2,value2]... ]
    bSort: when set: sort the array by their value: bigger first
    v0.6
    """
    retVal = [];
    if( len( dico ) > 0 ):
        for k,v in dico.iteritems():
            if( typetools.isDict( v ) ):
                retVal.append( [k,dictToArray(v)] );
            else:
                retVal.append( [k,v] ) # modif laurent
                retVal.append( [k,v] ); 
        if( bSort ):
            retVal.sort(key=lambda a:a[1], reverse=True );
    return retVal;
# dictToArray - end

def arrayToDict( elements, bTreatsEmptyArrayAsDict = False ):
    """
    Convert a dictionnary to an array [ [k1,value1], [k2,value2]... ]
    - bTreatsEmptyArrayAsDict: when set [['a', []]] => {'a': {}} else it would be {'a': []}
    WARNING: it won't reconstruct original array on every case!
    """
    retVal = dict();
    for k, v in elements:
        #~ print( "k:%s, v: %s" % (k,v) );
        if( 
                        typetools.isArray( v ) 
                and  (
                            bTreatsEmptyArrayAsDict 
                            or 
                            ( 
                                    (len(v) > 0 ) 
                                and (
                                                typetools.isString( v[0] )  # first check it could be a key
                                            or typetools.isArray( v[0] )   # or if it's not a key, so it's a sub array
                                        )  
                            )
                        ) 
        ):
            #~ print( "v is array to dictable: %s" % str( v ) );
            v = arrayToDict( v );
            retVal[k] = v;
        else:
            if( not typetools.isString( k ) ):
                # in fact we're not in an array, aborting, and returning elements as before
                return elements;
            retVal[k] = v;
    return retVal;
# arrayToDict - end

#~ print dictToArray( { "a": 123 } );
#~ print arrayToDict( dictToArray( { "a": 123 } ) );
# print arrayToDict( ['a', 'b', 'c'] ); # will raise an error
#~ print dictToArray({"a":{}})

def simplifyArray( a ):
    """
    remove nested solitary element in an array and subarray
    - a: an array
    return a simplied array.
    eg: [[[178, 901]], [[177, 902]], [[177, 904]]] => [[178, 901], [177, 902], [177, 904]]
    """
    out = [];
    for elem in a:
        if( len(elem) == 1 and typetools.isArray(elem[0]) ):
            out.append( elem[0] );
        else:
            out.append( elem );
    return out;
# simplifyArray - end

#~ print( simplifyArray(  [[[178, 901]], [[177, 902]], [[177, 904]]] ) );

def listPointToTuple( listPoints ):
    """
    todo: clean and comment and test!
    """
    listOut = [];
    for i in range( 0, len( listPoints ), 2 ):
        ptx = listPoints[i];
        pty = listPoints[i+1];
        if( ptx != 0. or pty != 0. ):        
            listOut.append( (ptx, pty) );
    return listOut;
    
    
def convertTupleListAngleToImagePixels( listTupleAngles, w, h ):
    """
    todo: clean and comment and test!
    """
    
    listOut = [];
    for pt in listTupleAngles:
        listOut.append( ( (-int(pt[0]*w)+w/2),int(pt[1]*h)+h/2 ) );
    return listOut;

def convertAngleToImagePixels( x, y, w, h ):
    return ( (-int(x*w)+w/2),int(y*h)+h/2 );
    
def convertSizeToImagePixels( sx, sy, w, h ):
    return ( (int(sx*w)),int(sy*h) );


def autoTest():
    a = arrayCreate( 8, 2 );
    s = arraySum( a );
    assert( s == 16 );
    

    d = {"a": 123, "b": [1,2,3], "c": {"pomme": 2, "caca": 3}, "d": 12.3, "embedded2": {"train": {"nuage": 6, "soleil": 2} } };
    print( d );
    a = dictToArray( d );
    print( a );
    d2 = arrayToDict( a );
    print( d2 );
    assert( d2 == d );    
    
    assert( {} == arrayToDict(dictToArray({}) ) );

    d = {"a":{}};
    print( d );
    a = dictToArray( d );
    print( a );
    d2 = arrayToDict( a, bTreatsEmptyArrayAsDict = True );
    print( d2 );
    assert( d2 == d );    
    d2 = arrayToDict( a, bTreatsEmptyArrayAsDict = False );
    print( d2 );
    assert( d2 == {'a': []} );
    
    d = {1: {'P07': [[0.3211357075700192, 0.08681054247451304], [-0.9747738710942114, 0.22319475852269827]]}};
    print( d );
    a = dictToArray( d );
    print( a );
    d2 = arrayToDict( a );
    print( d2 );
    assert( d2 == d );
    
    
    print( "autoTest: ok" );
# autoTest - end

if( __name__ == "__main__" ):
    autoTest();
