import curses
from random import randrange, choice
from collections import defaultdict

class Action(object):
    
    actions = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
    letter_codes = [ord(ch) for ch in 'wasdrqWASDRQ']
    action_dict = dict(zip(letter_codes, actions * 2))
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
    
    def get(self):
        char = 'N'
        while char not in self.action_dict:
            char = self.stdscr.getch()
        return self.action_dict[char]
    

class main(object):

        
    def state_init(self):
        game_field.reset()
        return 'game'
    
    def state_game(self):
        game_field.draw(self.stdscr)       
        action = self.action.get()
        if action == 'Restart':
            return 'init'
        if action == 'Exit':
            return 'exit'
        if game_field.move(action):
            if game_field.is_win():
                return 'win'
            if game_field.is_gameover():
                return 'over'
        return 'game'
     
    def state_win(self):
        game_field.draw(self.stdscr)
        return 'init' if self.action.get() ==  'Restart' else 'exit' 
    
    def state_over(self):
        game_field.draw(self.stdscr)
        return 'init' if self.action.get() ==  'Restart' else 'exit'      
    
    
    def __call__(self, stdscr):
        self.stdscr = stdscr
        self.action = Action(stdscr)
        curses.use_default_colors()
        self.state = 'init'
        while self.state != 'exit':
            self.state = getattr(self, 'state_'+self.state)()


class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height
        self.width = width
        self.win_value = 2048
        self.score = 0
        self.highscore =0
        self.reset()
    
    def spawn(self):
        new_element = 4 if randrange(100) > 89 else 2
        (i,j) = choice([(i,j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element
    
    def reset(self):
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    
    def move(self, direction):
        def move_row_left(row):
            def tighten(row):
                new_row = [i for i in row if i!=0]
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row
            
            def merge(row):
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        new_row.append(2*row[i])
                        self.score += 2 * row[i]
                        pair = False
                    else:
                        if i + 1 < len(row) and row[i] == row[i+1]:
                            pair = True
                            new_row.append(0)
                        else:
                            new_row.append(row[i])
                assert len(new_row) == len(row)
                return new_row
        
            return tighten(merge(tighten(row)))
        

        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))
        
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False
        
    def move_is_possible(self, direction):
        def row_is_left_moveable(row):
            def change(i):
                if row[i] == 0 and row[i+1] != 0:
                    return True
                if row[i] != 0 and row[i+1] == row[i]:
                    return True
                else:
                    return False
            return any(change(i) for i in range(len(row)-1))
        
        check = {}
        check['Left'] = lambda field: any(row_is_left_moveable(row) for row in field)
        check['Right'] = lambda field: check['Left'](invert(field))
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))
        
        if direction in check:
            return check[direction](self.field)
        else:
            return False
    
    def is_win(self):
        return any(any(i >= self.win_value for i in row) for row in self.field)
    
    def is_gameover(self):
        return not any(self.move_is_possible(move) for move in ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit'])
    
    def draw(self, screen):
        help_string1 = '(W)up (S)down (A)Left (D)Right'
        help_string2 = '(R)Restart (Q)Exit'
        gameover_string = 'GAME OVER'
        win_string = 'YOU WIN!'
        def cast(string):
            screen.addstr(string + '\n')
        
        def draw_hor_separator():
            line = '+' + ('+------' * self.width + '+')[1:]
            separator = defaultdict(lambda: line)
            if not hasattr(draw_hor_separator, 'counter'):
                draw_hor_separator.counter = 0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter += 1
        
        def draw_row(row):
            cast( ''.join('| %5d' % num if num > 0 else '|      ' for num in row)+'|')
        
        screen.clear()
        cast('SCORE: ' + str(self.score))
        if 0 != self.highscore:
            cast('HIGHSCORE:' + str(self.highscore))
        
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        
        draw_hor_separator()
        
        if self.is_win():
            cast(win_string)
        
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        
        cast(help_string2)
def transpose(field):
    return [list(row) for row in zip(*field)]
 
def invert(field):
    return [row[::-1] for row in field]
        
if __name__ == '__main__':
    game_field = GameField(win=2048)
    curses.wrapper(main())         
        
