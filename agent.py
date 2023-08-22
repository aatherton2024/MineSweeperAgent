from abc import ABC, abstractmethod
import math
import cnf
import copy
from dpll import dpll
import random
from grouping import Grouping


class MinesweeperMove(ABC):
    """Abstract base class for moves that a MinesweeperAgent can make during a game."""


class RandomReveal(MinesweeperMove):
    """Requests the Minesweeper game to press the parachute button, i.e. reveal a non-mine cell at random.
    """

    def __init__(self):
        pass

    def __eq__(self, other):
        return type(other) == RandomReveal


class Reveal(MinesweeperMove):
    """Requests the Minesweeper game to reveal the cell in the specified row and column.

    Rows and columns are specified num_mine_neighborsing from zero. The upper left cell of the Minesweeper board
    is in row 0 and column 0.
    """

    def __init__(self, row, column):
        self.row, self.column = row, column

    def __eq__(self, other):
        return (type(other).__name__ == Reveal
                and self.row == other.row
                and self.column == other.column)


class MinesweeperAgent(ABC):

    def __init__(self, num_rows, num_columns, num_mines):
        """Constructs a MinesweeperAgent designed to play a game with the specified grid.

        Parameters
        ----------
        num_rows : int
            The number of rows in the Minesweeper grid
        num_columns : int
            The number of columns in the Minesweeper grid
        num_mines : int
            The number of mines in the Minesweeper grid

        """
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.num_mines = num_mines

    @abstractmethod
    def report(self, row, column, num_mine_neighbors):
        """Informs the agent about the number of cell neighbors containing a mine.

        The cell is specified by its (row, column) coordinates, num_mine_neighborsing from 0.
        For instance, (0, 0) is the upper left cell of the Minesweeper board.

        A neighbor is any cell that is adjacent (including diagonally adjacent).
        Therefore, a cell can have up to 8 neighbors.

        Parameters
        ----------
        row : int
            The cell's row (num_mine_neighborsing from 0)
        column : int
            The cell's column (num_mine_neighborsing from 0)
        num_mine_neighbors : int
            The number of neighbors of the cell containing a mine

        """

    @abstractmethod
    def next_move(self):
        """Returns the next cell to reveal on a given Minesweeper board.

        Returns
        ----------
        (int, int)
            The (row, column) coordinates of the next cell that the agent wants to reveal.

        """

class NotSoGoodAgent(MinesweeperAgent):
    """A MinesweeperAgent who plays rather poorly.

    90% of the time, this agent just pushes the parachute button. The other 10% of the time,
    the agent reveals the unrevealed cell that is closest to the upper left (i.e. proceeding
    left-to-right through each row, until an unrevealed cell is found).

    """
    def __init__(self, num_rows, num_columns, num_mines):
        super().__init__(num_rows, num_columns, num_mines)
        self.unrevealed = set()
        for row in range(num_rows):
            for col in range(num_columns):
                self.unrevealed.add((row, col))

    def report(self, row, column, num_mine_neighbors):
        """Removes the reported cell from the agent's list of unrevealed cells."""
        self.unrevealed.remove((row, column))

    def next_move(self):
        """Executes the agent's not so good strategy."""
        if random.random() < 0.1 and len(self.unrevealed) > 0:
            row, col = sorted(self.unrevealed)[0]
            return Reveal(row, col)
        else:
            return RandomReveal()


class BetterAgent(MinesweeperAgent):
    """A MinesweeperAgent who plays better than NotSoGoodAgent.

    It keeps track of the state of the board after each move,
    in order to decide what it should do next.

    """
    def __init__(self, num_rows, num_columns, num_mines):
        super().__init__(num_rows, num_columns, num_mines)
        self.revealed = set()
        self.safe = set()
        self.flagged = set()
        self.groupings = []
    
    def find_neighbors(self, row, column, num_mine_neighbors):
        """A helper method that finds and gathers information about a given cells neighboring cells."""
        # mark cell safe in each grouping
        for grouping in self.groupings: grouping.is_safe((row, column))

        self.safe.add((row, column))
        self.revealed.add((row, column))
        new_set = set()

        for r in range(row - 1, row + 2): # set row boundary
            for c in range(column - 1, column + 2): # set col boundary
                # check that neighboring cell exists
                if (r, c) == (row, column) or r < 0 or c < 0 or r >= self.num_rows or c >= self.num_columns: continue
                if (r, c) in self.flagged: num_mine_neighbors -= 1
                elif (r, c) not in self.revealed: new_set.add((r, c))             
        # create new grouping with unrevealed and unflagged cells
        self.groupings.append(Grouping(new_set, num_mine_neighbors))
    
    def prune_groupings(self):
        """A helper method that prunes the groupings based on information about the cells in the groups."""
        
        for grouping in self.groupings:
            # remove empty groupings
            if grouping.is_empty():
                self.groupings.remove(grouping)
                continue

            # if the grouping is all bombs, flag all cells
            elif grouping.all_mines() is not None:     
                self.groupings.remove(grouping)
                self.flagged.union(grouping.all_mines())
                for bomb in grouping.all_mines().copy():
                    for grouping in self.groupings: grouping.is_mine(bomb)
                    self.flagged.add(bomb)
                continue
                    
            # if the grouping is all safe, mark all as safe
            elif grouping.all_safe() is not None:
                self.groupings.remove(grouping)
                self.safe.union(grouping.all_safe())
                for s in grouping.all_safe().copy():
                    for grouping in self.groupings: grouping.is_safe(s)
                    self.safe.add(s)
                continue
            
            for grouping2 in self.groupings:
                # remove duplicate groupings
                if grouping is not grouping2 and grouping == grouping2: self.groupings.remove(grouping2)
                # create new grouping of unmarked cells
                elif grouping is not grouping2 and all(el in grouping2.cells for el in grouping.cells):
                    new_cells = grouping2.cells.difference(grouping.cells)
                    new_num_mine_neighbors = grouping2.num_mine_neighbors - grouping.num_mine_neighbors
                    new_sent = Grouping(new_cells, new_num_mine_neighbors)
                    if new_sent not in self.groupings: self.groupings.append(new_sent)


    def report(self, row, column, num_mine_neighbors):
        """Removes the reported cell from the agent's list of unrevealed cells.
        Gives the agent information regarding the cell and it's neighbors.

        """      

        self.find_neighbors(row, column, num_mine_neighbors)
        self.prune_groupings()       

    def next_move(self):
        """Executes a random move from the list of safe moves that have not been executed."""

        if self.safe - self.revealed:  # check that there is a safe move to make
            # make a safe move
            row, col = list(self.safe - self.revealed)[0]
            return Reveal(row, col)
        
        # if there aren't any safe moves, hit the parachute button
        return RandomReveal()

def initialize_agent(num_rows, num_columns, num_mines):
    """Initializes the agent who will play Minesweeper."""
    
    return BetterAgent(num_rows, num_columns, num_mines)
