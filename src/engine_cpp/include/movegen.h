#ifndef MOVEGEN_H
#define MOVEGEN_H

#include "types.h"
#include "board.h"

// Pre-computed attack tables
class AttackTables
{
public:
    static void init();

    // Non-sliding pieces
    static Bitboard pawnAttacks[2][64]; // [color][square]
    static Bitboard knightAttacks[64];
    static Bitboard kingAttacks[64];

    // Sliding pieces (magic bitboards)
    static Bitboard bishopMasks[64];
    static Bitboard rookMasks[64];
    static Bitboard bishopAttacks[64][512];
    static Bitboard rookAttacks[64][4096];

    // Magic numbers (pre-computed)
    static uint64_t bishopMagics[64];
    static uint64_t rookMagics[64];
    static int bishopShifts[64];
    static int rookShifts[64];

    // Attack getters
    static Bitboard getPawnAttacks(Color c, Square sq) { return pawnAttacks[c][sq]; }
    static Bitboard getKnightAttacks(Square sq) { return knightAttacks[sq]; }
    static Bitboard getKingAttacks(Square sq) { return kingAttacks[sq]; }
    static Bitboard getBishopAttacks(Square sq, Bitboard occupied);
    static Bitboard getRookAttacks(Square sq, Bitboard occupied);
    static Bitboard getQueenAttacks(Square sq, Bitboard occupied);
};

class MoveGenerator
{
public:
    // Generate all legal moves
    static void generateLegalMoves(const Board &board, MoveList &moves);

    // Generate only captures (for quiescence search)
    static void generateCaptures(const Board &board, MoveList &moves);

    // Generate only quiet moves (non-captures)
    static void generateQuietMoves(const Board &board, MoveList &moves);

    // Check if a move is legal
    static bool isLegal(const Board &board, const Move &move);

private:
    // Generate pseudo-legal moves (may leave king in check)
    static void generatePseudoLegalMoves(const Board &board, MoveList &moves, bool capturesOnly = false);

    // Per-piece move generation
    static void generatePawnMoves(const Board &board, MoveList &moves, bool capturesOnly);
    static void generateKnightMoves(const Board &board, MoveList &moves, bool capturesOnly);
    static void generateBishopMoves(const Board &board, MoveList &moves, bool capturesOnly);
    static void generateRookMoves(const Board &board, MoveList &moves, bool capturesOnly);
    static void generateQueenMoves(const Board &board, MoveList &moves, bool capturesOnly);
    static void generateKingMoves(const Board &board, MoveList &moves, bool capturesOnly);
    static void generateCastlingMoves(const Board &board, MoveList &moves);

    // Helper: add moves from bitboard
    static void addMovesFromBitboard(MoveList &moves, Square from, Bitboard targets, uint8_t flags);
};

#endif // MOVEGEN_H
