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

    // NEW: Opening principles (Python v2.3.0)
    score += evaluateOpeningPrinciples(board);

    // NEW: Endgame and special positions
    score += evaluateEndgame(board);
    score += evaluateRookOnOpenFile(board);

    // Return score from SIDE TO MOVE's perspective for negamax
    // Negamax expects each node to return score from current player's POV
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
    // DISABLED: Legal move counting breaks symmetry with null move approach
    // TODO: Implement proper caching or use different approach
    // For now, return 0 to maintain evaluation stability
    return 0;

    /* Attempted implementation - causes asymmetry
    Score score = 0;
    Color originalSide = board.getSideToMove();

    MoveList currentMoves;
    MoveGenerator::generateLegalMoves(board, currentMoves);
    int currentMobility = currentMoves.size();

    Board tempBoard = board;
    tempBoard.makeNullMove();

    MoveList opponentMoves;
    MoveGenerator::generateLegalMoves(tempBoard, opponentMoves);
    int opponentMobility = opponentMoves.size();

    tempBoard.unmakeNullMove();

    if (originalSide == WHITE) {
        score = (currentMobility - opponentMobility) * 1;
    } else {
        score = (opponentMobility - currentMobility) * 1;
    }

    return score;
    */
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

// ============================================================================
// NEW: Opening Principles Evaluation (Python v2.3.0)
// ============================================================================

Score Evaluator::evaluateOpeningPrinciples(const Board &board)
{
    // Only apply in opening (first 20 moves)
    if (board.getFullMoveNumber() > 20)
        return 0;

    Score score = 0;

    score += evaluateCenterControl(board);
    score += evaluateDevelopment(board);
    score += evaluateCastlingRights(board);
    score += evaluateEarlyQueen(board);

    return score;
}

Score Evaluator::evaluateCenterControl(const Board &board)
{
    Score score = 0;

    // Center squares: e4, d4, e5, d5
    const Square centerSquares[] = {E4, D4, E5, D5};

    for (Square sq : centerSquares)
    {
        PieceType pt = board.pieceTypeAt(sq);
        Color pc = board.pieceColorAt(sq);

        if (pt == PAWN)
        {
            // Pawn in center: +20 (Python value, will be multiplied by 2 later)
            score += (pc == WHITE) ? 20 : -20;
        }

        // Control of center squares (Python: +5 per attacker)
        // Count attackers for each side
        Bitboard white_attackers = board.getAttackers(sq, WHITE);
        Bitboard black_attackers = board.getAttackers(sq, BLACK);
        int white_control = popcount(white_attackers);
        int black_control = popcount(black_attackers);
        score += (white_control - black_control) * 5;
    }

    return score * 2; // Python multiplies center control by 2
}

Score Evaluator::evaluateDevelopment(const Board &board)
{
    Score score = 0;

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        int developed = 0;
        int backRank = (c == WHITE) ? 0 : 7;

        // Knights developed (not on back rank)
        Bitboard knights = board.getPieces(c, KNIGHT);
        while (knights)
        {
            Square sq = popLsb(knights);
            if (rankOf(sq) != backRank)
                developed++;
        }

        // Bishops developed (not on back rank)
        Bitboard bishops = board.getPieces(c, BISHOP);
        while (bishops)
        {
            Square sq = popLsb(bishops);
            if (rankOf(sq) != backRank)
                developed++;
        }

        // +15 per developed piece (will be multiplied by 2 in evaluateOpeningPrinciples)
        score += sign * developed * 15;
    }

    return score * 2; // Python multiplies development by 2
}

Score Evaluator::evaluateCastlingRights(const Board &board)
{
    Score score = 0;

    // Bonus for having castling rights
    if (board.getCastlingRights() & (WHITE_OO | WHITE_OOO))
        score += 30;
    if (board.getCastlingRights() & (BLACK_OO | BLACK_OOO))
        score -= 30;

    return score;
}

Score Evaluator::evaluateEarlyQueen(const Board &board)
{
    // Only check in first 10 moves
    if (board.getFullMoveNumber() > 10)
        return 0;

    Score score = 0;

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        int backRank = (c == WHITE) ? 0 : 7;

        Bitboard queens = board.getPieces(c, QUEEN);
        while (queens)
        {
            Square sq = popLsb(queens);
            if (rankOf(sq) != backRank)
            {
                // Queen moved from back rank early = bad (-20)
                score += sign * (-20);
            }
        }
    }

    return score;
}

// ============================================================================
// NEW: Endgame Evaluation
// ============================================================================

Score Evaluator::evaluateEndgame(const Board &board)
{
    int totalPieces = popcount(board.getAllOccupied());

    // Not endgame yet
    if (totalPieces > 10)
        return 0;

    Score score = 0;

    // King activity in endgame
    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        Square kingSq = board.getKingSquare(c);

        // Centralized king is good in endgame
        int file = fileOf(kingSq);
        int rank = rankOf(kingSq);
        int centerDist = std::abs(file - 3) + std::abs(file - 4) +
                         std::abs(rank - 3) + std::abs(rank - 4);

        // Closer to center = better
        score += sign * (14 - centerDist) * 5;
    }

    return score;
}

Score Evaluator::evaluateRookOnOpenFile(const Board &board)
{
    Score score = 0;

    for (Color c : {WHITE, BLACK})
    {
        int sign = (c == WHITE) ? 1 : -1;
        Bitboard rooks = board.getPieces(c, ROOK);

        while (rooks)
        {
            Square sq = popLsb(rooks);
            int file = fileOf(sq);
            Bitboard fileBoard = 0x0101010101010101ULL << file;

            // Check if file is open (no pawns)
            bool open = !(board.getPieces(WHITE, PAWN) & fileBoard) &&
                        !(board.getPieces(BLACK, PAWN) & fileBoard);

            // Check if semi-open (no own pawns)
            bool semiOpen = !(board.getPieces(c, PAWN) & fileBoard);

            if (open)
                score += sign * 25; // Rook on open file
            else if (semiOpen)
                score += sign * 15; // Rook on semi-open file
        }
    }

    return score;
}

// ============================================================================
// DEBUG: Detailed Evaluation Breakdown
// ============================================================================

Evaluator::EvalBreakdown Evaluator::evaluateDetailed(const Board &board)
{
    EvalBreakdown breakdown;

    // Calculate each component
    breakdown.material = evaluateMaterial(board);
    breakdown.pst = evaluatePosition(board);
    breakdown.pawnStructure = evaluatePawnStructure(board);
    breakdown.kingSafety = evaluateKingSafety(board);
    breakdown.mobility = evaluateMobility(board);
    breakdown.threats = evaluateThreats(board);
    breakdown.openingPrinciples = evaluateOpeningPrinciples(board);
    breakdown.endgame = evaluateEndgame(board);
    breakdown.rooksOnOpenFile = evaluateRookOnOpenFile(board);

    // Total (from white's perspective, before flipping for side to move)
    Score total = breakdown.material + breakdown.pst + breakdown.pawnStructure +
                  breakdown.kingSafety + breakdown.mobility + breakdown.threats +
                  breakdown.openingPrinciples + breakdown.endgame + breakdown.rooksOnOpenFile;

    // Flip for side to move
    Color side = board.getSideToMove();
    breakdown.total = (side == WHITE) ? total : -total;

    return breakdown;
}
