# Recommendation Engine

In this file there are 2 recommendation types with the following idea:
1. Content based filtering: for each product in the database, retrieve other products with similar categories/brands and target audience, using a filtering system.  
The manner in which the filtering is done is as follows. For product A, look up products that have exactly the same categories/brands/target audience. If the result is less than 4 products, one of the filters is removed. This repeats until there are at least a minimum of 4 similar products.

2.	Collaborative based filtering: for each profile that has viewed at least one product, look up other profiles that have also viewed the exact same product(s). From these profiles, keep a list containing all the other products they have viewed and recommend the 4 most commonly viewed products among these profiles.


- Content_filtering takes around ~5-10 minutes to generate and insert the data for all products.
- Collaborative_filtering takes around ~3 minutes to generate and insert the data per individual profile.

If needed, files containing assignment 2 (creating database): https://github.com/ayoub-z/HU_WebShop

Screenshot query tables: https://imgur.com/a/cDEBji5
- The recommendations from content_filtering have all been put in the database
- Sinds collaborative_filtering takes ~3 minutes per profile, only 15 profiles have been inserted in the database as an example.
