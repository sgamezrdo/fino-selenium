# fino-selenium
Data scrapping for the Spanish blog [FinoFilipino](https://finofilipino.org/) 

Current functionality:
* Capture main content fields:
	* Title
	* Content(Currently only text / links to img/gif/video)
	* Number of views
	* Number of comments
	* Tags and categories
	* Publish date
 * User comments:
    * Content
    * Comment author
    * Comment publish date
    * Parent / Child hierarchy for answers to comments 
 * Automatic interaction with cookies pop-up
 * Logging
 * AWS compatibility (using -a or --aws as command line parameter)

The scrapped data will be used to run an analysis trying to capture the following dimensions:

* What posts are the most visited ones?
* What correlation is there between number of comments and views?
* What kind of content generates more views / comments?
* What are the most frequent words / topics in the title / content / comments?
* What users are the ones with the highest interaction?
