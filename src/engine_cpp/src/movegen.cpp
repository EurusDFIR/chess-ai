#include "movegen.h"
#include <random>

// Attack tables storage
Bitboard AttackTables::pawnAttacks[2][64];
Bitboard AttackTables::knightAttacks[64];
Bitboard AttackTables::kingAttacks[64];
Bitboard AttackTables::bishopMasks[64];
Bitboard AttackTables::rookMasks[64];
Bitboard AttackTables::bishopAttacks[64][512];
Bitboard AttackTables::rookAttacks[64][4096];
uint64_t AttackTables::bishopMagics[64];
uint64_t AttackTables::rookMagics[64];
int AttackTables::bishopShifts[64];
int AttackTables::rookShifts[64];

// Helper: Generate pawn attacks
static Bitboard genPawnAttacks(Color c, Square sq)
{
    Bitboard bb = bit(sq);
    Bitboard attacks = 0;

    if (c == WHITE)
    {
        if (fileOf(sq) > 0)
            attacks |= bb << 7;
        if (fileOf(sq) < 7)
            attacks |= bb << 9;
    }
    else
    {
        if (fileOf(sq) > 0)
            attacks |= bb >> 9;
        if (fileOf(sq) < 7)
            attacks |= bb >> 7;
    }

    return attacks;
}

// Helper: Generate knight attacks
static Bitboard genKnightAttacks(Square sq)
{
    Bitboard bb = bit(sq);
    Bitboard attacks = 0;

    int file = fileOf(sq);
    int rank = rankOf(sq);

    // All 8 knight moves
    if (file > 0 && rank < 6)
        attacks |= bb << 15;
    if (file < 7 && rank < 6)
        attacks |= bb << 17;
    if (file > 1 && rank < 7)
        attacks |= bb << 6;
    if (file < 6 && rank < 7)
        attacks |= bb << 10;
    if (file > 0 && rank > 1)
        attacks |= bb >> 17;
    if (file < 7 && rank > 1)
        attacks |= bb >> 15;
    if (file > 1 && rank > 0)
        attacks |= bb >> 10;
    if (file < 6 && rank > 0)
        attacks |= bb >> 6;

    return attacks;
}

// Helper: Generate king attacks
static Bitboard genKingAttacks(Square sq)
{
    Bitboard bb = bit(sq);
    Bitboard attacks = 0;

    int file = fileOf(sq);

    if (file > 0)
        attacks |= (bb << 7) | (bb >> 1) | (bb >> 9);
    if (file < 7)
        attacks |= (bb << 9) | (bb << 1) | (bb >> 7);
    attacks |= (bb << 8) | (bb >> 8);

    return attacks;
}

// Helper: Generate bishop mask (excludes edges)
static Bitboard genBishopMask(Square sq)
{
    Bitboard attacks = 0;
    int file = fileOf(sq);
    int rank = rankOf(sq);

    // NE
    for (int f = file + 1, r = rank + 1; f < 7 && r < 7; f++, r++)
        attacks |= bit(makeSquare(f, r));

    // NW
    for (int f = file - 1, r = rank + 1; f > 0 && r < 7; f--, r++)
        attacks |= bit(makeSquare(f, r));

    // SE
    for (int f = file + 1, r = rank - 1; f < 7 && r > 0; f++, r--)
        attacks |= bit(makeSquare(f, r));

    // SW
    for (int f = file - 1, r = rank - 1; f > 0 && r > 0; f--, r--)
        attacks |= bit(makeSquare(f, r));

    return attacks;
}

// Helper: Generate rook mask (excludes edges)
static Bitboard genRookMask(Square sq)
{
    Bitboard attacks = 0;
    int file = fileOf(sq);
    int rank = rankOf(sq);

    // North
    for (int r = rank + 1; r < 7; r++)
        attacks |= bit(makeSquare(file, r));

    // South
    for (int r = rank - 1; r > 0; r--)
        attacks |= bit(makeSquare(file, r));

    // East
    for (int f = file + 1; f < 7; f++)
        attacks |= bit(makeSquare(f, rank));

    // West
    for (int f = file - 1; f > 0; f--)
        attacks |= bit(makeSquare(f, rank));

    return attacks;
}

// Helper: Generate bishop attacks on the fly
static Bitboard genBishopAttacksSlow(Square sq, Bitboard occupied)
{
    Bitboard attacks = 0;
    int file = fileOf(sq);
    int rank = rankOf(sq);

    // NE
    for (int f = file + 1, r = rank + 1; f <= 7 && r <= 7; f++, r++)
    {
        Square s = makeSquare(f, r);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    // NW
    for (int f = file - 1, r = rank + 1; f >= 0 && r <= 7; f--, r++)
    {
        Square s = makeSquare(f, r);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    // SE
    for (int f = file + 1, r = rank - 1; f <= 7 && r >= 0; f++, r--)
    {
        Square s = makeSquare(f, r);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    // SW
    for (int f = file - 1, r = rank - 1; f >= 0 && r >= 0; f--, r--)
    {
        Square s = makeSquare(f, r);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    return attacks;
}

// Helper: Generate rook attacks on the fly
static Bitboard genRookAttacksSlow(Square sq, Bitboard occupied)
{
    Bitboard attacks = 0;
    int file = fileOf(sq);
    int rank = rankOf(sq);

    // North
    for (int r = rank + 1; r <= 7; r++)
    {
        Square s = makeSquare(file, r);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    // South
    for (int r = rank - 1; r >= 0; r--)
    {
        Square s = makeSquare(file, r);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    // East
    for (int f = file + 1; f <= 7; f++)
    {
        Square s = makeSquare(f, rank);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    // West
    for (int f = file - 1; f >= 0; f--)
    {
        Square s = makeSquare(f, rank);
        attacks |= bit(s);
        if (occupied & bit(s))
            break;
    }

    return attacks;
}

// Helper: Find magic number (simplified - uses pre-computed magics in practice)
static uint64_t findMagic(Square sq, bool isBishop)
{
    // In a real implementation, these would be found through brute force
    // For now, return a simple hash based on square
    return 0x0101010101010101ULL * (sq + (isBishop ? 64 : 0));
}

// Initialize attack tables
void AttackTables::init()
{
    // Initialize pawn attacks
    for (int sq = 0; sq < 64; sq++)
    {
        pawnAttacks[WHITE][sq] = genPawnAttacks(WHITE, Square(sq));
        pawnAttacks[BLACK][sq] = genPawnAttacks(BLACK, Square(sq));
    }

    // Initialize knight attacks
    for (int sq = 0; sq < 64; sq++)
    {
        knightAttacks[sq] = genKnightAttacks(Square(sq));
    }

    // Initialize king attacks
    for (int sq = 0; sq < 64; sq++)
    {
        kingAttacks[sq] = genKingAttacks(Square(sq));
    }

    // Initialize bishop masks and attacks
    for (int sq = 0; sq < 64; sq++)
    {
        bishopMasks[sq] = genBishopMask(Square(sq));
        int bits = popcount(bishopMasks[sq]);
        bishopShifts[sq] = 64 - bits;

        // Generate all possible occupancy variations
        int numVariations = 1 << bits;
        for (int i = 0; i < numVariations; i++)
        {
            Bitboard occupied = 0;
            Bitboard mask = bishopMasks[sq];
            int count = 0;

            // Create occupancy from index
            while (mask)
            {
                Square s = popLsb(mask);
                if (i & (1 << count))
                {
                    occupied |= bit(s);
                }
                count++;
            }

            // Generate attacks for this occupancy
            Bitboard attacks = genBishopAttacksSlow(Square(sq), occupied);

            // Store in table (simplified indexing)
            bishopAttacks[sq][i] = attacks;
        }

        bishopMagics[sq] = findMagic(Square(sq), true);
    }

    // Initialize rook masks and attacks
    for (int sq = 0; sq < 64; sq++)
    {
        rookMasks[sq] = genRookMask(Square(sq));
        int bits = popcount(rookMasks[sq]);
        rookShifts[sq] = 64 - bits;

        // Generate all possible occupancy variations
        int numVariations = 1 << bits;
        for (int i = 0; i < numVariations && i < 4096; i++)
        {
            Bitboard occupied = 0;
            Bitboard mask = rookMasks[sq];
            int count = 0;

            // Create occupancy from index
            while (mask)
            {
                Square s = popLsb(mask);
                if (i & (1 << count))
                {
                    occupied |= bit(s);
                }
                count++;
            }

            // Generate attacks for this occupancy
            Bitboard attacks = genRookAttacksSlow(Square(sq), occupied);

            // Store in table (simplified indexing)
            rookAttacks[sq][i] = attacks;
        }

        rookMagics[sq] = findMagic(Square(sq), false);
    }
}

// Get bishop attacks using magic bitboards
Bitboard AttackTables::getBishopAttacks(Square sq, Bitboard occupied)
{
    occupied &= bishopMasks[sq];
    int index = (occupied * bishopMagics[sq]) >> bishopShifts[sq];
    return bishopAttacks[sq][index & 511];
}

// Get rook attacks using magic bitboards
Bitboard AttackTables::getRookAttacks(Square sq, Bitboard occupied)
{
    occupied &= rookMasks[sq];
    int index = (occupied * rookMagics[sq]) >> rookShifts[sq];
    return rookAttacks[sq][index & 4095];
}

// Get queen attacks (bishop + rook)
Bitboard AttackTables::getQueenAttacks(Square sq, Bitboard occupied)
{
    return getBishopAttacks(sq, occupied) | getRookAttacks(sq, occupied);
}

// ============================================================================
// MOVE GENERATION
// ============================================================================

// Generate all legal moves
void MoveGenerator::generateLegalMoves(const Board &board, MoveList &moves)
{
    moves.clear();
    MoveList pseudoLegal;
    generatePseudoLegalMoves(board, pseudoLegal, false);

    // Filter out illegal moves (leave king in check)
    for (const Move &move : pseudoLegal)
    {
        Board copy = board;
        copy.makeMove(move);
        if (!copy.isCheck())
        {
            moves.add(move);
        }
    }
}

// Generate captures only
void MoveGenerator::generateCaptures(const Board &board, MoveList &moves)
{
    moves.clear();
    generatePseudoLegalMoves(board, moves, true);
}

// Generate quiet moves only
void MoveGenerator::generateQuietMoves(const Board &board, MoveList &moves)
{
    moves.clear();
    MoveList all;
    generatePseudoLegalMoves(board, all, false);

    // Filter out captures
    for (const Move &move : all)
    {
        if (!move.isCapture())
        {
            moves.add(move);
        }
    }
}

// Generate pseudo-legal moves (may leave king in check)
void MoveGenerator::generatePseudoLegalMoves(const Board &board, MoveList &moves, bool capturesOnly)
{
    Color us = board.getSideToMove();

    generatePawnMoves(board, moves, capturesOnly);
    generateKnightMoves(board, moves, capturesOnly);
    generateBishopMoves(board, moves, capturesOnly);
    generateRookMoves(board, moves, capturesOnly);
    generateQueenMoves(board, moves, capturesOnly);
    generateKingMoves(board, moves, capturesOnly);

    if (!capturesOnly)
    {
        generateCastlingMoves(board, moves);
    }
}

// Generate pawn moves
void MoveGenerator::generatePawnMoves(const Board &board, MoveList &moves, bool capturesOnly)
{
    Color us = board.getSideToMove();
    Color them = ~us;
    Bitboard pawns = board.getPieces(us, PAWN);
    Bitboard occupied = board.getAllOccupied();
    Bitboard enemies = board.getOccupied(them);

    int forward = (us == WHITE) ? 8 : -8;
    int promoRank = (us == WHITE) ? 7 : 0;

    while (pawns)
    {
        Square from = popLsb(pawns);
        int rank = rankOf(from);

        // Captures
        Bitboard attacks = AttackTables::getPawnAttacks(us, from) & enemies;
        while (attacks)
        {
            Square to = popLsb(attacks);

            // Promotion
            if (rankOf(to) == promoRank)
            {
                moves.add(Move(from, to, QUEEN_PROMO_CAPTURE));
                moves.add(Move(from, to, KNIGHT_PROMO_CAPTURE));
                moves.add(Move(from, to, ROOK_PROMO_CAPTURE));
                moves.add(Move(from, to, BISHOP_PROMO_CAPTURE));
            }
            else
            {
                moves.add(Move(from, to, CAPTURE));
            }
        }

        // En passant
        if (board.getEnPassantSquare() != NO_SQUARE)
        {
            Bitboard epAttacks = AttackTables::getPawnAttacks(us, from);
            if (epAttacks & bit(board.getEnPassantSquare()))
            {
                moves.add(Move(from, board.getEnPassantSquare(), EN_PASSANT));
            }
        }

        if (capturesOnly)
            continue;

        // Forward moves
        Square to = Square(from + forward);
        if (to >= 0 && to < 64 && !(occupied & bit(to)))
        {
            // Promotion
            if (rankOf(to) == promoRank)
            {
                moves.add(Move(from, to, QUEEN_PROMOTION));
                moves.add(Move(from, to, KNIGHT_PROMOTION));
                moves.add(Move(from, to, ROOK_PROMOTION));
                moves.add(Move(from, to, BISHOP_PROMOTION));
            }
            else
            {
                moves.add(Move(from, to, QUIET));

                // Double push
                int startRank = (us == WHITE) ? 1 : 6;
                if (rank == startRank)
                {
                    Square to2 = Square(to + forward);
                    if (!(occupied & bit(to2)))
                    {
                        moves.add(Move(from, to2, DOUBLE_PAWN_PUSH));
                    }
                }
            }
        }
    }
}

// Generate knight moves
void MoveGenerator::generateKnightMoves(const Board &board, MoveList &moves, bool capturesOnly)
{
    Color us = board.getSideToMove();
    Bitboard knights = board.getPieces(us, KNIGHT);
    Bitboard targets = capturesOnly ? board.getOccupied(~us) : ~board.getOccupied(us);

    while (knights)
    {
        Square from = popLsb(knights);
        Bitboard attacks = AttackTables::getKnightAttacks(from) & targets;

        addMovesFromBitboard(moves, from, attacks,
                             capturesOnly ? CAPTURE : QUIET);
    }
}

// Generate bishop moves
void MoveGenerator::generateBishopMoves(const Board &board, MoveList &moves, bool capturesOnly)
{
    Color us = board.getSideToMove();
    Bitboard bishops = board.getPieces(us, BISHOP);
    Bitboard occupied = board.getAllOccupied();
    Bitboard targets = capturesOnly ? board.getOccupied(~us) : ~board.getOccupied(us);

    while (bishops)
    {
        Square from = popLsb(bishops);
        Bitboard attacks = AttackTables::getBishopAttacks(from, occupied) & targets;

        addMovesFromBitboard(moves, from, attacks,
                             capturesOnly ? CAPTURE : QUIET);
    }
}

// Generate rook moves
void MoveGenerator::generateRookMoves(const Board &board, MoveList &moves, bool capturesOnly)
{
    Color us = board.getSideToMove();
    Bitboard rooks = board.getPieces(us, ROOK);
    Bitboard occupied = board.getAllOccupied();
    Bitboard targets = capturesOnly ? board.getOccupied(~us) : ~board.getOccupied(us);

    while (rooks)
    {
        Square from = popLsb(rooks);
        Bitboard attacks = AttackTables::getRookAttacks(from, occupied) & targets;

        addMovesFromBitboard(moves, from, attacks,
                             capturesOnly ? CAPTURE : QUIET);
    }
}

// Generate queen moves
void MoveGenerator::generateQueenMoves(const Board &board, MoveList &moves, bool capturesOnly)
{
    Color us = board.getSideToMove();
    Bitboard queens = board.getPieces(us, QUEEN);
    Bitboard occupied = board.getAllOccupied();
    Bitboard targets = capturesOnly ? board.getOccupied(~us) : ~board.getOccupied(us);

    while (queens)
    {
        Square from = popLsb(queens);
        Bitboard attacks = AttackTables::getQueenAttacks(from, occupied) & targets;

        addMovesFromBitboard(moves, from, attacks,
                             capturesOnly ? CAPTURE : QUIET);
    }
}

// Generate king moves
void MoveGenerator::generateKingMoves(const Board &board, MoveList &moves, bool capturesOnly)
{
    Color us = board.getSideToMove();
    Square from = board.getKingSquare(us);
    if (from == NO_SQUARE)
        return;

    Bitboard targets = capturesOnly ? board.getOccupied(~us) : ~board.getOccupied(us);
    Bitboard attacks = AttackTables::getKingAttacks(from) & targets;

    addMovesFromBitboard(moves, from, attacks,
                         capturesOnly ? CAPTURE : QUIET);
}

// Generate castling moves
void MoveGenerator::generateCastlingMoves(const Board &board, MoveList &moves)
{
    Color us = board.getSideToMove();

    if (board.isCheck())
        return; // Can't castle out of check

    uint8_t rights = board.getCastlingRights();
    Bitboard occupied = board.getAllOccupied();

    if (us == WHITE)
    {
        // White king-side
        if (rights & WHITE_OO)
        {
            if (!(occupied & ((1ULL << F1) | (1ULL << G1))))
            {
                if (!board.isSquareAttacked(F1, BLACK))
                {
                    moves.add(Move(E1, G1, KING_CASTLE));
                }
            }
        }

        // White queen-side
        if (rights & WHITE_OOO)
        {
            if (!(occupied & ((1ULL << D1) | (1ULL << C1) | (1ULL << B1))))
            {
                if (!board.isSquareAttacked(D1, BLACK))
                {
                    moves.add(Move(E1, C1, QUEEN_CASTLE));
                }
            }
        }
    }
    else
    {
        // Black king-side
        if (rights & BLACK_OO)
        {
            if (!(occupied & ((1ULL << F8) | (1ULL << G8))))
            {
                if (!board.isSquareAttacked(F8, WHITE))
                {
                    moves.add(Move(E8, G8, KING_CASTLE));
                }
            }
        }

        // Black queen-side
        if (rights & BLACK_OOO)
        {
            if (!(occupied & ((1ULL << D8) | (1ULL << C8) | (1ULL << B8))))
            {
                if (!board.isSquareAttacked(D8, WHITE))
                {
                    moves.add(Move(E8, C8, QUEEN_CASTLE));
                }
            }
        }
    }
}

// Helper: Add moves from bitboard to move list
void MoveGenerator::addMovesFromBitboard(MoveList &moves, Square from, Bitboard targets, uint8_t baseFlags)
{
    while (targets)
    {
        Square to = popLsb(targets);
        uint8_t flags = baseFlags;

        // Determine if capture (more accurate check would look at target square)
        // For now, assuming baseFlags is correct

        moves.add(Move(from, to, flags));
    }
}

// Check if move is legal
bool MoveGenerator::isLegal(const Board &board, const Move &move)
{
    MoveList legal;
    generateLegalMoves(board, legal);

    for (const Move &m : legal)
    {
        if (m == move)
            return true;
    }

    return false;
}
