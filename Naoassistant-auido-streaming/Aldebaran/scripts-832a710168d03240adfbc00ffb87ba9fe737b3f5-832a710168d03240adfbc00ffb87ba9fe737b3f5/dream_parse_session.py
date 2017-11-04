


def analyseSessions():
    """
    Read a file containing lines formatted like that: "2;Guess sports; 2;Electro Swing; 1;Spooky Dance"
    """
    strFile = "C:/Users/amazel/Downloads/sessions.txt"
    
    file = open(strFile)
    lines = file.read().split("\n")
    file.close()
    dictAllGames = {} # for each name the number of occurence
    nTotal = 0
    for line in lines:
        #~ print( "line: %s" % line )
        if len(line) < 4:
            continue
        line = line.replace( "Twinkle; Twinkle Little Star", "Twinkle" )
        line = line.replace( "Rain; Rain Go Away", "Rain" )
        line = line.replace( "'", "" )
        stats = line.split(";")
        i = 0
        while i < len(stats):
            nbr = int(stats[i])
            i += 1
            name = stats[i]
            i += 1
            if name not in dictAllGames.keys():
                dictAllGames[name] = 0
            dictAllGames[name] += nbr
            nTotal += nbr
    print dictAllGames
    print( "nTotal: %s" % nTotal )
    for k,v in sorted(dictAllGames.iteritems(), key=lambda tup:tup[1], reverse=True ):
        print( "%-40s %5s" % (k,v) )
    
    # generate a google script line "var rowsData = [['Plants', 'Animals'], ['Ficus', 'Goat'], ['Basil', 'Cat'], ['Moss', 'Frog']]"
    strOut = "var rowsData = [['Game Name', 'Launch Times'], "
    for k,v in sorted(dictAllGames.iteritems(), key=lambda tup:tup[1], reverse=True ):
        strOut += "['%s','%s'], " % (k,v)
    strOut += "];"
    print strOut + "\n"
        
# analyseSessions - end
            
analyseSessions()