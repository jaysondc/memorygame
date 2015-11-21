# Implementation of the card game - Memory
# Made by Jayson Dela Cruz
# 11/21/2015

import simplegui
import random

CARD_SIZE = [75, 100] 
CARD_FONT_SIZE = 32
CARD_MARGIN = 15
SCORE_MARGIN = 25
COLUMNS = 4
NUM_PAIRS = 8

class Memory_Game:
    def __init__(self, numpairs, card_size, columns):
        # Set board width, height
        self.width = (card_size[0] * columns) + (CARD_MARGIN * columns + CARD_MARGIN)
        numrows = (numpairs * 2)/columns
        if (numpairs * 2)%columns > 0:
            numrows += 1
        self.height = (card_size[1] * numrows) + (CARD_MARGIN * numrows + CARD_MARGIN) + SCORE_MARGIN
        
        # Create the frame and buttons
        self.frame = simplegui.create_frame("Memory", self.width, self.height)
        self.frame.add_button("Reset", self.reset_game)
        
        # Set cards
        self.numpairs = numpairs
        self.card_size = card_size
        self.columns = columns
        self.cards = Cards(self.numpairs, self.card_size, self.columns)
        
        # Set scoreboard
        self.scoreboard = Scoreboard()
        
        # Register event handlers
        self.frame.set_mouseclick_handler(self.on_mouseclick)
        self.frame.set_draw_handler(self.draw)

        # Start the frame
        self.frame.start()
    
    
    def new_game(self):
        self.cards = Cards(self.numpairs, self.card_size, self.columns)
        self.scoreboard.reset()
    def reset_game(self):
        self.new_game()
    def on_mouseclick(self, pos):
        scoreupdate = self.cards.click(pos)
        self.scoreboard.update_score(scoreupdate[0], scoreupdate[1])
        if self.scoreboard.check_win(self.numpairs):
            self.cards.set_state(3)
            print "YOU WON!"
        
    def draw(self, canvas):
        self.cards.draw(canvas, self.frame, self.width, self.height)
        self.scoreboard.draw(canvas)
        pass
    
    
class Cards:
    def __init__(self, numpairs, cardsize, cols):
        self.pairs = numpairs
        self.card_size = cardsize
        self.columns = cols
        self.deck = self.createdeck()
        self.gamestate = 0
        
        # Test print deck
        for card in self.deck:
            print "Card " + str(card.get_value())
    
    def createdeck(self):
        # Create identical sets of cards
        deck = [Card(x) for x in range(self.pairs)]
        deck2 = [Card(x) for x in range(self.pairs)]
        # Combine into one deck and shuffle
        deck.extend(deck2)
        random.shuffle(deck)
        
        # Assign size and position to each card
        column = 0
        card_in_row = 0
        card_row = 0
        score_margin = SCORE_MARGIN
        card_margin = CARD_MARGIN
        card_start = [card_margin, card_margin + score_margin] # replace after each card is placed
        
        for i in range(len(deck)):
            # Move card starting point
            # Increment cardstart vertical if end of row
            if card_in_row >= self.columns:
                card_in_row = 0
                card_row += 1
                # Reset to left and move one row down
                card_start[0] = card_margin
                card_start[1] += self.card_size[1] + card_margin
            
            # Set card corners
            topleft = [card_start[0], 
                       card_start[1]] #[10, 10]
            topright = [(card_start[0] + self.card_size[0]), 
                        card_start[1]] #60, 10
            bottomright = [(card_start[0] + self.card_size[0]), 
                           (card_start[1] + self.card_size[1])] #60, 60
            bottomleft = [card_start[0], 
                          (card_start[1] + self.card_size[1])] #10, 60
            
            # Set card position
            points = [topleft, topright, bottomright, bottomleft]
            deck[i].set_points(points)
            
            # Increment card_in_row
            card_in_row += 1
            # Increment cardstart horizontal
            card_start[0] += self.card_size[0] + card_margin
            
        return deck
    
    def click(self, pos):
        # Game logic for clicks and states
        '''
        ' State 0 - No cards selected
        ' State 1 - 1 card selected
        ' State 2 - 2 cards selected, clicking a 3rd card will end the turn
        ' State 3 - Win condition
        '
        ' Returns [points, turns]
        '''
        
        if self.gamestate == 0:
            for card in self.deck:
                if card.is_clicked(pos):
                    self.card1 = card
                    card.show()
                    self.set_state(1)
            return [0,0]
        elif self.gamestate == 1:
            for card in self.deck:
                if card.is_clicked(pos) and card.is_shown() == False:
                    self.card2 = card
                    card.show()
                    # increment points and grey out both cards
                    if self.card1.get_value() == self.card2.get_value():
                        self.card1.set_found()
                        self.card2.set_found()
                        self.set_state(2)
                        return [1,1] # add point
                    else:
                        self.set_state(2)
                        return [0,1]
            # If nothing is clicked
            return [0,0]
        elif self.gamestate == 2:
            for card in self.deck:
                if card.is_clicked(pos) and card.is_shown() == False:
                    # Hide previous cards if they aren't a match
                    if self.card1.is_found() == False:
                        self.card1.hide()
                        self.card2.hide()
                    # Select new card
                    self.card1 = card
                    card.show()
                    self.set_state(1)
                    return [0,0]
            # If nothing is clicked
            return [0,0]
        else: #self.gamestate ==3:
            return [0,0]
        
    def set_state(self, state):
        self.gamestate = state
    
    def draw(self, canvas, frame, canvaswidth, canvasheight):
        # Lay out cards based on position and state
        for card in self.deck:
            card.draw_card(canvas, frame)
            
        if self.gamestate == 3:
            text_width = frame.get_canvas_textwidth("YOU WON!", 64)
            offset_h = canvaswidth/2 - (text_width/2)
            offset_v = canvasheight/2 + (64/3)
            
            canvas.draw_text("YOU WON!", [offset_h, offset_v], 64, "Yellow")
        

class Card:
    def __init__(self, val):
        self.value = val
        self.shown = False
        self.found = False
        self.color = "Green"
    
    def get_value(self):
        return self.value
    
    def get_points(self):
        return self.pointlist
    
    def set_points(self, points):
        self.pointlist = points
    
    def draw_card(self, canvas, frame):
        # Draw card based on self contained state and value
        if self.shown and self.found == False:
            canvas.draw_polygon(self.pointlist, 5, "White", "White")
            canvas.draw_text(str(self.value), self.get_text_pos(frame), CARD_FONT_SIZE, "Black")
        elif self.shown and self.found == True:
            canvas.draw_polygon(self.pointlist, 5, "Gray", "Gray")
            canvas.draw_text(str(self.value), self.get_text_pos(frame), CARD_FONT_SIZE, "Black")
        else:
            canvas.draw_polygon(self.pointlist, 5, "Green", "Green")
    
    def get_text_pos(self, frame):
        # Return a point to start drawing text
        text_width = frame.get_canvas_textwidth(str(self.value), CARD_FONT_SIZE)
        offset_h = CARD_SIZE[0]/2 - (text_width/2)
        offset_v = CARD_SIZE[1]/2 + (CARD_FONT_SIZE/3)
        text_h = self.pointlist[0][0] + offset_h
        text_v = self.pointlist[0][1] + offset_v
        return [text_h, text_v]
                             
    def show(self):
        self.shown = True
    
    def hide(self):
        self.shown = False
        
    def set_found(self):
        self.found = True
    
    def is_shown(self):
        return self.shown
    
    def is_found(self):
        return self.found
    
    def is_clicked(self, point):
        # Check if a this card is clicked
        if point[0] > self.pointlist[0][0] and point[0] < self.pointlist[1][0]: # Horizontal check
            if point[1] > self.pointlist[1][1] and point[1] < self.pointlist[2][1]: # Vertical check
                return True
            
        return False
    
class Scoreboard:
    def __init__(self):
        self.score = 0
        self.turns = 0
        
    def draw(self, canvas):
        canvas.draw_text("Turn: " + str(self.turns) + "    Score: " + str(self.score),
                         [10,25], 20, "White")
    
    def update_score(self, scoreadd, turnsadd):
        self.score += scoreadd
        self.turns += turnsadd
    
    def check_win(self, numpairs):
        return self.score >= numpairs
    
    def reset(self):
        self.score = 0
        self.turns = 0
    
# get things rolling
memory = Memory_Game(NUM_PAIRS, CARD_SIZE, COLUMNS)
