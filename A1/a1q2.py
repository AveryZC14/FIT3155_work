
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
                print(f"replaced at index {z_box} with {i}")
    
    #create z suffix
    z_suffix = (z_algorithm(pat[::-1]))
    z_suffix.reverse()
    # print("zsuf",z_suffix)
    
    #init matched suffix
    matched_suffix = [None]*length
    
    #iterate backwards
    for i in range(length-1,-1,-1):
        suff_box = z_suffix[i]
        #if the suff box encapsulates all characters from the first to the i-th, then it's a suffix that matches the prefix
        if suff_box > 0 and i - suff_box + 1 == 0:
            matched_suffix[i] = suff_box
    
    #fill in values with their latest matched suffix length
    for i in range(1,length):
        if matched_suffix[i] == None:
            matched_suffix[i] = matched_suffix[i-1]
    
    return good_prefix, matched_suffix


# -----------------------------
# BOYER–MOORE SEARCH (0-based)
# -----------------------------

def boyer_moore_search(text, pattern):
    # n, m: lengths of text and pattern
    n = len(text)
    m = len(pattern)

    # matches: list of starting indices where pattern occurs in text
    matches = []

    # Edge cases: empty pattern or pattern longer than text
    if m == 0:
        # by convention, empty pattern matches at every position including n
        return list(range(n + 1))
    if n < m:
        return matches

    # last: bad-character table (rightmost position per character)
    # last = build_last_occurrence(pattern)
    last = []

    # z_suffix, good_suffix_pos, matched_prefix_len: tables for good-suffix / matched-prefix
    # z_suffix, good_suffix_pos, matched_prefix_len = preprocess_good_suffix_and_matched_prefix(pattern)
    z_suffix, good_suffix_pos, matched_prefix_len = []

    # full_match_shift: shift to apply after a full match (matched-prefix rule)
    # equals m - longest border of the whole pattern; longest border = matched_prefix_len[1]
    full_match_shift = m - (matched_prefix_len[1] if m >= 2 else 0)
    if full_match_shift <= 0:
        full_match_shift = 1

    # align_start: current alignment start in text (pattern[0] under text[align_start])
    align_start = 0

    # Galil skip window [known_start .. known_end] in pattern indices:
    # this region is guaranteed to match in the NEXT alignment (so we can skip it)
    known_start = -1  # left boundary of known-equal region in pattern for next alignment
    known_end = -2    # right boundary (< known_start means "no window")

    # Search main loop: while pattern fits in remaining text
    while align_start <= n - m:
        # i: current index in pattern (right-to-left scan)
        i = m - 1

        # Right-to-left comparisons at this alignment
        while i >= 0:
            # If i lies inside the known-equal window, jump left of the window (Galil)
            if known_start <= i <= known_end:
                i = known_start - 1
                continue

            # If characters match, move left
            if pattern[i] == text[align_start + i]:
                i -= 1
                continue

            # ---- Mismatch at pattern index i ----

            # Bad-character move:
            # last_pos: rightmost index of the mismatched text char in the pattern, or -1
            mismatched_char = text[align_start + i]
            last_pos = last.get(mismatched_char, -1)
            # Align that occurrence under the mismatched char in text; must move at least 1
            bad_char_move = i - last_pos
            if bad_char_move < 1:
                bad_char_move = 1

            # Good-suffix / matched-prefix move:
            # k0: table index for this mismatch (k0 = i+1
            k0 = i + 1
            # p: rightmost end position of an internal reoccurrence of the matched suffix
            p = good_suffix_pos[k0]
            if p != -1:
                # gs-based shift: move so that this internal occurrence lines up
                gs_move = m - (p + 1)
                used_gs_internal = True
            else:
                # fallback: matched-prefix shift for this k0
                gs_move = m - matched_prefix_len[k0]
                used_gs_internal = False

            # Choose the larger safe shift
            shift = gs_move if gs_move > bad_char_move else bad_char_move
            if shift < 1:
                shift = 1

            # -------------------------
            # Galil: set skip window for NEXT alignment (depends on which shift we used)
            # -------------------------
            if shift == gs_move:
                if used_gs_internal:
                    # s: length of the matched suffix before the mismatch
                    s = (m - 1) - i
                    # After an internal good-suffix shift, we KNOW pattern[p - s + 1 .. p]
                    # will match text at the next alignment. Record that window.
                    known_start = p - s + 1
                    known_end = p
                else:
                    # Matched-prefix case: we know the prefix of length mp = matched_prefix_len[k0]
                    mp = matched_prefix_len[k0]
                    if mp > 0:
                        known_start = 0
                        known_end = mp - 1
                    else:
                        # no guaranteed region
                        known_start = -1
                        known_end = -2
            else:
                # Bad-character won: we can't guarantee any region for the next alignment
                known_start = -1
                known_end = -2

            # Advance to next alignment
            align_start += shift
            break  # break the inner comparison loop; continue with next alignment

        else:
            # If we exit the while i>=0 loop normally, we matched the whole pattern
            matches.append(align_start)

            # For the NEXT alignment after a full match, we can also set a Galil window:
            # the prefix of length matched_prefix_len[1] is known to match.
            mp_after_full = matched_prefix_len[1] if m >= 2 else 0
            if mp_after_full > 0:
                known_start = 0
                known_end = mp_after_full - 1
            else:
                known_start = -1
                known_end = -2

            # Shift by the full-match (matched-prefix) amount 
            align_start += full_match_shift

    return matches



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
    
    print("hgelllo")
    
    #skip range for galil's optimisation
    skip_start = -1
    skip_end = -1
    
    #index to align the left edge of the pattern to
    pattern_align = txt_len-pat_len
    
    matches = []
    
    #outer while loop shifts pattern
    while pattern_align > 0:
        print("\nPA",pattern_align)
        ini = pattern_align
        #index in pattern
        i = 0
        #inner while loop matches txt to pattern
        while i < pat_len:
            print("i",i)
            # if in a skip range, skip
            if skip_start <= i and i <= skip_end:
                print("skip to",str(skip_end+1))
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
                    print("used matched suffix")
                else:
                    print("used good prefix")
                
                print("shifts",shift,bad_char_shift,good_prefix_shift)
                shift = max([shift,bad_char_shift,good_prefix_shift])
                
                #galil's skip window
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
            
        print(f"while loop broken, i: {i}")
        if (i >= pat_len):
            print("full match ",pattern_align)
            
            #reset galil skip window
            skip_start = -1
            skip_end = -1
            #full match?
            matches.append(pattern_align)
            #shift by like,,,, ms[1]? or something?
            full_match_shift = 1
            #if the patterns' longer than 1, then there might be a matched_suffix with a better safe shift
            if (pat_len > 1):
                full_match_shift = matched_suffix[1]
                #and again we can set the matched suffix galil's skip window
                skip_start = 0
                skip_end = good_prefix_shift
            pattern_align -= full_match_shift
            
        assert ini != pattern_align
        
    print("matches:",matches)
    return matches
                
                
                
                
                
        
    

def main(argv):
    #open sussies
    text_path, pattern_path = argv[1], argv[2]
    
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read().rstrip('\n')
        
    with open(pattern_path, 'r', encoding='utf-8') as f:
        pattern = f.read().rstrip('\n')
    
    output = boyer_moore_leftwards(text,pattern)
    # wababaabcabzbbabacbayabababaxbacaxx
    #                        ababacba
    # output = boyer_moore_leftwards("wababaabcabzbbabacbayabababaxbacaxx", "ababacba")
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
