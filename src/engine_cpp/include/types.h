#ifndef TYPES_H
#define TYPES_H

#include <cstdint>
#include <string>
#include <vector>

// Basic types
typedef uint64_t Bitboard;
typedef int8_t Square;
typedef int16_t Score;

// Constants
constexpr int MAX_MOVES = 256;
constexpr int MAX_PLY = 128;
constexpr Score SCORE_INFINITE = 32000;
constexpr Score SCORE_MATE = 31000;
constexpr Score SCORE_DRAW = 0;

// Piece types
enum PieceType : uint8_t
{
    PAWN = 0,
    KNIGHT,
    BISHOP,
    ROOK,
    QUEEN,
    KING,
    NO_PIECE_TYPE = 7
};

// Colors
enum Color : uint8_t
{
    WHITE = 0,
    BLACK = 1,
    NO_COLOR = 2
};

// Squares (0-63, A1=0, H8=63)
enum Squares : Square
{
    A1,
    B1,
    C1,
    D1,
    E1,
    F1,
    G1,
    H1,
    A2,
    B2,
    C2,
    D2,
    E2,
    F2,
    G2,
    H2,
    A3,
    B3,
    C3,
    D3,
    E3,
    F3,
    G3,
    H3,
    A4,
    B4,
    C4,
    D4,
    E4,
    F4,
    G4,
    H4,
    A5,
    B5,
    C5,
    D5,
    E5,
    F5,
    G5,
    H5,
    A6,
    B6,
    C6,
    D6,
    E6,
    F6,
    G6,
    H6,
    A7,
    B7,
    C7,
    D7,
    E7,
    F7,
    G7,
    H7,
    A8,
    B8,
    C8,
    D8,
    E8,
    F8,
    G8,
    H8,
    NO_SQUARE = 64
};

// Castling rights
enum CastlingRights : uint8_t
{
    WHITE_OO = 1,  // White king-side
    WHITE_OOO = 2, // White queen-side
    BLACK_OO = 4,  // Black king-side
    BLACK_OOO = 8, // Black queen-side
    NO_CASTLING = 0,
    ANY_CASTLING = 15
};

// Move flags
enum MoveFlags : uint8_t
{
    QUIET = 0,
    DOUBLE_PAWN_PUSH = 1,
    KING_CASTLE = 2,
    QUEEN_CASTLE = 3,
    CAPTURE = 4,
    EN_PASSANT = 5,
    KNIGHT_PROMOTION = 8,
    BISHOP_PROMOTION = 9,
    ROOK_PROMOTION = 10,
    QUEEN_PROMOTION = 11,
    KNIGHT_PROMO_CAPTURE = 12,
    BISHOP_PROMO_CAPTURE = 13,
    ROOK_PROMO_CAPTURE = 14,
    QUEEN_PROMO_CAPTURE = 15
};

// TT entry types
enum TTFlag : uint8_t
{
    TT_EXACT = 0,
    TT_ALPHA = 1,
    TT_BETA = 2
};

// Utility functions
inline Color operator~(Color c) { return Color(c ^ BLACK); }
inline Square makeSquare(int file, int rank) { return Square(rank * 8 + file); }
inline int fileOf(Square s) { return s & 7; }
inline int rankOf(Square s) { return s >> 3; }

// Bitboard operations
inline Bitboard bit(Square s) { return 1ULL << s; }
inline bool moreThanOne(Bitboard b) { return b & (b - 1); }

// Platform-specific popcount and ctz
#ifdef _MSC_VER
#include <intrin.h>
inline int popcount(Bitboard b) { return (int)__popcnt64(b); }
inline Square lsb(Bitboard b)
{
    unsigned long idx;
    _BitScanForward64(&idx, b);
    return Square(idx);
}
#else
inline int popcount(Bitboard b) { return __builtin_popcountll(b); }
inline Square lsb(Bitboard b) { return Square(__builtin_ctzll(b)); }
#endif

inline Square popLsb(Bitboard &b)
{
    Square s = lsb(b);
    b &= b - 1;
    return s;
}

// Move encoding (16 bits)
// bits 0-5: from square
// bits 6-11: to square
// bits 12-15: flags
class Move
{
private:
    uint16_t data;

public:
    Move() : data(0) {}
    Move(Square from, Square to, uint8_t flags = QUIET)
        : data(from | (to << 6) | (flags << 12)) {}

    Square from() const { return Square(data & 0x3F); }
    Square to() const { return Square((data >> 6) & 0x3F); }
    uint8_t flags() const { return data >> 12; }

    bool isCapture() const { return flags() & CAPTURE; }
    bool isPromotion() const { return flags() & 0x8; }
    bool isCastling() const
    {
        uint8_t f = flags();
        return f == KING_CASTLE || f == QUEEN_CASTLE;
    }
    bool isEnPassant() const { return flags() == EN_PASSANT; }

    bool isNull() const { return data == 0; }

    std::string toUCI() const;
    static Move fromUCI(const std::string &uci);

    bool operator==(const Move &m) const { return data == m.data; }
    bool operator!=(const Move &m) const { return data != m.data; }
};

// Move list
class MoveList
{
private:
    Move moves[MAX_MOVES];
    int count;

public:
    MoveList() : count(0) {}

    void add(const Move &move) { moves[count++] = move; }
    void clear() { count = 0; }

    int size() const { return count; }
    Move &operator[](int i) { return moves[i]; }
    const Move &operator[](int i) const { return moves[i]; }

    Move *begin() { return moves; }
    Move *end() { return moves + count; }
    const Move *begin() const { return moves; }
    const Move *end() const { return moves + count; }
};

// Piece values
constexpr Score PIECE_VALUES[7] = {
    100,   // PAWN
    320,   // KNIGHT
    330,   // BISHOP
    500,   // ROOK
    900,   // QUEEN
    20000, // KING
    0      // NO_PIECE
};

#endif // TYPES_H
