class Sentence():
    """This class describes a Minesweeper sentence.

    It provides all of the necessary methods to determine information about the
    MinesweeperAgent's next move.
    
    """
    def __init__(self, cells, num_mine_neighbors):
        self.cells = set(cells)
        self.num_mine_neighbors = num_mine_neighbors
    
    def __eq__(self, sentence2):
        """Checks logical equality between two sentences."""
        return self.cells == sentence2.cells and self.num_mine_neighbors == sentence2.num_mine_neighbors
    
    def is_mine(self, cell):
        """Deals with a cell that has been determined to be a mine."""
        if cell in self.cells:
            self.cells.remove(cell)
            self.num_mine_neighbors -= 1
    
    def is_safe(self, cell):
        """Removes a cell that has been determined to be safe."""
        if cell in self.cells: self.cells.remove(cell)
    
    def all_mines(self):
        """Returns the cells if they are all bombs, else None."""
        return self.cells if self.num_mine_neighbors == len(self.cells) else None 
    
    def all_safe(self):
        """Returns the cells if they are all safe, else None."""
        return self.cells if not self.num_mine_neighbors else None
    
    def is_empty(self):
        """Returns whether the sentence is empty or not."""
        return len(self.cells) == 0
    
   