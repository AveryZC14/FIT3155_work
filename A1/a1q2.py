
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
    
    return z_prefix, good_prefix, matched_suffix

def preprocess_good_suffix(pat):
    
    z_suffix = (z_algorithm(pat[::-1]))
    z_suffix.reverse()
    print(z_suffix)

    length = len(pat)
    good_suffix = [None] * (length+1)
    
    for i in range(length):
        z_box = z_suffix[i]
        good_suffix[length-z_box] = i
    print(good_suffix)
    
    matchedprefix = [None]*(length+1)
    
def preprocess_good_suffix_and_matched_prefix(pat: str):
    """
    Preprocess 'pat' to build:
      1) z_suffix:  length-m array (0-based). z_suffix[p] = length L of the longest substring
         that ENDS at index p in 'pat' and equals a SUFFIX of the whole pattern.
         (Built by computing Z on the reversed pattern and mapping back.)

      2) good_suffix_pos: length-(m+1) array (0-based indices, but sized like the notes).
         Index k0 in [0..m] corresponds to k = k0+1 in the notes.
         For a mismatch at pattern index i, the matched suffix length is s = m-1-i,
         and k0 = i+1. Then:
             p = good_suffix_pos[k0]  (p is the RIGHTMOST end position in 'pat' where
                                       that matched suffix reoccurs with a different
                                       preceding character)
         If p != -1, the good-suffix shift is:  shift = m - (p+1).
         If p == -1, there is no internal reoccurrence; we must fall back to matched-prefix.

         We store -1 when there is no such p. (This is equivalent to gs(k+1)=0 in the notes.)
         NOTE: We choose the RIGHTMOST p when multiple candidates exist.

      3) matched_prefix_len: length-(m+1) array (0-based, sized like the notes).
         matched_prefix_len[k0] (k0 in [0..m]) corresponds to mp(k0+1) in the notes:
             the length of the LONGEST PREFIX of 'pat' that is also a suffix of pat[k..m-1],
             where k = k0 (0-based).
         We set:
             matched_prefix_len[0]   = m   (mp(1) = m by convention)
             matched_prefix_len[m]   = 0   (mp(m+1) = 0)
         and fill the middle using the ordinary Z-array on 'pat', plus a rightward
         propagation so shorter suffixes inherit the best known border.

    Returns:
        z_suffix, good_suffix_pos, matched_prefix_len
    """
    m = len(pat)
    if m == 0:
        # Trivial edge case
        return [], [0], [0]

    # -----------------------------
    # Build z_suffix via reversed Z
    # -----------------------------
    pat_rev = pat[::-1]
    Z_rev = z_algorithm(pat_rev)

    # Map Z on reversed back to "end-aligned" Z on the original:
    # Z_rev[i] is a prefix match length starting at i in pat_rev,
    # which corresponds to a suffix match ENDING at p = m-1 - i in pat.
    z_suffix = [0] * m
    for i in range(m):
        p = m - 1 - i        # end position in original pat
        z_suffix[p] = Z_rev[i]

    # -------------------------------------------
    # Build good_suffix_pos (aka gs positions)
    # -------------------------------------------
    # good_suffix_pos has size m+1 so index k0 corresponds to k = k0+1 (notes).
    # We'll store the RIGHTMOST end-position p (0-based) for each k0; -1 means none.
    good_suffix_pos = [-1] * (m + 1)

    # For each end position p in pat, z_suffix[p] = L means:
    # there is a substring ending at p that equals the suffix of length L.
    # For L in (0, m): it contributes to gs at index k0 = m - L
    # (since k = m - L + 1 in the notes, so k0 = k-1 = m - L).
    #
    # We ignore L == m (the whole pattern), since the good-suffix rule uses PROPER suffixes.
    for p in range(m):
        L = z_suffix[p]
        if 0 < L < m:
            k0 = m - L  # 0-based index into our size-(m+1) table
            # Choose the RIGHTMOST p (largest p) if multiple candidates exist
            if p > good_suffix_pos[k0]:
                good_suffix_pos[k0] = p

    # ----------------------------------------------------------------------------------
    # Build matched_prefix_len (mp) using the ordinary Z-array on the original pattern
    # ----------------------------------------------------------------------------------
    # Idea: if j + Z[j] == m, then a prefix of length L = Z[j] is a suffix of the WHOLE
    # pattern. That border also serves as a prefix for any suffix pat[k..m-1] that is
    # long enough. We'll seed the positions k0 = m - L, then propagate to the left.
    Z = z_algorithm(pat)

    matched_prefix_len = [0] * (m + 1)
    matched_prefix_len[0] = m   # mp(1) = m by convention
    matched_prefix_len[m] = 0   # mp(m+1) = 0

    # Seed from Z entries that "touch the end"
    for j in range(1, m):  # j = 1..m-1 (0-based)
        L = Z[j]
        if L > 0 and j + L == m:
            k0 = m - L              # corresponds to mp(k0+1) = L
            if L > matched_prefix_len[k0]:
                matched_prefix_len[k0] = L

    # Propagate best values right-to-left so shorter suffixes inherit the best known border
    for k0 in range(m - 1, 0, -1):
        if matched_prefix_len[k0] < matched_prefix_len[k0 + 1]:
            matched_prefix_len[k0] = matched_prefix_len[k0 + 1]

    return z_suffix, good_suffix_pos, matched_prefix_len

def boyer_moore_leftwards(pattern, text, bad_char, good_prefix):
    pass

def main(argv):
    #open sussies
    text_path, pattern_path = argv[1], argv[2]
    
    with open(text_path, 'r', encoding='utf-8') as f:
        text = f.read().rstrip('\n')
        
    with open(pattern_path, 'r', encoding='utf-8') as f:
        pattern = f.read().rstrip('\n')

    #combined pattern
    combined = pattern + DELIMITER + text
    
    #apply the Z algorithm 
    Z = z_algorithm(combined)
    m = len(pattern)
    
    output_line = ""
    
    #get the indexes where the Z value is high enough that it means a full pattern match
    for i in range(m + 1, len(combined)):
        if Z[i] >= m:
            output_line += str(i - m) + "\n"
            
    output_line = output_line.strip()
    
    print(output_line)
    
    #write to file
    with open("output_a1q2.txt", "w", encoding="utf-8") as out:
        out.write(output_line + "\n")


if __name__ == "__main__":
    # main(sys.argv)
    # res = bad_character("abacab")
    # for b in res:
    #     print(b,res[b])
    # preprocess_good_suffix("acababacaba")
    print("\n".join(map(str,preprocess_good_suffix_and_matched_prefix("acababacaba"))))
    print("\n")
    print("\n".join(map(str,preprocess_good_prefix_matched_suffix("abacababaca"))))
