
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
    
        

def preprocess_good_prefix(pat):
    z_prefix = z_algorithm(pat)
    length = len(pat)
    good_prefix = [None] * length
    
    for i in range(length-1,-1,-1):
        z_box = z_prefix[i]
        good_prefix[z_box] = i

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
    preprocess_good_suffix("acababacaba")
