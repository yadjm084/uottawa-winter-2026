#DTI5125-Data Science Applications

#Practice 2 – Text Data Partitioning (Gutenberg)

#Student: Adjmal Younoussa


1. Objective of the Assignment

- Take a sufficient sample of Gutenberg's digital 3 books.

- Create (random?!) samples of 200 partitions of the book. 

- Make sure each partition or record has 100 words.

- Generalize the program so that you can replicate that for multiple books.

- Maintain the label for each of the text segments or records or document, label them as a, b and c etc. as per the book they belong to.

- Use Regular Expressions and Pandas to manipulate the data and serialize them.


- Deliverables include the Python program and a ReadMe.doc file. Please make your programs literate to be easier for your respected TA to evaluate and grade.


2. Text Preparation and Tokenization

For each book:

* The raw text is loaded from the Gutenberg corpus.
* The text is tokenized into sentences using:
  nltk.sent_tokenize(text)

This produces a list of sentences that preserves the original structure of the book.


4. Partitioning Strategy

A generalized function is implemented to partition a book into a fixed number of segments:

partition_function(name_of_book, number_of_partition)

Inside the function:

* The total number of sentences in the book is divided by the number of partitions to determine how many sentences go into each partition.
* The list of tokenized sentences is sliced sequentially to produce the required number of partitions.
* Each partition is a list of sentences taken from the original book.

This approach ensures that the code can be reused for any book and any number of partitions.


5. Generalization to Multiple Books

The program applies the partitioning function to multiple books by iterating over a list of 3 Gutenberg book filenames.
The partitions from all books are combined into a single collection, and the combined dataset is shuffled to mix partitions from different books.


6. Labeling of Text Segments

Each partition is labeled with the name of the book it comes from.


7. Use of Pandas and Serialization

After partitioning and labeling:

	- The data is converted into a Pandas DataFrame.
	- Each row represents one partition.
	- Columns created:

		* `book` → the book filename
		* `partition_id` → unique index in the combined dataset
		* `text` → the partition as one string (sentences joined together)

8. How to Run the Program

	- Make sure NLTK and Pandas are installed.

	- Download required NLTK resources:

	    	* gutenberg
	    	* punkt

	- Run all cells in the notebook in order.

	- The final output will be stored in a Pandas DataFrame.


