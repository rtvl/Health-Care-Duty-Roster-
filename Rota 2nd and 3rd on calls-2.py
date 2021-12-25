#!/usr/bin/env python
# coding: utf-8

# In[177]:


import random
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
import random 
from itertools import permutations
import traceback
warnings.filterwarnings('ignore')


# In[184]:


names = ['Alfred', 'Bob', 'Charles', 'David', 'Edward', 'Frank', 'George', 'Henry', 'Ida', 'John', 'King', 'Lincoln', 'Mary', 'Nancy', 'Oscar', 'Peter']


# In[185]:


def Diff(a, b):
    c = [x for x in a if x not in b]
    return c

#Gaps between on calls
def Gaps(DB):
    for i in DB['On call'].value_counts().index:
        DB[i]=np.nan
        DDB=DB[DB["On call"]==i]
        Index=DDB.index
        for j in range(len(Index)-1):
            d=Index[j+1]-Index[j]
            d=d.days

            DB[i].loc[Index[j+1]]=d
    return DB

# Defining a function to count days/holidays/weekends

def Counter(DB):
    names=list(set(DB["On call"].values))
    Par=["Holiday","Weekend","Friday","Workday"]
    Counts=pd.DataFrame(np.nan, columns=Par, index=names)
    
    for p in Par:
        db=DB[DB[p]=="Yes"]
        Counts[p]=db["On call"].value_counts()
    Counts=Counts.fillna(0)
    
    Counts["Weekends & Holidays"]=Counts["Holiday"]+Counts["Weekend"]
    Counts["Weekdays & Fridays"]=Counts["Workday"]+Counts["Friday"]
    Counts["Total"]=Counts["Weekdays & Fridays"]+Counts["Weekends & Holidays"]
        
    return Counts

#Count staff with GAPs
def Gaps_n(DB, Min_gap=5):
    GAP=Gaps(DB)
    GAP=GAP.iloc[:,6:]
    GAP=GAP[GAP<Min_gap]

    GAP=GAP.dropna(how="all", axis=0)
    GAP=GAP.dropna(how="all", axis=1)
    DF=pd.DataFrame(np.nan, index=GAP.columns, columns=["Days_Gaps"])
    for i in GAP.columns:
        DF["Days_Gaps"].loc[i]=len(GAP[i].dropna())
    return DF
        


# In[186]:


def Dist(DB):
    index=DB.index
    #Check and swap those who have 2 on calls on a row    
    for i in range(len(index)-1):
        if DB["On call"].loc[index[i]]==DB["On call"].loc[index[i+1]] and (DB["Holiday"].loc[index[i]]=="No" or DB["Holiday"].loc[index[i+1]]=="No"):
            try:
                DB["On call"].loc[index[i]], DB["On call"].loc[index[i+7]]=DB["On call"].loc[index[i+7]], DB["On call"].loc[index[i]]

            except:
                DB["On call"].loc[index[i]], DB["On call"].loc[index[i-7]]=DB["On call"].loc[index[i-7]], DB["On call"].loc[index[i]]
        
    return DB


# In[187]:


#Name lists

names.sort()
N=len(names)
print("Number of staff", N)

#Holidays for 2022
holidays = [datetime.date(2022, 1, 1),datetime.date(2022, 4, 30) , datetime.date(2022, 5, 1), datetime.date(2022, 5, 2), datetime.date(2022, 5, 3), datetime.date(2022, 5, 4), 
            datetime.date(2022, 7, 8), datetime.date(2022, 7, 9),datetime.date(2022, 7, 10), datetime.date(2022, 7, 11),
           datetime.date(2022, 7, 30), datetime.date(2022, 10, 8),datetime.date(2022, 12, 24), datetime.date(2022, 12, 25),datetime.date(2022, 12, 26)]


# In[188]:


# Create list of weekdays of the year 2022
weekdays = []
for i in range(1, 366):
    weekdays.append(datetime.date(2021, 12, 31) + datetime.timedelta(days=i))


print(len(weekdays))

#Creating calender

ical=weekdays

Cal=pd.DataFrame("No", index=ical, columns=["Day", "Workday","Friday", "Weekend", "Holiday", "On call"])

Cal["Holiday"].loc[holidays]="Yes"

Cal.index = pd.to_datetime(Cal.index)


Cal["Day"]=Cal.index.day_name()

#Rule 1: If Holiday comes on one of the weekend days, then the whole weekend is treated as a holiday
    
for i in range(len(Cal.index)):
    if Cal["Holiday"].loc[Cal.index[i]]=="Yes" and Cal["Day"].loc[Cal.index[i]]=="Saturday":
        Cal["Holiday"].loc[Cal.index[i+1]]="Yes"
    elif Cal["Holiday"].loc[Cal.index[i]]=="Yes" and Cal["Day"].loc[Cal.index[i]]=="Sunday":
        Cal["Holiday"].loc[Cal.index[i-1]]="Yes"

#Rule 2 if weekends happen to happen on a holiday, they are counted as holidays not weekends
for i in range(len(Cal.index)):
    if (Cal["Day"].loc[Cal.index[i]]=="Sunday" or  Cal["Day"].loc[Cal.index[i]]=="Saturday") and  Cal["Holiday"].loc[Cal.index[i]]=="No":
        Cal["Weekend"].loc[Cal.index[i]]="Yes"
        
    
#Rule 3: if Friday is on a holiday then it is only counted as a holiday noy Friday
for i in range(len(Cal.index)):
    if Cal["Day"].loc[Cal.index[i]]=="Friday"  and  Cal["Holiday"].loc[Cal.index[i]]=="No":
        Cal["Friday"].loc[Cal.index[i]]="Yes"

        
# Workdays
for i in range(len(Cal.index)):
    if (Cal["Day"].loc[Cal.index[i]]!="Friday"  and  Cal["Holiday"].loc[Cal.index[i]]=="No") and Cal["Weekend"].loc[Cal.index[i]]=="No":
        Cal["Workday"].loc[Cal.index[i]]="Yes"

# Allocating names on the holidays 
Holiday=Cal[Cal["Holiday"]=="Yes"]
N=len(names)
for i in range(len(Holiday.index)):
    if i>=N:
        j=i-(N*int(i/N))
        Holiday["On call"].loc[Holiday.index[i]]=names[j]
    else:
        Holiday["On call"].loc[Holiday.index[i]]=names[i]

#Count names and sort them from the least to the most :
names_count=Holiday["On call"].value_counts()
names=list(names_count.sort_values().index)
print(names_count)


#Compiling the holiday on calls into the Cal
Cal["On call"].loc[Holiday.index]=Holiday["On call"]


# Allocating names on the Weekends 
Weekend=Cal[Cal["Weekend"]=="Yes"]
N=len(names)
for i in range(len(Weekend.index)):
    if i>=N:
        j=i-(N*int(i/N))

        Weekend["On call"].loc[Weekend.index[i]]=names[j]
    else:
        Weekend["On call"].loc[Weekend.index[i]]=names[i]

#Count names and sort them from the least to the most :
names_count=Weekend["On call"].value_counts()+names_count
print(names_count)
names=list(names_count.sort_values().index)



#Compiling the Weekend on calls into the Cal
Cal["On call"].loc[Weekend.index]=Weekend["On call"]

# Allocating names on the Fridays 
Friday=Cal[Cal["Friday"]=="Yes"]
N=len(names)
for i in range(len(Friday.index)):
    if i>=N:
        j=i-(N*int(i/N))

        Friday["On call"].loc[Friday.index[i]]=names[j]
    else:
        Friday["On call"].loc[Friday.index[i]]=names[i]

#Count names and sort them from the least to the most :
names_count=Friday["On call"].value_counts()+names_count
print(names_count)
names=list(names_count.sort_values().index)



#Compiling the Friday on calls into the Cal
Cal["On call"].loc[Friday.index]=Friday["On call"]


# Allocating names on the Workdays 
Workday=Cal[Cal["Workday"]=="Yes"]
N=len(names)
for i in range(len(Workday.index)):
    if i>=N:
        j=i-(N*int(i/N))

        Workday["On call"].loc[Workday.index[i]]=names[j]
    else:
        Workday["On call"].loc[Workday.index[i]]=names[i]

#Count names and sort them from the least to the most :
names_count=Workday["On call"].value_counts()+names_count
print(names_count)
names=list(names_count.sort_values().index)



#Compiling the Workday on calls into the Cal
Cal["On call"].loc[Workday.index]=Workday["On call"]

DB=Cal


# In[189]:


DB=Gaps(DB)
GAP=DB.min()
GAP=GAP.iloc[6:]

MIN=GAP.min()
GAP=Gaps(DB)
GAP=GAP.iloc[:,6:]
GAP=GAP[GAP<5]
            
GAP=GAP.dropna(how="all", axis=0)
GAP=GAP.dropna(how="all", axis=1)
for i in GAP.columns:
    d=GAP[i].dropna()
    print(i,len(d))


# In[ ]:





# In[190]:


Min_gap=5
Names_only=Gaps(DB).iloc[:,6:]
Names_only=Names_only[Names_only<Min_gap]
MIN=Names_only.min().min()


print("Minimum",MIN)
counter=0    
while MIN<Min_gap:
    GAPS_N=Gaps_n(DB)
    print("Number of staff with short gap",len(GAPS_N))
    

    for name in names:
        counter+=1
        print("Counter",counter)
        

        GAP=Gaps(DB)
        GAP=GAP.iloc[:,6:]
        GAP=GAP.sort_values(by=name)
        df=GAP[GAP[name]<Min_gap]
        GAP[name].loc[df.index]=df[name]

        GAP=GAP.dropna(how="all", axis=0)
        GAP=GAP.dropna(how="all", axis=1)
        if name in set(GAP.columns):


            GAP["Holiday"]=DB["Holiday"].loc[GAP.index]
            GAP["Weekend"]=DB["Weekend"].loc[GAP.index]
            GAP["Friday"]=DB["Friday"].loc[GAP.index]
            cn=name
            GAP=GAP.sort_values(by=name)
            dtc=GAP.index[0]
            GAP=GAP.dropna(how="all", axis=0)
            GAP=GAP.dropna(how="all", axis=1)
            GAP=GAP[GAP["Holiday"]==GAP["Holiday"].iloc[0]]
            GAP=GAP[GAP["Weekend"]==GAP["Weekend"].iloc[0]]
            GAP=GAP[GAP["Friday"]==GAP["Friday"].iloc[0]]
            if GAP.shape[1]<=3:
                    break
            else:

                GAP=GAP[GAP[cn].isna()]

                GAP=GAP.dropna(how="all")
               
                if GAP.shape[0]==0:

                    continue
                else:

                    gap=GAP.iloc[:, :-3]
                    gap=GAP.iloc[:, :-3]
                    ntct=gap.min().sort_values().index[0]

                    dtct=GAP[ntct].sort_values().index[0] 
                        
                        

                    DB["On call"].loc[dtct],DB["On call"].loc[dtc]=DB["On call"].loc[dtc],DB["On call"].loc[dtct]

            
                        

      
            GAP=Gaps(DB)

            GAP=GAP.iloc[:,6:]
            df=GAP[GAP[name]<Min_gap]
            GAP[name].loc[df.index]=df[name]
            GAP=GAP.dropna(how="all", axis=0)
            GAP=GAP.dropna(how="all", axis=1)

            MIN=GAP.min().min()
 

                
  
         
                        

        else:
            continue
            
    
    

    Names_only=Gaps(DB).iloc[:,6:]
    Names_only=Names_only[Names_only<Min_gap]
    MIN=Names_only.min().min()

    print("Minimum",MIN)


    print()
print(Gaps_n(DB))
    


# In[191]:


gap[gap==gap.min().min()].dropna(how="all", axis=1).dropna(how="all", axis=0)


# In[192]:


GAPS=Gaps(DB).iloc[:,6:].dropna(how="all")
GAPS=GAPS[GAPS<Min_gap]
GAPS=GAPS.dropna(how="all", axis=1)
GAPS=GAPS.dropna(how="all", axis=0)

GAPS


# In[193]:


DB


# In[194]:


Counter(DB).sort_values(by="Holiday")


# In[113]:


DB


# In[ ]:




