import urllib
import csv

#url='https://catalogue.data.govt.nz/dataset/e8fc2893-c60c-46cb-8341-aada40881947/resource/76be4f61-1591-443d-bcac-07eaa587b633/download/celebrant-register-data-2019-04-18.csv'


# -------------------------
# Load data into the stream
# -------------------------

url='https://catalogue.data.govt.nz/dataset/dd726ae7-75a6-43b3-83be-2076a1a77dc6/resource/2c560a20-a003-4ce4-988c-12fda04336d1/download/dog-control-statistics.csv'  
datastream = urllib.urlopen(url)

#datastream=open('dog-control-statistics.csv', 'rb')


# --------------
# Main programm
# --------------
spamreader = csv.reader(datastream, delimiter=',', quotechar='"')
i=0
breeds=dict() # create empty map
for row in spamreader:
  if (i>0):
    breedname = row[2]
    if not breedname in breeds:
      breeds[breedname]=0 # add breed to the map with the default number 0
      
    if (row[3]=='1001_total' and row[4]=='2018'):
      # save in the map. if there was a number from different region, the old number will be lost
      breeds[breedname]=row[5] 
      print row[0]+': '+breedname+' - '+row[5]
  i=i+1

