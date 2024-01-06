https://recruitmentdashboard.streamlit.app

# Recruitment Dashboard
![Home](home.png)
A dynamic dashboard that shows lead recruitment performance indicators

## 🚧 Under Development 🚧
[ ] Add Candidate Form

[ ] Modification_Date Column

[ ] API Integration

## Index
- <a href="## About">About </a>
- <a href="## Tech Stack">Technology Used </a> 
- <a href="## Layout">Layout </a>
- <a href="## Concepts Covered">Concepts Covered </a>
- <a href="## KPI's">KPI's </a>
- <a href="# -KPIs">Running Locally </a>

## About
This app is a free solutions to recruiters that want to get visual insights of their recruitment kpis with a dynamic dashboard that can be filtered by various parametters. There is a database menu with a dataframe that can be filtered and searched for any value.

An excell template is provided to test the app although any excell file with the columns "Fullname","Phone_Number" and "Email" will work. The columns doesn't have to follow any specific order.

The recommend columns to get the full experience of the app are:
[Comments,Fullname,Email,Phone_Number,Address,DoB,Gender,Language,Source,Application_Date,Status,Recruitment_Stages,Company,Location,Decline_Reasons,Phone_Screen_Date,Harver_Test_Date,Interview_Date,Offer_Date,Hiring_Date,Payment_Date,Modification_Date]

## Technology Used
This app is build with Python 3.7.9 and uses <a href="https://numpy.org">NumPy</a> for mathematical functions, <a href="https://pandas.pydata.org">Pandas</a> to manipulate datafarmes, <a href="https://plotly.com">Plotly</a> for the visualization tools and Streamlit to turn data script into a WebApp and deploy on <a href="https://streamlit.io">Streamlit Cloud Platform </a>.

## Layout
![Dashboard_Sidebar](Dashboard_Sidebar.png)
Dashboard Sidebar

![Database](Database.png)
Database

![Database_Sidebar](Database_Sidebar.png)
Database Sidebar

## Concepts Covered

## KPI's
### All the KPI's shown in the dashboard are in a specific period of time and with the selected language, location, gender or company.
#### Hired
Hired stands for the number of candidates hired.

#### Success Rate
Success Rate is the percentage of hired candidates that turns into an effective placement instead of turning into a whitdrawl or rejection during training for example.

#### Applications Per Hire
Applications Per Hire is the ratio of the total applications divided by the total hired candidates.

#### Days to Hire
Days to Hire is the time taken to hire suitable talent.

#### Recruitment Funnel
The Recruitment Funnel provides a clear understanding of where candidates are in the recruitment process, what stage they need to move to next, and what resources are needed to support them. This can help streamline the recruitment process, improve candidate experience, and ultimately increase the chances of hiring top talent.

#### Recruitment Stages Pipeline


#### Source


#### Source Performance
##### % Of Applications
##### % Of Hired
##### % Of Convertion Rate


#### Decline Reasons
##### % of Applications


## Running Locally
