from PIL import Image, ImageFont, ImageDraw, ImageSequence
from rgbmatrix import graphics
from utils import center_text
from calendar import month_abbr
from renderer.screen_config import screenConfig
from datetime import datetime, timedelta
import time as t
import debug
import re

class MainRenderer:
    def __init__(self, matrix, data):
        self.matrix = matrix
        self.data = data
        self.screen_config = screenConfig("64x32_config")
        self.canvas = matrix.CreateFrameCanvas()
        self.width = 64
        self.height = 32
        # Create a new data image.
        self.image = Image.new('RGB', (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        # Load the fonts
        self.font = ImageFont.truetype("fonts/score_large.otf", 16)
        self.font_mini = ImageFont.truetype("fonts/04B_24__.TTF", 8)
        self.gametime = datetime.strptime(self.data.game['date'], "%Y-%m-%dT%H:%MZ")

    def render(self):
        # we're in turbo lazy playoff mode right now don't @ me
        while True:
            self.data.get_current_date()
            if self.data.game['state'] == "in":
                self._draw_game()
            else:
                self.__render_game()

    def __render_game(self):
        time = self.data.get_current_date()
        if time < self.gametime - timedelta(hours=2) and self.data.game['state'] == 'pre':
            debug.info('Scheduled State, waiting 30')
            self._draw_pregame()
            t.sleep(1800)
        elif time < self.gametime - timedelta(hours=1) and self.data.game['state'] == 'pre':
            debug.info('Pre-Game State, waiting 1 minute')
            self._draw_pregame()
            t.sleep(60)
        elif time < self.gametime and self.data.game['state'] == 'pre':
            debug.info('Countdown til gametime')
            self._draw_countdown()
        elif self.data.game['state'] == 'post':
            debug.info('Final State, waiting 6 hours')
            self._draw_post_game()
            t.sleep(3600)
        else:
            debug.info('Live State, checking every 5s')
            self._draw_game()
        debug.info('ping render_game')

    def __render_off_day(self):
        debug.info('ping_day_off')
        self._draw_off_day()
        t.sleep(21600) #sleep 6 hours

    def _draw_countdown(self):
        time = self.data.get_current_date()
        if time < self.gametime:
            print(self.gametime - time)
            overview = self.data.game
            gametime = self.gametime - time
            # as beautiful as I am
            if gametime > timedelta(hours=1):
                gametime = ':'.join(str(self.gametime - time).split(':')[:2])
            else:
                gametime = ':'.join(str(self.gametime - time).split(':')[1:]).split('.')[:1][0]
            # Center the game time on screen.
            gametime_pos = center_text(self.font_mini.getsize(gametime)[0], 32)
            awaysize = self.screen_config.team_logos_pos[overview['awayteam']]['size']
            homesize = self.screen_config.team_logos_pos[overview['hometeam']]['size']
            # Set the position of each logo
            away_team_logo_pos = self.screen_config.team_logos_pos[overview['awayteam']]['preaway']
            home_team_logo_pos = self.screen_config.team_logos_pos[overview['hometeam']]['prehome']
            # Open the logo image file
            away_team_logo = Image.open('logos/{}.png'.format(overview['awayteam'])).resize((19, 19), 1)
            home_team_logo = Image.open('logos/{}.png'.format(overview['hometeam'])).resize((19, 19), 1)
            # Draw the text on the Data image.
            self.draw.text((29, 0), 'IN', font=self.font_mini)
            self.draw.multiline_text((gametime_pos, 6), gametime, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.text((25, 15), 'VS', font=self.font)
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
            t.sleep(1)

    def _draw_pregame(self):
        if self.data.game != 0:
            overview = self.data.game
            gametime = self.data.gametime
            # Center the game time on screen.
            gametime_pos = center_text(self.font_mini.getsize(gametime)[0], 32)
            awaysize = self.screen_config.team_logos_pos[overview['awayteam']]['size']
            homesize = self.screen_config.team_logos_pos[overview['hometeam']]['size']
            # Set the position of each logo
            away_team_logo_pos = self.screen_config.team_logos_pos[overview['awayteam']]['preaway']
            home_team_logo_pos = self.screen_config.team_logos_pos[overview['hometeam']]['prehome']
            # Open the logo image file
            away_team_logo = Image.open('logos/{}.png'.format(overview['awayteam'])).resize((19, 19), 1)
            home_team_logo = Image.open('logos/{}.png'.format(overview['hometeam'])).resize((19, 19), 1)
            # Draw the text on the Data image.
            self.draw.text((22, -1), 'TODAY', font=self.font_mini)
            self.draw.multiline_text((gametime_pos, 5), gametime, fill=(255, 255, 255), font=self.font_mini, align="center")
            self.draw.text((25, 15), 'VS', font=self.font)
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            #(Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            t.sleep(60)  # sleep for 1 min
            # Refresh canvas
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)

    def _draw_game(self):
        # self.data.refresh_game()
        overview = self.data.game
        homescore = overview['homescore']
        awayscore = overview['awayscore']
        i = 5
        while True:
            # Refresh the data
            if self.data.needs_refresh:
                debug.info('Refresh game overview')
                self.data.refresh_game()
                self.data.needs_refresh = False
            if self.data.game != 0:
                overview = self.data.game
                # Use This code if you want the goal animation to run only for your fav team's goal
                # if self.data.fav_team_id == overview['hometeam']:
                #     if overview['homescore'] > homescore:
                #         self._draw_goal()
                # else:
                #     if overview['awayscore'] > awayscore:
                #         self._draw_goal()
                # Use this code if you want the goal animation to run for both team's goal.
                # Run the goal animation if there is a goal.
                if overview['homescore'] > homescore + 5 or overview['awayscore'] > awayscore + 5:
                   self._draw_td()
                elif overview['homescore'] > homescore + 2 or overview['awayscore'] > awayscore + 2:
                   self._draw_fg()
                # Prepare the data
                score = '{}-{}'.format(overview['awayscore'], overview['homescore'])
                if overview['possession'] == overview['awayid']:
                    pos = overview['awayteam']
                else:
                    pos = overview['hometeam']
                quarter = str(overview['quarter'])
                time_period = overview['time']
                # this is ugly but I want to replace the possession info with down info and spot info
                down = None
                spot = None
                game_info = None
                if overview['down']:
                    down = re.sub(r"[a-z]+", "", overview['down']).replace(" ", "")
                if overview['spot']:
                    spot = overview['spot'].replace(" ", "")
                pos_colour = (255, 255, 255)
                if i == 3 and pos:
                    game_info = pos
                    i = 5
                    if overview['redzone']:
                        pos_colour = (255, 25, 25)
                elif i == 5 and down:
                    game_info = down
                    i = 2
                elif i == 2 and spot:
                    game_info = spot
                    i = 3
                else:
                    i = 5
                # Set the position of the information on screen.
                time_period_pos = center_text(self.font_mini.getsize(time_period)[0], 32)
                score_position = center_text(self.font.getsize(score)[0], 32)
                quarter_position = center_text(self.font_mini.getsize(quarter)[0], 32)
                if game_info:
                    info_pos = center_text(self.font_mini.getsize(game_info)[0], 32)
                    self.draw.multiline_text((info_pos, 12), game_info, fill=pos_colour, font=self.font_mini, align="center")
                # Set the position of each logo on screen.
                awaysize = self.screen_config.team_logos_pos[overview['awayteam']]['size']
                homesize = self.screen_config.team_logos_pos[overview['hometeam']]['size']
                # Set the position of each logo
                away_team_logo_pos = self.screen_config.team_logos_pos[overview['awayteam']]['away']
                home_team_logo_pos = self.screen_config.team_logos_pos[overview['hometeam']]['home']
                # Open the logo image file
                away_team_logo = Image.open('logos/{}.png'.format(overview['awayteam'])).resize((19, 19), 1)
                home_team_logo = Image.open('logos/{}.png'.format(overview['hometeam'])).resize((19, 19), 1)
                # Draw the text on the Data image.
                self.draw.multiline_text((quarter_position, 0), quarter, fill=(255, 255, 255), font=self.font_mini, align="center")
                self.draw.multiline_text((time_period_pos, 6), time_period, fill=(255, 255, 255), font=self.font_mini, align="center")
                self.draw.multiline_text((score_position, 19), score, fill=(255, 255, 255), font=self.font, align="center")
                # Put the data on the canvas
                self.canvas.SetImage(self.image, 0, 0)
                # Put the images on the canvas
                self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
                self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])
                # Load the canvas on screen.
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                # Refresh the Data image.
                self.image = Image.new('RGB', (self.width, self.height))
                self.draw = ImageDraw.Draw(self.image)
                # Check if the game is over
                if overview['state'] == 'post':
                    debug.info('GAME OVER')
                    break
                # Save the scores.
                awayscore = overview['awayscore']
                homescore = overview['homescore']
                self.data.needs_refresh = True
                t.sleep(i)
            else:
                # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
                self.draw.line((0, 0) + (self.width, 0), fill=128)
                self.canvas = self.matrix.SwapOnVSync(self.canvas)
                t.sleep(60)  # sleep for 1 min

    def _draw_post_game(self):
        self.data.refresh_game()
        if self.data.game != 0:
            overview = self.data.game
            # Prepare the data
            score = '{}-{}'.format(overview['awayscore'], overview['homescore'])
            # Set the position of the information on screen.
            score_position = center_text(self.font.getsize(score)[0], 32)
            # awaysize = self.screen_config.team_logos_pos[overview['hometeam']]['size']
            # homesize = self.screen_config.team_logos_pos[overview['awayteam']]['size']
            awaysize = self.screen_config.team_logos_pos[overview['awayteam']]['size']
            homesize = self.screen_config.team_logos_pos[overview['hometeam']]['size']
            # Set the position of each logo
            # away_team_logo_pos = self.screen_config.team_logos_pos[overview['hometeam']]['away']
            # home_team_logo_pos = self.screen_config.team_logos_pos[overview['awayteam']]['home']
            away_team_logo_pos = self.screen_config.team_logos_pos[overview['awayteam']]['away']
            home_team_logo_pos = self.screen_config.team_logos_pos[overview['hometeam']]['home']
            # Open the logo image file
            # away_team_logo = Image.open('logos/{}.png'.format(overview['hometeam'])).resize((awaysize, awaysize), 1)
            # home_team_logo = Image.open('logos/{}.png'.format(overview['awayteam'])).resize((homesize, homesize), 1)
            away_team_logo = Image.open('logos/{}.png'.format(overview['awayteam'])).resize((19, 19), 1)
            home_team_logo = Image.open('logos/{}.png'.format(overview['hometeam'])).resize((19, 19), 1)
            # Draw the text on the Data image.
            self.draw.multiline_text((score_position, 19), score, fill=(255, 255, 255), font=self.font, align="center")
            self.draw.multiline_text((26, 0), "END", fill=(255, 255, 255), font=self.font_mini,align="center")
            # Put the data on the canvas
            self.canvas.SetImage(self.image, 0, 0)
            # Put the images on the canvas
            self.canvas.SetImage(away_team_logo.convert("RGB"), away_team_logo_pos["x"], away_team_logo_pos["y"])
            self.canvas.SetImage(home_team_logo.convert("RGB"), home_team_logo_pos["x"], home_team_logo_pos["y"])
            # Load the canvas on screen.
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            # Refresh the Data image.
            self.image = Image.new('RGB', (self.width, self.height))
            self.draw = ImageDraw.Draw(self.image)
        else:
            # (Need to make the screen run on it's own) If connection to the API fails, show bottom red line and refresh in 1 min.
            self.draw.line((0, 0) + (self.width, 0), fill=128)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            t.sleep(60)  # sleep for 1 min

    def _draw_td(self):
        debug.info('TD')
        # Load the gif file
        ball = Image.open("sssets/td_ball.gif")
        words = Image.open("sssets/td_words.gif")
        # Set the frame index to 0
        frameNo = 0
        self.canvas.Clear()
        # Go through the frames
        x = 0
        while x is not 3:
            try:
                ball.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                ball.seek(frameNo)
            self.canvas.SetImage(ball.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            t.sleep(0.05)

        x = 0
        while x is not 3:
            try:
                words.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                words.seek(frameNo)
            self.canvas.SetImage(words.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            t.sleep(0.05)

    def _draw_fg(self):
        debug.info('FG')
        # Load the gif file
        im = Image.open("assets/fg.gif")
        # Set the frame index to 0
        frameNo = 0
        self.canvas.Clear()
        # Go through the frames
        x = 0
        while x is not 3:
            try:
                im.seek(frameNo)
            except EOFError:
                x += 1
                frameNo = 0
                im.seek(frameNo)
            self.canvas.SetImage(im.convert('RGB'), 0, 0)
            self.canvas = self.matrix.SwapOnVSync(self.canvas)
            frameNo += 1
            t.sleep(0.05)

    def _draw_off_day(self):
        self.draw.text((0, -1), 'NO GAME TODAY', font=self.font_mini)
        self.canvas.SetImage(self.image, 0, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)