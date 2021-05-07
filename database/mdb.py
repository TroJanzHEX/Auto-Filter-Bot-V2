#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex


import re
import pymongo

from pymongo.errors import DuplicateKeyError
from marshmallow.exceptions import ValidationError

from config import DATABASE_URI, DATABASE_NAME


myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]



async def savefiles(docs, group_id):
    mycol = mydb[str(group_id)]
    
    try:
        mycol.insert_many(docs, ordered=False)
    except Exception:
        pass


async def channelgroup(channel_id, channel_name, group_id, group_name):
    mycol = mydb["ALL DETAILS"]

    channel_details = {
        "channel_id" : channel_id,
        "channel_name" : channel_name
    }

    data = {
        '_id': group_id,
        'group_name' : group_name,
        'channel_details' : [channel_details],
    }
    
    if mycol.count_documents( {"_id": group_id} ) == 0:
        try:
            mycol.insert_one(data)
        except:
            print('Some error occured!')
        else:
            print(f"files in '{channel_name}' linked to '{group_name}' ")
    else:
        try:
            mycol.update_one({'_id': group_id},  {"$push": {"channel_details": channel_details}})
        except:
            print('Some error occured!')
        else:
            print(f"files in '{channel_name}' linked to '{group_name}' ")


async def ifexists(channel_id, group_id):
    mycol = mydb["ALL DETAILS"]

    query = mycol.count_documents( {"_id": group_id} )
    if query == 0:
        return False
    else:
        ids = mycol.find( {'_id': group_id} )
        channelids = []
        for id in ids:
            for chid in id['channel_details']:
                channelids.append(chid['channel_id'])

        if channel_id in channelids:
            return True
        else:
            return False


async def deletefiles(channel_id, channel_name, group_id, group_name):
    mycol1 = mydb["ALL DETAILS"]

    try:
        mycol1.update_one(
            {"_id": group_id},
            {"$pull" : { "channel_details" : {"channel_id":channel_id} } }
        )
    except:
        pass

    mycol2 = mydb[str(group_id)]
    query2 = {'channel_id' : channel_id}
    try:
        mycol2.delete_many(query2)
    except:
        print("Couldn't delete channel")
        return False
    else:
        print(f"filters from '{channel_name}' deleted in '{group_name}'")
        return True


async def deletealldetails(group_id):
    mycol = mydb["ALL DETAILS"]

    query = { "_id": group_id }
    try:
        mycol.delete_one(query)
    except:
        pass


async def deletegroupcol(group_id):
    mycol = mydb[str(group_id)]

    if mycol.count() == 0:
        return 1

    try:    
        mycol.drop()
    except Exception as e:
        print(f"delall group col drop error - {str(e)}")
        return 2
    else:
        return 0


async def channeldetails(group_id):
    mycol = mydb["ALL DETAILS"]

    query = mycol.count_documents( {"_id": group_id} )
    if query == 0:
        return False
    else:
        ids = mycol.find( {'_id': group_id} )
        chdetails = []
        for id in ids:
            for chid in id['channel_details']:
                chdetails.append(
                    str(chid['channel_name']) + " ( <code>" + str(chid['channel_id']) + "</code> )"
                )
            return chdetails


async def countfilters(group_id):
    mycol = mydb[str(group_id)]

    query = mycol.count()

    if query == 0:
        return False
    else:
        return query

        
async def findgroupid(channel_id):
    mycol = mydb["ALL DETAILS"]

    ids = mycol.find()
    groupids = []
    for id in ids:
        for chid in id['channel_details']:
            if channel_id == chid['channel_id']:
                groupids.append(id['_id'])
    return groupids


async def searchquery(group_id, name):

    mycol = mydb[str(group_id)]

    filenames = []
    filelinks = []

    # looking for a better regex :(
    pattern = name.lower().strip().replace(' ','.*')
    raw_pattern = r"\b{}\b".format(pattern)
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)

    query = mycol.find( {"file_name": regex} )
    for file in query:
        filename = "[" + str(file['file_size']//1048576) + "MB] " + file['file_name']
        filenames.append(filename)
        filelink = file['link']
        filelinks.append(filelink)
    return filenames, filelinks


