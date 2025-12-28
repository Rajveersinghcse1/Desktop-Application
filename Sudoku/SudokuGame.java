package Sudoku;
import javax.swing.*;
import javax.swing.text.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

public class SudokuGame extends JFrame {

    private JTextField[][] sudokuGrid = new JTextField[9][9];

    public SudokuGame() {
        setTitle("Sudoku Solver");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(500, 500);
        setLocationRelativeTo(null);
        setLayout(new BorderLayout());

        // Create the grid for Sudoku
        JPanel gridPanel = new JPanel();
        gridPanel.setLayout(new GridLayout(9, 9));

        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                sudokuGrid[i][j] = new JTextField();
                sudokuGrid[i][j].setHorizontalAlignment(JTextField.CENTER);
                sudokuGrid[i][j].setFont(new Font("Arial", Font.BOLD, 20));
                sudokuGrid[i][j].setBackground(Color.WHITE);
                sudokuGrid[i][j].setBorder(BorderFactory.createLineBorder(Color.BLACK));

                // Restrict input to numbers only
                sudokuGrid[i][j].setDocument(new NumberLimitDocument(1));

                gridPanel.add(sudokuGrid[i][j]);
            }
        }

        add(gridPanel, BorderLayout.CENTER);

        // Button to solve the Sudoku puzzle
        JButton solveButton = new JButton("Solve Sudoku");
        solveButton.setFont(new Font("Arial", Font.BOLD, 18));
        solveButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                int[][] board = getBoard();
                if (board == null) {
                    JOptionPane.showMessageDialog(null, "Invalid input! Please enter valid Sudoku numbers.");
                    return;
                }

                if (solveSudoku(board)) {
                    setBoard(board);
                    JOptionPane.showMessageDialog(null, "Solved!");
                } else {
                    JOptionPane.showMessageDialog(null, "No solution exists for the given puzzle.");
                }
            }
        });

        add(solveButton, BorderLayout.SOUTH);

        setVisible(true);
    }

    // Method to retrieve the current board from the JTextFields
    private int[][] getBoard() {
        int[][] board = new int[9][9];

        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                String text = sudokuGrid[i][j].getText();
                if (text.equals("")) {
                    board[i][j] = 0; // Empty cells are represented by 0
                } else {
                    try {
                        int num = Integer.parseInt(text);
                        if (num >= 1 && num <= 9) {
                            board[i][j] = num;
                        } else {
                            return null; // Invalid number detected
                        }
                    } catch (NumberFormatException e) {
                        return null; // Invalid input detected
                    }
                }
            }
        }
        return board;
    }

    // Method to set the solution board back into the JTextFields
    private void setBoard(int[][] board) {
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                sudokuGrid[i][j].setText(board[i][j] == 0 ? "" : String.valueOf(board[i][j]));
            }
        }
    }

    // Backtracking algorithm to solve the Sudoku puzzle
    private boolean solveSudoku(int[][] board) {
        for (int row = 0; row < 9; row++) {
            for (int col = 0; col < 9; col++) {
                if (board[row][col] == 0) { // Find an empty cell
                    for (int num = 1; num <= 9; num++) {
                        if (isValid(board, row, col, num)) {
                            board[row][col] = num; // Try the number

                            if (solveSudoku(board)) {
                                return true; // Recursively solve the rest of the board
                            }

                            board[row][col] = 0; // Undo the move (backtrack)
                        }
                    }
                    return false; // No valid number found, trigger backtracking
                }
            }
        }
        return true; // Puzzle solved
    }

    // Check if placing num in board[row][col] is valid
    private boolean isValid(int[][] board, int row, int col, int num) {
        // Check the row
        for (int i = 0; i < 9; i++) {
            if (board[row][i] == num) return false;
        }

        // Check the column
        for (int i = 0; i < 9; i++) {
            if (board[i][col] == num) return false;
        }

        // Check the 3x3 subgrid
        int startRow = (row / 3) * 3;
        int startCol = (col / 3) * 3;
        for (int i = startRow; i < startRow + 3; i++) {
            for (int j = startCol; j < startCol + 3; j++) {
                if (board[i][j] == num) return false;
            }
        }

        return true;
    }

    // Restrict input to a specific number of characters
    class NumberLimitDocument extends PlainDocument {
        private int limit;

        public NumberLimitDocument(int limit) {
            this.limit = limit;
        }

        public void insertString(int offset, String str, AttributeSet attr) throws BadLocationException {
            if (str == null) return;

            if ((getLength() + str.length()) <= limit && str.matches("[1-9]")) {
                super.insertString(offset, str, attr);
            }
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> new SudokuGame());
    }
}
