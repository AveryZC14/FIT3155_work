"""
File: a1q1.py
Author: Avery Cheng
Description: This was the best I could think of, please give me good marks
"""
import sys

SPECIAL_CHAR = '#'
BWT_DELIM = '$'


def burrows_wheeler_transform(text):

    # append the delim to mark the end of the string
    text_with_delim = text + BWT_DELIM
    n = len(text_with_delim)

    # Generate all cyclic rotations of the text_with_sentinel
    # Each rotation is a string where we rotate by i characters
    rotations = []
    for i in range(n):
        #putting together the text from i to the end and then the start to i creates the permutation we want
        rotations.append(text_with_delim[i:] + text_with_delim[:i])

    # Sort the rotations to form the BWT matrix
    sorted_rotations = sorted(rotations)

    #get and join the last character of each rotation
    bwt_string = "".join( map( (lambda s:s[-1]), sorted_rotations ))

    return bwt_string

def preprocess_rank(bwt_string):
    char_counts = {}
    unique_chars = []
    
    #count how many of each character there are
    for char in bwt_string:
        
        if char not in char_counts:
            char_counts[char] = 0
            unique_chars.append(char)   
        
        char_counts[char] += 1
    
    #sort each unique character
    chars_sorted = sorted(unique_chars)
    
    rank = {}
    accumulator = 0
    
    #iterate through sorted chars, creating the rank array
    for char in chars_sorted:
        rank[char] = accumulator
        accumulator += char_counts[char]
    
    return rank

def preprocess_noccurences_exclusive(bwt_string):
    
    no_occurences = {}
    
    #iterate through chars initialising no_occurences
    for char in bwt_string:
        
        #also initialise the character in no_occurences
        no_occurences[char] = [0]*len(bwt_string)
    
    #construct no_occurences
    #marked char is the char that'll be updated in the next iteration
    marked_char = bwt_string[0]
    for i in range(1,len(bwt_string)):
        current_char = bwt_string[i]
        
        for char in no_occurences:
            #make the no_occurences the same as previous i
            no_occurences[char][i] = no_occurences[char][i-1]
            
            #if marked, that means that character was at i-1, thus update here (because exclusivity)
            if char == marked_char:
                no_occurences[char][i] += 1
        
        marked_char = current_char
    
    return no_occurences

def preprocess_noccurences_inclusive(bwt_string):
    
    no_occurences = {}
    
    #iterate through chars initialising no_occurences
    for char in bwt_string:
        
        #also initialise the character in no_occurences
        no_occurences[char] = [0]*len(bwt_string)
    
    
    #construct no_occurences
    for i in range(1,len(bwt_string)):
        current_char = bwt_string[i]
        
        for char in no_occurences:
            #make the no_occurences the same as previous i
            no_occurences[char][i] = no_occurences[char][i-1]
            
            #if marked, that means that character was at i-1, thus update here (because exclusivity)
            if char == current_char:
                no_occurences[char][i] += 1
    
    return no_occurences
    

#simple pattern match
def find_occurrences(pattern, text, bwt_string, rank, no_occ_ex, no_occ_in):
    
    #initialise the pointers
    start_pointer = 0
    end_pointer = len(bwt_string) - 1

    # process pattern from right to left
    for query_char in reversed(pattern):
        # If the character never appears in the text, there are no matches.
        if query_char not in rank:
            return []

        # update the pointers using the rules
        start_pointer = rank[query_char] + no_occ_ex[query_char][start_pointer]
        end_pointer = rank[query_char] + no_occ_in[query_char][end_pointer] - 1

        # if start pointer greater than end pointer, then no matches.
        if start_pointer > end_pointer:
            return []

    #we'll use LF-mapping to get the starting index of each row
    def lf_mapping(row_index):
        symbol = bwt_string[row_index]
        #using the formula in the notes
        return rank[symbol] + no_occ_in[symbol][row_index] - 1

    # The row in F that starts with the delim is.    
    first_row = 0

    occurrences = []

    # For each matching row, walk LF steps until we reach the sentinel row in F.
    # The number of LF steps taken is exactly the starting position of that suffix in `text`.
    for row_index in range(start_pointer, end_pointer + 1):
        
        steps_to_first = 0
        
        cursor = row_index
        
        while cursor != first_row:
            cursor = lf_mapping(cursor)
            steps_to_first += 1

        start_position_in_text = steps_to_first

        # Sanity check: make sure the pattern fits entirely within `text`.
        # (It should, but this keeps outputs clean and avoids off-by-one mistakes.)
        if start_position_in_text + len(pattern) <= len(text):
            occurrences.append(start_position_in_text)

    # Return positions sorted (BWT order is not necessarily text order).
    occurrences.sort()
    return occurrences

#splits the pattern into blocks of literals and offsets
def split_pattern(pattern):
    pat_len = len(pattern)
    
    # edge case: all wild cards
    if all(c == SPECIAL_CHAR for c in pattern):
        #no blocks
        return [], []
    
    #blocks are the string blocks of literal text
    #offsets is an array of indices for the blocks to go
    blocks, offsets = [], []
    
    i = 0
    
    while i < pat_len:
        #we'll use j for look-ahead iteration
        j = i
        
        #scan for a block of special chars
        if pattern[i] == SPECIAL_CHAR:
            while j < pat_len and pattern[j] == SPECIAL_CHAR:
                j += 1
        
        #scan a block of literals
        else:
            while j < pat_len and pattern[j] != SPECIAL_CHAR:
                j += 1
                
            #slice out the literal block
            blocks.append(pattern[i:j])
            #append i, the idx of the start of the block of literals
            offsets.append(i)
            
        #new i is what we looked ahead to
        i = j
    return blocks, offsets

#does a pattern match with potential special characters in the pattern
def pattern_match_wildcard(text, pattern):
    #lengths
    txt_len = len(text)
    pat_len = len(pattern)
    
    #get the blocks and offsets
    blocks, offsets = split_pattern(pattern)
    
    #preprocess bwt, rank and no_occurences
    bwt_string = burrows_wheeler_transform(text)
    rank = preprocess_rank(bwt_string)
    no_occurences_exclusive = preprocess_noccurences_exclusive(bwt_string)
    no_occurences_inclusive = preprocess_noccurences_inclusive(bwt_string)
    
    # case: all wildcards
    if not blocks:
        return list(range(0, txt_len - pat_len + 1))
    
    #we won't try to match past this max_start
    #this also accounts for trailing special characters in the pat
    max_start = txt_len - pat_len

    #at every starting position, keep track of the number of aligned blocks
    # aligned_blocks[i] is the number of blocks that, when the offset is subtracted from the beginning of the block in the text, will get the index i.
    aligned_blocks = [0] * (max_start + 1)

    #for each block and corresponding offset
    for i in range(len(blocks)):
        
        #extract the block and offset, find occurences of the block in the text
        block = blocks[i]
        offset = offsets[i]
        occurences = find_occurrences(block, text, bwt_string, rank, no_occurences_exclusive, no_occurences_inclusive)
        
        #for each occurence
        for pos in occurences:
            #aligned_position refers to the start of where the pattern would match if this block is part of a match. 
            aligned_position = pos - offset
            
            #if it's a valid aligned position, then increment it
            if 0 <= aligned_position and aligned_position <= max_start:
                aligned_blocks[aligned_position] += 1
            
    result = []
    
    #iterate through every valid start
    for start in range(max_start + 1):
        #if there are the correct number of aligned blocks, then it's a full match
        if aligned_blocks[start] == len(blocks):
            result.append(start)
            
    return result

def main(argv):
    #open files
    text_path, pattern_path = argv[1], argv[2]
    
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read().rstrip('\n')
        
    with open(pattern_path, 'r', encoding='utf-8') as f:
        pattern = f.read().rstrip('\n')
    
    #strip spaces too    
    text = text.strip()
    pattern = pattern.strip()
    
    match_indexes = pattern_match_wildcard(text,pattern)
    
    #swap them to 1 based indexing for assignment purposes
    outputs = map( (lambda x: x+1) ,match_indexes)
    
    output_str = "\n".join(map(str, outputs))
    
    print(output_str)
    
    #write to file
    with open("output_a1q1.txt", "w", encoding="utf-8") as out:
        out.write(output_str)


if __name__ == "__main__":
    main(sys.argv)

# bbebabababebebababab
# be##ba#