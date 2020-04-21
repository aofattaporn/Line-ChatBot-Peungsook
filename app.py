#!/usr/bin/python
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import pandas as pd
import requests
import geopy.distance as ps
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage, FlexSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

app = Flask(__name__)

lineaccesstoken = 'sVi63a9na79V/b+yduVI4yExkvFLcsZGHpCNgiDRnJVNdlWG22i5ICYiEfSmyX3o0ES4ZZ268XYaGETDPlSEu6htUND4nMeICcbHDvUoj3JHlLO0ZQBLh26jgoWOOk6moTB3eRp8U0+wBHbt54SZQwdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(lineaccesstoken)

casedata = pd.read_excel('casedata.xlsx')

####################### new ########################
@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200


def event_handle(event):
    print(event)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "text":
        msg = str(event["message"]["text"])
        replyObj = TextSendMessage(text=msg)
        line_bot_api.reply_message(rtoken, replyObj)

    if msgType == "location":
        lat = event["message"]["latitude"]
        lng = event["message"]["longitude"]
        #txtresult = handle_location(lat,lng,casedata,3)
        result = getcaseflex(lat,lng)
        replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=result)
        line_bot_api.reply_message(rtoken, replyObj)
    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

def flexmessage():
    flex = '''
    {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "https://res.cloudinary.com/hoyixx2q0/image/upload/v1587305042/image_Uc217a79841540c1b0afe06312a885849_1587305039337.jpg.jpg",
          "margin": "none",
          "size": "full",
          "aspectRatio": "1:1",
          "aspectMode": "cover",
          "action": {
            "type": "uri",
            "label": "Action",
            "uri": "https://linecorp.com"
          }
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "spacing": "md",
          "action": {
            "type": "uri",
            "label": "Action",
            "uri": "https://linecorp.com"
          },
          "contents": [
            {
              "type": "text",
              "text": "แคปหมูแม่หญิงลำปาง",
              "size": "xl",
              "weight": "bold"
            },
            {
              "type": "text",
              "text": "กรอบ อร่อย ไม่เหม็นหืน ห่อละ 100 บาท รวมจัดส่งทั่วไทย",
              "wrap": true
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "button",
              "action": {
                "type": "postback",
                "label": "ติดต่อคนขาย",
                "text": "<<shopcontact>>",
                "data": "<<shopcontact>>"
              },
              "color": "#F67878",
              "style": "primary"
            }
          ]
        }
      }'''
    return flex

def handle_text(inpmessage):
    if inpmessage=='ส่ง flex':
        flex = flexmessage()
        replyObj = FlexSendMessage(alt_text='Flex Message alt text', contents=result)
    else:
        replyObj = TextSendMessage(text=inpmessage)
    return replyObj





def handle_location(lat,lng,cdat,topK):
    result = getdistace(lat, lng,cdat)
    result = result.sort_values(by='km')
    result = result.iloc[0:topK]
    txtResult = ''
    for i in range(len(result)):
        kmdistance = '%.1f'%(result.iloc[i]['km'])
        newssource = str(result.iloc[i]['News_Soruce'])
        txtResult = txtResult + 'ห่าง %s กิโลเมตร\n%s\n\n'%(kmdistance,newssource)
    return txtResult[0:-2]


def getcaseflex(lat,lng):
    url = 'http://botnoiflexapi.herokuapp.com/getnearcase?lat=%s&long=%s'%(lat,lng)
    res = requests.get(url).json()
    return res

def getdistace(latitude, longitude,cdat):
  coords_1 = (float(latitude), float(longitude))
  ## create list of all reference locations from a pandas DataFrame
  latlngList = cdat[['Latitude','Longitude']].values
  ## loop and calculate distance in KM using geopy.distance library and append to distance list
  kmsumList = []
  for latlng in latlngList:
    coords_2 = (float(latlng[0]),float(latlng[1]))
    kmsumList.append(ps.vincenty(coords_1, coords_2).km)
  cdat['km'] = kmsumList
  return cdat


if __name__ == '__main__':
    app.run(debug=True)
