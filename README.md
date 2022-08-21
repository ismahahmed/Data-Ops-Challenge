# Data Ops Challenge

## Objective
You are being asked to take multiple member rosters and combine them to get a full view of the membership. With the full membership, create summary statistics to be used for further analysis.
Using `Python` and `SQLite` to complete the steps of combining the member rosters and creating the requested tables and summary statistics.

## Data 
The `interview.db` is a sqlite database that includes the following tables:
- `roster_1`
- `roster_2`
- `roster_3`
- `roster_4`
- `roster_5`
- `model_scores_by_zip`

The five rosters have the following columns: *Person_Id, First_Name, Last_Name, Dob, Age, Gender, Street_Address, State, City, Zip, Street_Address, State, City, Zip, eligibility_start_date, eligibility_end_date, payer*

The `model_scores_by_zip` has the following columns: *zcta, state_code, state_name, nightborhood_stress_score, algorex_sdoh_composite_score, social_isolation_score, transportation_access_score, food_access_score, unstable_housing_score, state_govt_assitance, homeless_indicator, derived_indicator*

## Creating std_member_info table
For this challenge, I needed to create a table that included data from the 5 rosters only inluding members that are eligible during April 2022. It is also important to note that this table includes one row per member. Here are the folloing columns I will be including in the `std_member_info` table:
- *member_id*
- *member_first_name*
- *member_last_name* 
- *date_of_birth*
- *main_address* 
- *city*
- *state*
- *zip_code*
- *payer*

## Standarizing Data

In order to combine the rosters into one table, I needed to make sure the data was standarized. Firstly, I needed to change roster 2 date format to match other rosters: YYYY-MM-DD. I did this by creating a function that took in two parameters: `table` and `col`. Based on the table and column selected, the data will be changed from DD-MM-YYYY to YYYY-MM-DD.

```python
def change_date_format(table, col): 
    sql = f'''UPDATE {table} SET [{col}] = substr({col}, 7, 4) 
    || '-' || substr({col}, 1,2) || '-' || 
    substr({col}, 4,2);'''

    c.execute(sql)
    conn.commit()
```
All but one roster had the state set as 'California'. Roster 4 however used the abbriviated version of `CA`. I created a fucntion that would fix this. 

```python
def change_state_format(table):
    sql = f'''UPDATE {table} SET state = "California" WHERE state = "CA";'''
    c.execute(sql)
    conn.commit()
```

## Inputting Data and Querying
The rest of the script is available <a href="https://github.com/ismahahmed/Data-Ops-Challenge/tree/main/data_challenge.py">here</a>. In the script I include creating the `std_member_info` table, inserting data for the eligible members in April 2022 as well as answering the questions below. 

## Questions answered in the script 

### Q1: How many distinct members are eligible in April 2022? 

There are **98,041** distinct members who are eligible in April 2022 

~~~~sql
SELECT COUNT (DISTINCT member_id) FROM std_member_info;
~~~~

### Q2: How many members were included more than once?

For members eligible in April 2022, there were **17,740** members included more than once. 

~~~~sql
SELECT count(*) FROM (SELECT Person_Id, COUNT(Person_Id) 
FROM (
  SELECT Person_Id  FROM roster_1 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01" 
	UNION ALL SELECT Person_Id FROM roster_2 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01"
	UNION ALL SELECT Person_Id FROM roster_3 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01"
	UNION ALL SELECT Person_Id FROM roster_4 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01"
	UNION ALL SELECT Person_Id FROM roster_5 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01"
) 
GROUP BY Person_Id
HAVING COUNT(Person_Id) > 1);
~~~~

For members overall, there were **24,620** members included more than once. 

~~~~sql
SELECT count(*) FROM (SELECT Person_Id, COUNT(Person_Id) 
FROM (
  SELECT Person_Id  FROM roster_1
	UNION ALL SELECT Person_Id FROM roster_2
	UNION ALL SELECT Person_Id FROM roster_3
	UNION ALL SELECT Person_Id FROM roster_4
	UNION ALL SELECT Person_Id FROM roster_5
) 
GROUP BY Person_Id
HAVING COUNT(Person_Id) > 1);
~~~~

### Q3: What is the breakdown of members by payer? (Using `std_member_info` table)

For payer `Madv` there were **36,690** members, and for payer `Mdcd` there were **61,351** members

~~~~sql
SELECT payer, count(member_id) FROM std_member_info GROUP BY payer;
~~~~

### Q4: How many members live in a zip code with a food_access_score lower than 2? (Using `std_member_info` and `model_scores_by_zip` tables)

There are **7566** members who live in a zip code with a food_access_score lower than 2

~~~~sql
SELECT COUNT(*) FROM 
(SELECT member_id, zipcode FROM std_member_info
INNER JOIN
model_scores_by_zip ON std_member_info.zipcode = 
model_scores_by_zip.zcta WHERE 
model_scores_by_zip.food_access_score < 2.0);
~~~~

### Q5: What is the average social isolation score for the members? (Using `std_member_info` and `model_scores_by_zip` tables)

The average social isolation score for the members is **3.0686842239472822**

~~~~sql
SELECT avg(social_isolation_score) FROM 
(SELECT zcta, social_isolation_score FROM model_scores_by_zip
JOIN std_member_info ON model_scores_by_zip.zcta = std_member_info.zipcode);
~~~~

### Q6: Which members live in the zip code with the highest algorex_sdoh_composite_score? (Using `std_member_info` and `model_scores_by_zip` tables)

~~~~sql
SELECT member_id, member_first_name, member_last_name, zipcode
from std_member_info WHERE zipcode = 
(SELECT zcta from model_scores_by_zip
ORDER BY algorex_sdoh_composite_score DESC LIMIT 1);
~~~~
