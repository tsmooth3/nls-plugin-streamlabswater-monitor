"""
Ovi Goal Tracker board module implementation.
"""
import json
import logging
import math
import os
import requests

from PIL import Image
from boards.base_board import BoardBase
from data.data import Data
from datetime import datetime, timedelta
from renderer.matrix import Matrix
from pathlib import Path

from . import __board_name__, __description__, __version__

#import values from config.json
config_json_path = Path(__file__).parent / "config.json"
with open(config_json_path, "r", encoding="utf-8") as f:
    _config = json.load(f)

debug = logging.getLogger("scoreboard")

# ---- Main class --------------------------------------------------------------
class StreamLabs(BoardBase):
    """
    The **Ovi Goal Tracker Board** displays Ovechkin's goal count, 
    expected goals, and points.
    """

    def __init__(self, data: Data, matrix: Matrix, sleepEvent):
        super().__init__(data, matrix, sleepEvent)

        # Board metadata from package
        self.board_name = __board_name__
        self.board_version = __version__
        self.board_description = __description__
        self.board_show_points = False

        # Get configuration values with defaults
        self.data = data
        self.matrix = matrix
        self.sleepEvent = sleepEvent
        self.sleepEvent.clear()
        self.streamlabs_token = _config.get("streamlabs_token", "")
        self.barMax = _config.get("barMax", 112)
        self.chartMax = _config.get("chartMax", 260)
        self.historicalDays = _config.get("historicalDays", 30)

        # Resolve paths relative to the plugin directory
        self.board_dir = self._get_board_directory()

        # Access standard application config
        self.font = data.config.layout.font
        self.font.large = data.config.layout.font_large_2
        self.font.medium = data.config.layout.font_medium
        self.font.scroll = data.config.layout.font_xmas

    def _get_board_directory(self):
        """Get the absolute path to this board's directory."""
        import inspect
        board_file = inspect.getfile(self.__class__)
        return os.path.dirname(os.path.abspath(board_file))

    # -------- Rendering --------
    def render(self):
        debug.info("Rendering Ovi Goal Board")

        self.matrix.clear()

        streamlabs_image = Image.open(f'{self.board_dir}/assets/images/streamlabs.png').resize((32,32))
        
        page = 1
        index = 0
        segment = 0
        segmentVol = 0
        dayTotal = 0
        rVols = [] 
        results = []
        bars = []
        morn = (168,246,252)
        day = (55,117,176)
        evening = (99,177,213) 
        maxColor = (242,33,222)
        avgColor = (228,228,0)
        avgyColor = (245,135,0)
        barMax = self.barMax
        chartMax = self.chartMax
       
        now = datetime.today()
        startDate = now - timedelta(days=2,hours=now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
        historicalStartDate = now - timedelta(days=self.historicalDays,hours=now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
        url = "https://api.streamlabswater.com"
        headers = {
            "Authorization" : f"Bearer {self.streamlabs_token}"
        }

        locationId = requests.get(url + "/v1/locations", headers=headers).json()['locations'][0]['locationId']
        hourlyUsageUri = url + "/v1/locations/" + locationId + f"/readings/water-usage?page={page}&groupBy=hour&startTime=" + startDate.astimezone().isoformat()
        res = requests.get(hourlyUsageUri, headers=headers)
        
        historicalUsageUri = url + "/v1/locations/" + locationId + f"/readings/water-usage?page={page}&groupBy=day&startTime=" + historicalStartDate.astimezone().isoformat()
        historicalresults = requests.get(historicalUsageUri, headers=headers).json()['readings']
        
        summaryUri = url + "/v1/locations/" + locationId + "/readings/water-usage/summary"
        summary = requests.get(summaryUri, headers=headers).json()

        results += res.json()['readings']
        while(page < res.json()['pageCount']):
            page += 1
            hourlyUsageUri = url + "/v1/locations/" + locationId + f"/readings/water-usage?page={page}&groupBy=hour&startTime=" + startDate.astimezone().isoformat()
            res = requests.get(hourlyUsageUri, headers=headers)
            results += res.json()['readings']

        self.matrix.draw_rectangle((0,0),(128,64),(32,55,65))
        self.matrix.draw_image((0,-1), streamlabs_image)
        
        for r in results:
            # get the stuff
            rDate = datetime.fromisoformat(r['time'])
            rVol = math.ceil(r['volume'])

            #rDate.hour % 8 = 0
            if rDate.hour % 8 == 0:
                if len(rVols) > 0:
                    segment += 1
                    segmentVol = 0
                    index += 1
                    if segment == 3:
                        segment = 0
                        dayTotal = 0
            rVols.append({'date':rDate,'seg':segment,'vol':0,'dayTotal':0})

            # add the volume to current segment
            segmentVol += rVol
            dayTotal += rVol
            rVols[index]['date']=rDate
            rVols[index]['seg']=segment
            rVols[index]['vol']=segmentVol
            rVols[index]['dayTotal']=dayTotal
    
        avgGaly = summary['thisYear'] / 365 
        avgGal = summary['thisMonth'] / int(datetime.now().day) 
        avgBar = round((avgGal/chartMax)*barMax)
        avgyBar = round((avgGaly/chartMax)*barMax)
        maxGal = max(list(map(lambda x: (math.ceil(x['volume'])), historicalresults)))
        maxBar = round((maxGal/chartMax)*barMax)
        debug.info(f"average: {round(avgGal,2)} - yearAverage: {round(avgGaly,2)} - maxGal: {maxGal} - chartMax: {chartMax}")

        for v in rVols:
            bars.append(round((v['vol']/chartMax)*barMax))

        self.matrix.draw_rectangle((16+maxBar+2,28),(1,36), (242,33,222))
        for i in range(0, len(bars), 3):
            try:
                x1 = bars[i]
            except:
                x1 = 0
    
            try:
                x2 = bars[i+1]
            except:
                x2 = 1
    
            try:
                x3 = bars[i+2]
            except:
                x3 = 2

            y0 = 30 + (i*4)
            
            m_x0 = 16
            d_x0 = 16 + x1 + 1
            e_x0 = 16 + x1 + x2 + 2

            self.matrix.draw_text((3,y0),rVols[i]['date'].strftime("%a")[0:1],font=self.font.medium,fill=(242,242,242))
            self.matrix.draw_rectangle((m_x0,y0),(x1,8),morn)
            self.matrix.draw_rectangle((d_x0,y0),(x2,8),day)
            self.matrix.draw_rectangle((e_x0,y0),(x3,8),evening)
 
        # draw the stuff
        nowVol = math.ceil(summary['today'])
        self.matrix.draw_text((27,1),  "Now".ljust(3) + ":".ljust(2),font=self.font.large,fill=(242,242,242))
        self.matrix.draw_text((54,1),  str(nowVol).ljust(4),font=self.font.large,fill=(242,242,242))
        
        #max 
        self.matrix.draw_rectangle((16+maxBar+2,28),(1,36), maxColor)
        self.matrix.draw_text((27,15), "Max".ljust(3) + ":".ljust(2),font=self.font.large,fill=(242,242,242))
        self.matrix.draw_text((54,15), str(maxGal).ljust(4),font=self.font.large,fill=(242,33,222))
       
        #avg 
        self.matrix.draw_rectangle((16+avgBar+2,28),(0,36), avgColor)
        self.matrix.draw_rectangle((16+avgyBar+2,28),(0,36), avgyColor)
        self.matrix.draw_text((76,1), f"{now.strftime('%b')}:",font=self.font.large,fill=(242,242,242))
        self.matrix.draw_text((104,1), str(round(avgGal)).ljust(3),font=self.font.large,fill=avgColor)
        self.matrix.draw_text((76,15), "A.YR:",font=self.font.large,fill=(242,242,242))
        self.matrix.draw_text((104,15),  str(round(avgGaly)).ljust(4),font=self.font.large,fill=avgyColor)
        
        self.matrix.render()
        self.sleepEvent.wait(30)