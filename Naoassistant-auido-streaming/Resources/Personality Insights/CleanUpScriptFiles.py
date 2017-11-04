from collections import Counter

pathToFile = "Game of Thrones Scripts/Character Scripts/"

person = input("Enter name of person's script to be cleaned up (remember to include quotation marks around the name, and make the names capitalised!!!!): ")

firstname = person.split(' ')[0]

fullPath = pathToFile + person

with open(fullPath + '.txt', 'r') as textFile:
    contents =textFile.read()
    new_contents = contents.replace('\n', ' ')
    new_contents = new_contents.replace(person + ':', '')
    new_contents = new_contents.replace(firstname + ':', '')
    new_contents = new_contents.replace(firstname.upper() + ':', '')

with open(fullPath + "_clean.txt", 'w') as newfile:
    newfile.write(new_contents)

with open(fullPath + "_clean.txt", 'r') as textFile:
    words = [word for line in textFile for word in line.split()]
    print "The total word count is:", len(words)
