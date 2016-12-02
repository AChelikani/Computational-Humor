import pronouncing

def editDistance(str1, str2):
    '''
    Uses Wagner-Fischer algorithm to find the edit distance between two strings.
    '''
    m = len(str1)
    n = len(str2)
    # dists[i, j] is the edit distance between str1[:i] and str2[:j].
    dists = [[-1 for i in range(n + 1)] for j in range(m + 1)]

    # The distance between a non-empty string and an empty string is the length
    # of the non-empty string.
    for i in range(m + 1):
        dists[i][0] = i
    for j in range(n + 1):
        dists[0][j] = j

    for j in range(1, n + 1):
        for i in range(1, m + 1):
            if str1[i - 1] == str2[j - 1]:
                dists[i][j] = dists[i - 1][j - 1]           # no operation
            else:
                dists[i][j] = min(dists[i - 1][j] + 1,      # deletion
                                  dists[i][j - 1] + 1,      # insertion
                                  dists[i - 1][j - 1] + 1)  # substitution

    return dists[m][n]

# Create a mapping from each consonant to the corresponding digit for Soundex
# coding.
__replacements = {}
for i, e in enumerate([['b', 'f', 'p', 'v'], ['c', 'g', 'j', 'k', 'q', 's', 'x', 'z'], ['d', 't'], ['l'], ['m', 'n'], ['r']]):
    for char in e:
        __replacements[char] = str(i + 1)

def __soundex(str1):
    '''
    Finds the Soundex code of a string.
    '''
    first = str1[0]

    # Remove all occurrences of 'h' and 'w'.
    str1 = str1.replace('h', '')
    str1 = str1.replace('w', '')

    # Replace all consonants with the appropriate digits.
    for rep in __replacements:
        if rep in str1:
            str1 = str1.replace(rep, __replacements[rep])

    # Replace all adjacent same digits with one digit.
    j = 0
    for i in range(1, len(str1)):
        if str1[j] == str1[j - 1]:
            str1 = str1[:j] + str1[j + 1:]
        else:
            j += 1

    # Remove all vowels except the first.
    str2 = str1[1:]
    for vowel in ['a', 'e', 'i', 'o', 'u', 'y']:
        str2 = str2.replace(vowel, '')
    str1 = first + str2

    # Capitalize the first letter and make sure that the first character
    # is not a digit.
    str1 = first.upper() + str1[1:]

    # Make sure the code is valid.
    str1 += "000"
    str1 = str1[:4]

    return str1


def soundexDistance(str1, str2):
    '''
    Finds the edit distance of the Soundex codes of two strings.
    '''
    return editDistance(__soundex(str1), __soundex(str2))

def editSimilarity(str1, str2):
    '''
    Finds the relative edit distance between two strings.
    '''
    dist = editDistance(str1, str2)
    scale = max(len(str1), len(str2))
    return float(dist) / scale

def pronunciationSimilarity(str1, str2):
    '''
    Finds the relative edit distance of the phones of two strings.
    '''
    try:
        pronunciation1 = pronouncing.phones_for_word(str1.lower())
        pronunciation2 = pronouncing.phones_for_word(str2.lower())

        phones1 = pronunciation1[0].split()
        phones2 = pronunciation2[0].split()
        
        return editSimilarity(phones1, phones2)
    except:
        return 1

def wordEquality(str1, str2):
    '''
    Determines whether two words are the same.
    '''
    str1 = str1.lower()
    str2 = str2.lower()

    return str1 == str2 \
           or (str1 == str2 + 'd' or str1 == str2 + 's') \
           or (str2 == str1 + 'd' or str2 == str1 + 's')
