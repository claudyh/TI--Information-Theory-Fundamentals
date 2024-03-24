## Information Theory Fundamentals
*in Python*

&nbsp;

### 📋 Project 1 Description
---

The goal of the first project was to promote sensitivity to the fundamental issues of information theory, particularly information, redundancy, entropy, and mutual information. For this purpose, a small music identification simulator was developed, following these steps:

&nbsp;

1. Write a function that, given a source of information P with an alphabet A={a1,…,an}, determines and visualizes the histogram of occurrence of its symbols.
   
3. Write the code that, given a source of information P with an alphabet A={a1,…,an}, determines the theoretical minimum limit for the average number of bits per symbol.
4. Using the functions developed in questions above, determine the statistical distribution (histogram) and the minimum limit for the average number of bits per symbol.
5. Using the Huffman encoding functions provided, determine the average number of bits per symbol for each of the information sources.
6. Repeat question 3 applying symbol sequesnces, i.e., assuming that each symbol is actually a sequence of two contiguous symbols.
7. At this point, the mutual information between the signal to be searched (query) and the signal where to search (target) will be calculated using a sliding window. This means that the query will "slide" over the target, and the mutual information will be calculated in each of the windows. The interval between consecutive windows is designated by step.
   - Write a function that, given the query, the target, an alphabet A={a1,…,an}, and the step, returns the vector of mutual information values in each window.
   - Using the file "saxriff.wav" as the query, determine the variation of mutual information between this and the files "target01 - repeat.wav" and "target02 – repeatNoise.wav". Define a step value of ¼ of the length of the query vector (rounded value).
   - Note: Use only the first channel of each sound file (first column).
   - Now, a small music identification simulator will be created. Using the file "saxriff.wav" as the query and the files Song*.wav as targets: determine the evolution of mutual information for each of the files; calculate the maximum mutual information in each of them; finally, present the search results, sorted in descending order of mutual information. Define a step with a value of ¼ of the duration of the query.

&nbsp;

### 📋 Project 2 Description
---

The goal of the second project was to acquire sensitivity to the fundamental issues related to encoding using Huffman trees and LZ77 dictionaries. For this purpose, a 'gzip' file decompressor was developed, following this steps:

&nbsp;

1. Create a method that reads the block format (i.e., returns the value corresponding to HLIT, HDIST, and HCLEN), according to the structure of each block.
   
3. Create a method that stores in an array the lengths of the codes from the "code length alphabet", based on HCLEN. Note that the sequences of 3 bits to be read correspond to the order 16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15 in the code array.
4. Create a method that converts the code lengths from the previous item into Huffman codes of the "code length alphabet".
5. Create a method that reads and stores in an array the HLIT + 257 lengths of the codes referring to the literal/length alphabet, encoded according to the Huffman code of code lengths. Use functions from the huffmantree.py file, especially the functions for sequential code search (bit by bit). Note that some codes require reading some extra bits (especially indexes 16, 17, and 18 of the alphabet).
6. Create a method that reads and stores in an array the HDIST + 1 code lengths referring to the literal/length alphabet, encoded according to the Huffman code of code lengths. Use functions from the huffmantree.py file, especially the functions for sequential code search (bit by bit). Note that some codes require reading some extra bits (especially indexes 16, 17, and 18 of the alphabet).
7. Using the method from point 3, determine the Huffman codes referring to the two alphabets (literal/length and distances) and store them in an array.
8. Create the necessary functions to decompress the compressed data, based on the Huffman codes and the LZ77 algorithm. Use functions from the huffmantree.py file, especially the functions for sequential code search (bit by bit). Note that some codes require reading some extra bits (for example, indexes 265 to 285 in the literal/length alphabet or indexes 4 to 29 in the distance alphabet).
9. Save the decompressed data to a file with the original name (consult the gzipHeader structure, especially the fName field).

&nbsp;

---

**NOTE:** For the development of these projects we had support documents given by our professors as well as a source code given as a working base. The authors of those codes are identified in the beginning of each code. Those files are: gzip.py, huffmantree.py and testhuffmantree.py. These projects were developed within the scope of a Computer Science course by Cláudia Torres and Maria João Rosa.
