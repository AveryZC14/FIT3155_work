"""
File: a1q1.py
Author: Avery Cheng
Description: This was the best I could think of, please give me good marks
"""
import sys

SPECIAL_CHAR = '#'
DELIMITER = '$'

def match_special(a,b):
    if a == DELIMITER or b == DELIMITER:
        return False
    if a == b:
        return True
    #no longer used but can't be bothered to remove it
    return b == SPECIAL_CHAR or a == SPECIAL_CHAR

# Function to compute the Z-array for a given string
def z_algorithm_special(s):
    # Initialize the length of the string
    n = len(s)
    # Create an array Z of the same length as s, initialized to zeros
    Z = [0] * n
    # Set initial window [L, R] to [0, 0]
    l, r = 0, 0
    # Iterate over the string from position 1 to end
    for k in range(1, n):
        
        #case 1: if k > r
        if k > r:
            # explicitly compare
            matching = True
            match_length = 0
            while matching and k+match_length < n:
                matching = match_special( s[k+match_length], s[match_length])
                if matching:
                    match_length += 1
            Z[k] = match_length
            l = k 
            r = k + match_length - 1
            
        #case 2: if k <= r
        else:
            
            prev_box = Z[k-l]
            remaining = r-k+1
            
            # case 2a: it doesnt extend the z box, so copy from existing Z value
            if prev_box < remaining:
                Z[k] = Z[k-l]
                
            #case 2b: it does extend the z box, which means we can cut it off at the end of the z box
            elif prev_box > remaining:
                Z[k] = remaining
                
            # case 2b also: it equals the z box, which means we need explicit comparisons
            else:
                #explicitly compare again
                matching = True
                match_length = 0
                while matching and k+match_length < n:
                    matching = match_special( s[k+match_length], s[match_length])
                    if matching:
                        match_length += 1
                Z[k] = match_length
                l = k 
                r = k + match_length - 1
    return Z

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
        occurences = find_occurrences(block, text)
        
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


#simple pattern match with Z algorithm (to pattern match the blocks to the text)
def find_occurrences(pattern, text):
    
    combined = pattern + DELIMITER + text
    Z = z_algorithm_special(combined)
    pat_length = len(pattern)
    occurences = []
    
    for i in range(len(text)):
        
        #Z[pat_length + i + 1] is the z box of text[i]
        #if the z box goes over, it's a full match
        if Z[pat_length + i + 1] >= pat_length:
            occurences.append(i)
            
    return occurences

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