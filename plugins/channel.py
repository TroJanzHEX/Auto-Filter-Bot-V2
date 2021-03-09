#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @trojanzhex


import re
import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant

from bot import Bot
from database.mdb import (
    savefiles,
    deletefiles,
    deletegroupcol,
    channelgroup,
    ifexists,
    deletealldetails
)



@Client.on_message(filters.group & filters.command(["add"]))
async def addchannel(client: Bot, message: Message):

    cmd, chid = message.text.split(" ", 1)

    try:
        invitelink = await client.export_chat_invite_link(chid)
    except:
        await message.reply_text(
            "<i>Add me as admin in your channel with admin rights - 'Invite Users via Link' and try again</i>",
        )
        return

    try:
        user = await client.USER.get_me()
    except:
        user.first_name =  " "

    try:
        await client.USER.join_chat(invitelink)
    except UserAlreadyParticipant:
        pass
    except Exception as e:
        print(e)
        await message.reply_text(
            f"<i>User {user.first_name} couldn't join your channel! Make sure user is not banned in channel."
            "\n\nOr manually add the user to your channel and try again</i>",
        )
        return

    try:
        chatdetails = await client.USER.get_chat(chid)
    except:
        await message.reply_text(
            "<i>Send a message to your channel and try again</i>"
        )
        return

    intmsg = await message.reply_text(
        "<i>Please wait while I'm adding your channel files to DB</i>"
    )

    channel_id = chatdetails.id
    channel_name = chatdetails.title
    group_id = message.chat.id
    group_name = message.chat.title

    already_added = await ifexists(channel_id, group_id)
    if already_added:
        await intmsg.edit_text("Channel already added to db!")
        return

    docs = []
    try:
        async for msg in client.USER.search_messages(channel_id,filter='document'):
            file_name = msg.document.file_name
            file_id = msg.document.file_id                    
            link = msg.link
            data = {
                '_id': file_id,
                'channel_id' : channel_id,
                'file_name': file_name,
                'link': link
            }
            docs.append(data)
    except:
        pass

    try:
        async for msg in client.USER.search_messages(channel_id,filter='video'):
            file_name = msg.video.file_name
            file_id = msg.video.file_id                    
            link = msg.link
            data = {
                '_id': file_id,
                'channel_id' : channel_id,
                'file_name': file_name,
                'link': link
            }
            docs.append(data)
    except:
        pass

    if docs:
        await savefiles(docs, group_id)
    else:
        await intmsg.edit_text("Channel couldn't be added. Try after some time!")
        return

    await channelgroup(channel_id, channel_name, group_id, group_name)

    await intmsg.edit_text("Channel added successfully!")


@Client.on_message(filters.group & filters.command(["del"]))
async def deletechannelfilters(client: Bot, message: Message):

    cmd, chid = message.text.split(" ", 1)

    try:
        chatdetails = await client.USER.get_chat(chid)
    except:
        await message.reply_text(
            "<i>User must be present in given channel.\n\n"
            "If user is already present, send a message to your channel and try again</i>"
        )
        return

    intmsg = await message.reply_text(
        "<i>Please wait while I'm deleteing your channel</i>"
    )

    channel_id = chatdetails.id
    channel_name = chatdetails.title
    group_id = message.chat.id
    group_name = message.chat.title

    already_added = await ifexists(channel_id, group_id)
    if not already_added:
        await intmsg.edit_text("That channel is not currently added in db!")
        return

    delete_files = await deletefiles(channel_id, channel_name, group_id, group_name)
    
    if delete_files:
        await intmsg.edit_text(
            "Channel deleted successfully!"
        )
    else:
        await intmsg.edit_text(
            "Couldn't delete Channel"
        )

@Client.on_message(filters.group & filters.command(["delall"]))
async def deleteallfilters(client: Bot, message: Message):

    intmsg = await message.reply_text(
        "<i>Please wait while I'm deleteing your channel</i>"
    )

    group_id = message.chat.id

    await deletealldetails(group_id)

    delete_all = await deletegroupcol(group_id)

    if delete_all == 0:
        await intmsg.edit_text(
            "All filters from group deleted successfully!"
        )
    elif delete_all == 1:
        await intmsg.edit_text(
            "Nothing to delete!!"
        )
    elif delete_all == 2:
        await intmsg.edit_text(
            "Couldn't delete filters. Try again after sometime.."
        )  
