#ifndef BOARD_H
#define BOARD_H

#include "types.h"
#include <array>
#include <string>

// Zobrist keys for hashing
class Zobrist
{
public:
    static void init();
    static uint64_t psq[2][7][64]; // [color][piece][square]
    static uint64_t enpassant[8];  // [file]
    static uint64_t castling[16];  // [castling rights]
    static uint64_t sideToMove;
};

// Board state (for unmake)
struct BoardState
{
    uint8_t castlingRights;
    Square enPassantSquare;
    uint16_t halfMoveClock;
    uint64_t hash;
    PieceType capturedPiece;
};

class Board
{
private:
    // Bitboards for each piece type and color
    Bitboard pieces[2][7]; // [color][piece type]
    Bitboard occupied[3];  // [WHITE, BLACK, BOTH]

    // Piece on each square
    PieceType pieceTypes[64];
    Color pieceColors[64];

    // Game state
    Color sideToMove;
    uint8_t castlingRights;
    Square enPassantSquare;
    uint16_t halfMoveClock;
    uint32_t fullMoveNumber;
    uint64_t hash;

    // History for unmake
    std::vector<BoardState> history;

    // Helper functions
    void clearSquare(Square sq);
    void putPiece(Color c, PieceType pt, Square sq);
    void movePiece(Color c, PieceType pt, Square from, Square to);
    void updateHash(Square sq, Color c, PieceType pt);

public:
    Board();

    // Initialization
    void initStartPosition();
    bool fromFEN(const std::string &fen);
    std::string toFEN() const;

    // Move operations
    void makeMove(const Move &move);
    void unmakeMove(const Move &move);
    void makeNullMove();
    void unmakeNullMove();

    // Board queries
    Bitboard getPieces(Color c, PieceType pt) const { return pieces[c][pt]; }
    Bitboard getOccupied(Color c) const { return occupied[c]; }
    Bitboard getAllOccupied() const { return occupied[WHITE] | occupied[BLACK]; }

    PieceType pieceTypeAt(Square sq) const { return pieceTypes[sq]; }
    Color pieceColorAt(Square sq) const { return pieceColors[sq]; }
    bool isEmpty(Square sq) const { return pieceTypes[sq] == NO_PIECE_TYPE; }

    Color getSideToMove() const { return sideToMove; }
    uint8_t getCastlingRights() const { return castlingRights; }
    Square getEnPassantSquare() const { return enPassantSquare; }
    uint16_t getHalfMoveClock() const { return halfMoveClock; }
    uint32_t getFullMoveNumber() const { return fullMoveNumber; }
    uint64_t getHash() const { return hash; }

    // Game state checks
    bool isCheck() const;
    bool isCheckmate() const;
    bool isStalemate() const;
    bool isDraw() const;
    bool isRepetition() const;
    bool isInsufficientMaterial() const;

    // Attack queries
    Bitboard getAttackers(Square sq, Color attackerColor) const;
    bool isSquareAttacked(Square sq, Color attackerColor) const;

    // Utility
    void print() const;
    int getMaterial(Color c) const;

    // King positions
    Square getKingSquare(Color c) const;
};

#endif // BOARD_H
