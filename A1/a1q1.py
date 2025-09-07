
import sys

SPECIAL_CHAR = '#'
DELIMITER = '$'

def match_special(a,b):
    if a == b:
        return True
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
                    matching = match_special( s[k+match_length], s[match_length])
                    if matching:
                        match_length += 1
                Z[k] = match_length
                l = k 
                r = k + match_length - 1
    return Z

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
    Z = z_algorithm_special(combined)
    m = len(pattern)
    
    output_line = ""
    
    #get the indexes where the Z value is high enough that it means a full pattern match
    for i in range(m + 1, len(combined)):
        if Z[i] >= m:
            output_line += str(i - m) + "\n"
            
    output_line = output_line.strip()
    
    print(output_line)
    
    #write to file
    with open("output_a1q1.txt", "w", encoding="utf-8") as out:
        out.write(output_line + "\n")


if __name__ == "__main__":
    main(sys.argv)
