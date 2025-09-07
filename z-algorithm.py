# Z-algorithm structure (no implementation, only comments)

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
                    matching = s[k+match_length] == s[match_length]
                    if matching:
                        match_length += 1
                Z[k] = match_length
                l = k 
                r = k + match_length - 1
    return Z
    

if __name__ == "__main__":
    # Example usage
    s = "ababcab"
    z_array = z_algorithm(s)
    print("Z-array:", z_array)
    # Test cases
    print(z_algorithm("aaaa"))
    assert z_algorithm("aaaa") == [0,3,2,1]
    print(z_algorithm("abc"))
    assert z_algorithm("abc") == [0, 0, 0]
    print(z_algorithm("ababc"))
    assert z_algorithm("ababc") == [0, 0, 2, 0, 0]