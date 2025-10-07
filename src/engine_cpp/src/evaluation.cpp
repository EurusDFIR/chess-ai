#include "evaluation.h"
#include "movegen.h"

// Game phase constants
constexpr int PHASE_PAWN = 0;
constexpr int PHASE_KNIGHT = 1;
constexpr int PHASE_BISHOP = 1;
constexpr int PHASE_ROOK = 2;
constexpr int PHASE_QUEEN = 4;
constexpr int PHASE_MAX = 16 * PHASE_PAWN + 4 * PHASE_KNIGHT + 4 * PHASE_BISHOP + 4 * PHASE_ROOK + 2 * PHASE_QUEEN;

// Main evaluation function
Score Evaluator::evaluate(const Board &board)
{
    Score score = 0;

    // Material + position
    score += evaluateMaterial(board);
    score += evaluatePosition(board);

    // Positional factors
    score += evaluatePawnStructure(board);
    score += evaluateKingSafety(board);
    score += evaluateMobility(board);
    score += evaluateThreats(board);

    // Return score from white's perspective
    Color side = board.getSideToMove();
    return side == WHITE ? score : -score;
}

// Evaluate material
Score Evaluator::evaluateMaterial(const Board &board)
{
    Score score = 0;

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;

        // Count pieces
        int pawns = popcount(board.getPieces(c, PAWN));
        int knights = popcount(board.getPieces(c, KNIGHT));
        int bishops = popcount(board.getPieces(c, BISHOP));
        int rooks = popcount(board.getPieces(c, ROOK));
        int queens = popcount(board.getPieces(c, QUEEN));

        // Add material value
        score += sign * (pawns * PIECE_VALUES[PAWN] +
                         knights * PIECE_VALUES[KNIGHT] +
                         bishops * PIECE_VALUES[BISHOP] +
                         rooks * PIECE_VALUES[ROOK] +
                         queens * PIECE_VALUES[QUEEN]);

        // Bishop pair bonus
        if (bishops >= 2)
        {
            score += sign * 50;
        }
    }

    return score;
}

// Evaluate position using PST
Score Evaluator::evaluatePosition(const Board &board)
{
    Score score = 0;
    int phase = getGamePhase(board);

    for (Color c : {WHITE, BLACK})
    {
        for (PieceType pt : {PAWN, KNIGHT, BISHOP, ROOK, QUEEN, KING})
        {
            Bitboard pieces = board.getPieces(c, pt);

            while (pieces)
            {
                Square sq = popLsb(pieces);
                score += getPSTValue(pt, sq, c, phase);
            }
        }
    }

    return score;
}

// Evaluate pawn structure
Score Evaluator::evaluatePawnStructure(const Board &board)
{
    Score score = 0;

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        Bitboard pawns = board.getPieces(c, PAWN);
        Bitboard enemyPawns = board.getPieces(~c, PAWN);

        while (pawns)
        {
            Square sq = popLsb(pawns);
            int file = fileOf(sq);
            int rank = rankOf(sq);

            // Isolated pawn penalty
            Bitboard adjacentFiles = 0;
            if (file > 0)
                adjacentFiles |= 0x0101010101010101ULL << (file - 1);
            if (file < 7)
                adjacentFiles |= 0x0101010101010101ULL << (file + 1);

            if (!(board.getPieces(c, PAWN) & adjacentFiles))
            {
                score -= sign * 20; // Isolated pawn
            }

            // Doubled pawn penalty
            Bitboard fileBoard = 0x0101010101010101ULL << file;
            if (popcount(board.getPieces(c, PAWN) & fileBoard) > 1)
            {
                score -= sign * 10; // Doubled pawn
            }

            // Passed pawn bonus
            Bitboard passedMask = 0;
            if (c == WHITE)
            {
                for (int r = rank + 1; r < 8; r++)
                {
                    passedMask |= (0xFFULL << (r * 8));
                }
            }
            else
            {
                for (int r = 0; r < rank; r++)
                {
                    passedMask |= (0xFFULL << (r * 8));
                }
            }
            passedMask &= (adjacentFiles | fileBoard);

            if (!(enemyPawns & passedMask))
            {
                int passedRank = (c == WHITE) ? rank : (7 - rank);
                score += sign * (20 + passedRank * 10); // Passed pawn
            }
        }
    }

    return score;
}

// Evaluate king safety
Score Evaluator::evaluateKingSafety(const Board &board)
{
    Score score = 0;
    int phase = getGamePhase(board);

    // King safety matters more in middlegame
    if (phase < PHASE_MAX / 2)
        return 0;

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        Square kingSq = board.getKingSquare(c);

        // Pawn shield
        Bitboard shield = AttackTables::getKingAttacks(kingSq);
        shield &= board.getPieces(c, PAWN);
        int shieldPawns = popcount(shield);
        score += sign * shieldPawns * 10;

        // Attackers near king
        Bitboard kingZone = AttackTables::getKingAttacks(kingSq);
        Bitboard attackers = board.getAttackers(kingSq, ~c);
        int numAttackers = popcount(attackers);
        score -= sign * numAttackers * 15;
    }

    return score;
}

// Evaluate mobility
Score Evaluator::evaluateMobility(const Board &board)
{
    Score score = 0;
    Bitboard occupied = board.getAllOccupied();

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        int mobility = 0;

        // Knight mobility
        Bitboard knights = board.getPieces(c, KNIGHT);
        while (knights)
        {
            Square sq = popLsb(knights);
            Bitboard attacks = AttackTables::getKnightAttacks(sq);
            attacks &= ~board.getOccupied(c); // Exclude own pieces
            mobility += popcount(attacks);
        }

        // Bishop mobility
        Bitboard bishops = board.getPieces(c, BISHOP);
        while (bishops)
        {
            Square sq = popLsb(bishops);
            Bitboard attacks = AttackTables::getBishopAttacks(sq, occupied);
            attacks &= ~board.getOccupied(c);
            mobility += popcount(attacks);
        }

        // Rook mobility
        Bitboard rooks = board.getPieces(c, ROOK);
        while (rooks)
        {
            Square sq = popLsb(rooks);
            Bitboard attacks = AttackTables::getRookAttacks(sq, occupied);
            attacks &= ~board.getOccupied(c);
            mobility += popcount(attacks);
        }

        // Queen mobility
        Bitboard queens = board.getPieces(c, QUEEN);
        while (queens)
        {
            Square sq = popLsb(queens);
            Bitboard attacks = AttackTables::getQueenAttacks(sq, occupied);
            attacks &= ~board.getOccupied(c);
            mobility += popcount(attacks);
        }

        score += sign * mobility * 2; // 2 centipawns per legal move
    }

    return score;
}

// Evaluate threats
Score Evaluator::evaluateThreats(const Board &board)
{
    Score score = 0;

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        Bitboard enemyPieces = board.getOccupied(~c);

        // Pieces attacked by pawns
        Bitboard pawns = board.getPieces(c, PAWN);
        Bitboard pawnAttacks = 0;

        while (pawns)
        {
            Square sq = popLsb(pawns);
            pawnAttacks |= AttackTables::getPawnAttacks(c, sq);
        }

        // Bonus for attacking enemy pieces with pawns
        Bitboard threatenedPieces = pawnAttacks & enemyPieces;
        while (threatenedPieces)
        {
            Square sq = popLsb(threatenedPieces);
            PieceType pt = board.pieceTypeAt(sq);
            if (pt != PAWN && pt != NO_PIECE_TYPE)
            {
                score += sign * 25; // Pawn threatens piece
            }
        }
    }

    return score;
}

// Get game phase (0 = endgame, PHASE_MAX = opening)
int Evaluator::getGamePhase(const Board &board)
{
    int phase = 0;

    for (Color c : {WHITE, BLACK})
    {
        phase += popcount(board.getPieces(c, PAWN)) * PHASE_PAWN;
        phase += popcount(board.getPieces(c, KNIGHT)) * PHASE_KNIGHT;
        phase += popcount(board.getPieces(c, BISHOP)) * PHASE_BISHOP;
        phase += popcount(board.getPieces(c, ROOK)) * PHASE_ROOK;
        phase += popcount(board.getPieces(c, QUEEN)) * PHASE_QUEEN;
    }

    return std::min(phase, PHASE_MAX);
}

// Interpolate between middlegame and endgame scores
Score Evaluator::interpolateScore(Score mg, Score eg, int phase)
{
    return (mg * phase + eg * (PHASE_MAX - phase)) / PHASE_MAX;
}

// Get PST value for a piece
Score Evaluator::getPSTValue(PieceType pt, Square sq, Color c, int phase)
{
    // Flip square for black
    if (c == BLACK)
    {
        sq = flipSquare(sq);
    }

    int sign = (c == WHITE) ? 1 : -1;
    Score mg = 0, eg = 0;

    switch (pt)
    {
    case PAWN:
        mg = PAWN_PST_MG[sq];
        eg = PAWN_PST_EG[sq];
        break;
    case KNIGHT:
        mg = KNIGHT_PST_MG[sq];
        eg = KNIGHT_PST_EG[sq];
        break;
    case BISHOP:
        mg = BISHOP_PST_MG[sq];
        eg = BISHOP_PST_EG[sq];
        break;
    case ROOK:
        mg = ROOK_PST_MG[sq];
        eg = ROOK_PST_EG[sq];
        break;
    case QUEEN:
        mg = QUEEN_PST_MG[sq];
        eg = QUEEN_PST_EG[sq];
        break;
    case KING:
        mg = KING_PST_MG[sq];
        eg = KING_PST_EG[sq];
        break;
    default:
        return 0;
    }

    return sign * interpolateScore(mg, eg, phase);
}
