import sqlite3

db = 'interview.db'
conn = sqlite3.connect(db)
c = conn.cursor()

#  Creating std_member_info table
def create_std_member_info():
    sql = '''CREATE TABLE IF NOT EXISTS std_member_info (
            member_id PRIMARY KEY,
            member_first_name,
            member_last_name,
            date_of_birth,
            main_address,
            city,
            state, 
            zipcode, 
            payer); '''
    c.execute(sql)

# Organzing Date Format to be changed to YYYY-DD-MM
def change_date_format(table, col):
    sql = f'''UPDATE {table} SET [{col}] = substr({col}, 7, 4) 
    || '-' || substr({col}, 1,2) || '-' || 
    substr({col}, 4,2);'''

    c.execute(sql)
    conn.commit()

def change_state_format(table):
    sql = f'''UPDATE {table} SET state = "California" WHERE state = "CA";'''
    c.execute(sql)
    conn.commit()

# Inserting data into std_member_info table
def insert_data():
    sql = '''INSERT into std_member_info (member_id, member_first_name, member_last_name,date_of_birth,main_address,city,state, zipcode, payer) 
    SELECT Person_Id, First_Name, Last_Name, Dob, Street_Address, City, State, Zip, payer FROM roster_2 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01" 
    UNION SELECT Person_Id, First_Name, Last_Name, Dob, Street_Address, City, State, Zip, payer FROM roster_5 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01"
    UNION SELECT Person_Id, First_Name, Last_Name, Dob, Street_Address, City, State, Zip, payer FROM roster_1 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01"
    UNION SELECT Person_Id, First_Name, Last_Name, Dob, Street_Address, City, State, Zip, payer FROM roster_3 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01"
    UNION SELECT Person_Id, First_Name, Last_Name, Dob, Street_Address, City, State, Zip, payer FROM roster_4 WHERE eligibility_start_date <= "2022-04-01" AND eligibility_end_date > "2022-04-01";'''

    c.execute(sql)
    conn.commit()



# Run below once:

# Change roster 2 date format to match other rosters: YYYY-MM-DD
change_date_format('roster_2', 'eligibility_start_date')
change_date_format('roster_2', 'eligibility_end_date')
change_date_format('roster_2', 'Dob')

# Change roster 4 format of state 'CA' -> 'California'
change_state_format('roster_4')

# Create new table
create_std_member_info()

# Insert data into table
insert_data()

'''
QUESTIONS
'''

# Q1:How many distinct members are eligible in April 2022? Answer: 98401 members
q1_sql = '''SELECT COUNT (DISTINCT member_id) FROM std_member_info;'''
c.execute(q1_sql)
q1_results = c.fetchall()
print(f'Q1: How many distinct members are eligible in April 2022? Answer: {q1_results[0][0]}\n')


# Q2: How many members were included more than once? (Those eligible in April 2022)
q2_sql = '''
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
'''
c.execute(q2_sql)
q2_results1 = c.fetchall()
print(f'Q2: How many members were included more than once? (Those only eligible in April 2022) Answer: {q2_results1[0][0]}')

# Q2: How many members were included more than once?
q2_sql2 = '''
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
'''
c.execute(q2_sql2)
q2_results2 = c.fetchall()
print(f'Q2: How many members were included more than once? Answer: {q2_results2[0][0]}\n')

# Q3: What is the breakdown of members by payer?

q3_sql = '''
SELECT payer, count(member_id) FROM std_member_info GROUP BY payer;
'''
c.execute(q3_sql)
q3_results = c.fetchall()
print(f'Q3: What is the breakdown of members by payer? (Eligible in April 2022) Answer: {q3_results}\n')

# Q4: How many members live in a zip code with a food_access_score lower than 2?
q4_sql = '''
SELECT COUNT(*) FROM 
(SELECT member_id, zipcode FROM std_member_info
INNER JOIN
model_scores_by_zip ON std_member_info.zipcode = 
model_scores_by_zip.zcta WHERE 
model_scores_by_zip.food_access_score < 2.0);
'''
c.execute(q4_sql)
q4_results = c.fetchall()
print(f'Q4: How many members live in a zip code with a food_access_score lower than 2? (Eligible in April 2022) Answer: {q4_results[0][0]}\n')

# Q5: What is the average social isolation score for the members?
q5_sql = '''
SELECT avg(social_isolation_score) FROM 
(SELECT zcta, social_isolation_score FROM model_scores_by_zip
JOIN std_member_info ON model_scores_by_zip.zcta = std_member_info.zipcode);
'''
c.execute(q5_sql)
q5_results = c.fetchall()
print(f'Q5: What is the average social isolation score for the members? (Eligible in April 2022) Answer: {q5_results[0][0]}\n')


# Q6: Which members live in the zip code with the highest algorex_sdoh_composite_score?
q6_sql = '''
SELECT member_id, member_first_name, member_last_name, zipcode
from std_member_info WHERE zipcode = 
(SELECT zcta from model_scores_by_zip
ORDER BY algorex_sdoh_composite_score DESC LIMIT 1);'''
print('Q6: Which members live in the zip code with the highest algorex_sdoh_composite_score?')
c.execute(q6_sql)
q6_results = c.fetchall()
zip = q6_results[0][3]
print(f'The zip code with the highest algorex_sdoh_composite_score is {zip}. Below are the list of members who live in that zipcode')
for i in q6_results:
    print(i[0], ': ', i[1], ', ', i[2])


c.close()