
To run 

$ make docker-compose-up

Go to http://localhost:8888/docs#/
To see all the api endpoints 




1. /api -> gets all the courses supports sorting and filtering of courses based on domain

2. Endpoint to get the course overview.
    
    /api/course/{course_id} -> gets a specific course

3. Endpoint to get specific chapter information.
    
    /api/chapter/{chapter_id} -> gets a specific chapter

4. Endpoint to allow users to rate each chapter (positive/negative), while aggregating all ratings for each course.

  /api/rating/{chapter_id} -> updates the rating of a specific chapter

   Assuming that rating are anonymous 


Flow: loading data
  
  check if the course documents are already loaded or not <br />
  if not then <br />
      Load the course documents <br />
      Create indexing for those documents <br />
  All setup done <br />
 
  
  
 
 
 For indexing we 
          #General id indexing
         collection.create_index('id')

        # ascending indexing of name fields
        collection.create_index([('name', 1)])

        # descending indexing of date fields
        collection.create_index([('date', -1)])

        # descending indexing of rating fields
        collection.create_index([('rating', -1)])

        # for domain queries
        collection.create_index('domain')

        # General purpose indexing of id fields
        collection.create_index('chapters.id')

        # accesnding indexing of name of chapters
        collection.create_index([('chapters.name', 1), ])

        # decending indexing of rating of chapters
        collection.create_index([('chapters.rating', -1)])
        
 
      
