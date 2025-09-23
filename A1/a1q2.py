
import sys

# Function to compute the Z-array for a given string
def z_algorithm(s):
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
                matching = s[k+match_length] == s[match_length]
                if matching:
                    match_length += 1
            Z[k] = match_length
            l = k 
            r = k + match_length - 1
        #case 2: if k <= r
        else:
            # case 2a: it doesnt extend the z box, so copy from existing Z value
            prev_box = Z[k-l]
            remaining = r-k+1
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
                    matching =s[k+match_length] == s[match_length]
                    if matching:
                        match_length += 1
                Z[k] = match_length
                l = k 
                r = k + match_length - 1
    return Z

def preprocess_bad_character(pat):
    #latest occurence is a dictionary of characters to their latest occurence
    latest_occurence = {}
    length = len(pat)
    
    #initialise result to an empty dictionary. we'll attribute chars to lists in result
    result = {}  
    
    #Iterate through the indexes backwards
    for i in range(length-1,-1,-1):
        
        char = pat[i]

        #if char isn't in the result, add it to the result
        if char not in result:
            result[char] = [None]*length

        #for each character, take their latest occurence as the new value
        for existingChar in latest_occurence:
            result[existingChar][i] = latest_occurence[existingChar]
        
        #update the latest character in latest occurence
        latest_occurence[char] = i

    return result
    
        

def preprocess_good_prefix_matched_suffix(pat):
    #z suffix array can be created with the z algorithm
    z_prefix = z_algorithm(pat)
    
    #length
    length = len(pat)
    
    #initialise good prefix to Nones.
    good_prefix = [None] * length
    
    #compute good_prefix
    #iterate backwards through the indices
    for i in range(length-1,-1,-1):
        
        z_box = z_prefix[i]
        #if the z_box is greater than 0, it means the substring starting at index i matches the prefix
        if z_box > 0:
            #if there isn't a value at z_box already, or if it's larger than our index, then replace with i.
            #we want the smallest i value for every z box size because that ensures we don't accidentally shift and skip an occurence of good prefix
            if good_prefix[z_box] == None or good_prefix[z_box] > i:
                good_prefix[z_box] = i
                # print(f"replaced at index {z_box} with {i}")
    
    #create z suffix
    z_suffix = (z_algorithm(pat[::-1]))
    z_suffix.reverse()
    # print("zsuf",z_suffix)
    
    #init matched suffix
    matched_suffix = [None]*length
    
    #iterate 
    for i in range(length):
        suff_box = z_suffix[i]
        #if the suff box encapsulates all characters from the first to the i-th, then it's a suffix that matches the prefix
        if suff_box > 0 and i - suff_box + 1 == 0:
            matched_suffix[i] = suff_box
    
    #fill in values with their latest matched suffix length
    for i in range(1,length):
        if matched_suffix[i] == None:
            matched_suffix[i] = matched_suffix[i-1]
    #could probably combine the for loops but i have no time
    
    return good_prefix, matched_suffix


def boyer_moore_leftwards(text, pattern):
    #lengths
    txt_len = len(text)
    pat_len = len(pattern)
    
    #edge case
    if txt_len < pat_len:
        return []
    #todo: more edge cases idk
    
    #preprocessing stage
    bad_char_dict = preprocess_bad_character(pattern)
    good_prefix, matched_suffix = preprocess_good_prefix_matched_suffix(pattern)
    
    for b in bad_char_dict:
        print(b,bad_char_dict[b])
    print("gp",good_prefix)
    print("ms",matched_suffix)
    
    # print("hgelllo")
    
    #skip range for galil's optimisation
    skip_start = -1
    skip_end = -1
    
    #index to align the left edge of the pattern to
    pattern_align = txt_len-pat_len
    
    matches = []
    
    #outer while loop shifts pattern
    while pattern_align >= 0:
        # print("\nPA",pattern_align)
        ini = pattern_align
        #index in pattern
        i = 0
        #inner while loop matches txt to pattern
        while i < pat_len:
            # print("i",i)
            # print("skipstartend",skip_start,skip_end)
            # if in a skip range, skip
            if skip_start <= i and i <= skip_end:
                # print("skip to",str(skip_end+1))
                i = skip_end+1
            #if the characters match, move on
            elif text[pattern_align+i] == pattern[i]:
                i += 1
            #else we have a mismatch at position i
            else:
                shift = 1
                
                # bad character shift
                bad_char_shift = 0
                bad_char = text[pattern_align+i]
                
                if bad_char in bad_char_dict:
                    
                    #get next occurence of bad character in pat
                    idx_of_character = bad_char_dict[bad_char][i]
                    
                    # minus i to get the shift
                    if idx_of_character != None:
                        bad_char_shift = idx_of_character - i
                
                #good prefix shift
                used_good_prefix = True
                good_prefix_shift = good_prefix[i]
                if good_prefix_shift == None:
                    #fall back onto matched_suffix
                    good_prefix_shift = matched_suffix[i]
                    used_good_prefix = False
                    # print("used matched suffix")
                else:
                    # print("used good prefix")
                    pass
                
                # print("shifts",shift,bad_char_shift,good_prefix_shift)
                shift = max([shift,bad_char_shift,good_prefix_shift])
            
            
                # #galil's skip window
                if (shift == good_prefix_shift & shift >= 1):
                    #set the shift window
                    if used_good_prefix:
                        #the skip window will be the place where the prefix occurs again in the text
                        #good prefix shift is the place where the prefix occurs again
                        # i is the length of the prefix
                        # skip_start = good_prefix_shift
                        skip_start = -1
                        skip_end = -1
                    else:
                        #the skip window will be the prefix that matches the suffix
                        # skip_start = pat_len-good_prefix_shift
                        # skip_end = pat_len
                        skip_start = -1
                        skip_end = -1
                else: # bad character rule used, no shift available
                    skip_start = -1
                    skip_end = -1
                
                assert shift >= 1
                pattern_align -= shift
                break # no more on this alignment
            
        # print(f"while loop broken, i: {i}")
        if (i >= pat_len): #full match
            
            #reset galil skip window
            # skip_start = -1
            # skip_end = -1
            
            matches.append(pattern_align)
            
            pattern_align -= 1
            
        assert ini != pattern_align
        
    # print("matches:",matches)
    return matches
                
                
                
                
                
        
    

def main(argv):
    #open sussies
    text_path, pattern_path = argv[1], argv[2]
    
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read().rstrip('\n')
        
    with open(pattern_path, 'r', encoding='utf-8') as f:
        pattern = f.read().rstrip('\n')
    
    
    indexes = boyer_moore_leftwards(text,pattern)
    # wababaabcabzbbabacbayabababaxbacaxx
    #                        ababacba
    # output = boyer_moore_leftwards("wababaabcabzbbabacbayabababaxbacaxx", "ababacba")
    #increment to 1 based indexing for assignment purposes
    
    output = map((lambda x:x+1), indexes)
    output_line = "\n".join(map(str,output))
    
    print(output_line)
    
    #write to file
    with open("output_a1q2.txt", "w", encoding="utf-8") as out:
        out.write(output_line + "\n")


if __name__ == "__main__":
    main(sys.argv)
    # res = bad_character("abacab")
    # for b in res:
    #     print(b,res[b])
    # preprocess_good_suffix("acababacaba")
    # print("\n".join(map(str,preprocess_good_suffix_and_matched_prefix("acababacaba"))))
    # print("\n")
    # print("\n".join(map(str,preprocess_good_prefix_matched_suffix("abacababaca"))))
    # output = boyer_moore_leftwards("wababacbaxababacbazbbabacbayabababxacbaxx", "ababacba")
    # wababacbaxababacbazbbabacbayabababxacbaxx
    #           ababacba
    
    #       a
    #       ababacba
    # output_line = "\n".join(map(str,output))
    # print(output_line)
