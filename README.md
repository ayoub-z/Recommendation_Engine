# Recommendation Engine

There are 2 recommendation engines:
1. Content based filtering: for each product in the database, retrieve other products with similar categories/brands and target audience, using a filtering system.  
The manner in which the filtering is done is as follows. For product A, look up products that have exactly the same categories/brands/target audience. If the result is less than 4 products, one of the filters is removed. This repeats until there are at least 4 products.

2.	Collaborative based filtering: for each profile that has viewed at least one product, look up other profiles that have also viewed the same product(s). From these profiles, keep a list containing all the products they have viewed and recommend the 4 products that have been the most commonly viewed among these profiles.


- Content_filtering takes around ~5-10 minutes to generate and insert the data for all products.
- Collaborative_filtering takes around ~3 minutes generate and insert the data per individual profile.
