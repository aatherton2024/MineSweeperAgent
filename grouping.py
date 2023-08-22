class Grouping():
    """A class that contains methods for gathering information for a group of Minesweeper cells."""
    def __init__(self, cells, num_mine_neighbors):
        self.cells = set(cells)
        self.num_mine_neighbors = num_mine_neighbors
    
    def __eq__(self, sentence2):
        return self.cells == sentence2.cells and self.num_mine_neighbors == sentence2.num_mine_neighbors
    
    def is_mine(self, cell):
        """Updates grouping information if given cell is a mine."""
        if cell in self.cells:
            self.cells.remove(cell)
            self.num_mine_neighbors -= 1
    
    def is_safe(self, cell):
        """Removes safe cells from the group."""
        if cell in self.cells: self.cells.remove(cell)
    
    def all_mines(self):
        """Returns the cells of the grouping if they are all mines.
        Otherwise returns None.

        """
        return self.cells if self.num_mine_neighbors == len(self.cells) else None 
    
    def all_safe(self):
        """Returns the cells of the grouping if they are all safe."""
        return self.cells if not self.num_mine_neighbors else None
    
    def is_empty(self):
        """Returns whether the grouping is empty."""
        return len(self.cells) == 0
    
   