#include "search.h"
#include "evaluation.h"
#include "movegen.h"
#include <algorithm>
#include <cstring>
#include <iostream>

// Constructor
SearchEngine::SearchEngine(size_t ttSizeMB) : tt(ttSizeMB), stopSearch(false)
{
    clearKillerMoves();
    clearHistory();
}

// Main search interface
Move SearchEngine::getBestMove(Board &board, int maxDepth, int timeLimit)
{
    // Initialize search
    stats.clear();
    stopSearch = false;
    startTime = std::chrono::steady_clock::now();
    limits.maxDepth = maxDepth;
    limits.timeLimit = timeLimit;
    limits.maxNodes = 0;
    limits.infinite = false;

    clearKillerMoves();
    tt.incrementAge();

    // Iterative deepening
    Score score = iterativeDeepening(board, maxDepth);

    // Get best move from PV
    Move bestMove = pvTable[0][0];

    // Calculate statistics
    stats.timeElapsed = getElapsedTime() / 1000.0;

    return bestMove;
}

// Iterative deepening
Score SearchEngine::iterativeDeepening(Board &board, int maxDepth)
{
    Score score = 0;
    Move bestMove;

    for (int depth = 1; depth <= maxDepth; depth++)
    {
        if (shouldStop())
            break;

        pvLength[0] = 0;
        score = alphaBeta(board, depth, -SCORE_INFINITE, SCORE_INFINITE, true, 0);

        if (stopSearch)
            break;

        stats.maxDepthReached = depth;
        bestMove = pvTable[0][0];

        // Print info (optional)
        if (depth >= 3)
        {
            std::cout << "info depth " << depth
                      << " score cp " << score
                      << " nodes " << stats.nodesSearched
                      << " nps " << (int)stats.getNodesPerSecond()
                      << " time " << getElapsedTime()
                      << " pv " << bestMove.toUCI()
                      << std::endl;
        }
    }

    return score;
}

// Alpha-beta search
Score SearchEngine::alphaBeta(Board &board, int depth, Score alpha, Score beta, bool pvNode, int ply)
{
    // Check time
    if ((stats.nodesSearched & 4095) == 0 && shouldStop())
    {
        stopSearch = true;
        return 0;
    }

    // Check for draw
    if (ply > 0)
    {
        if (board.isDraw() || board.isRepetition())
        {
            return SCORE_DRAW;
        }
    }

    // Mate distance pruning
    alpha = std::max(alpha, Score(-SCORE_MATE + ply));
    beta = std::min(beta, Score(SCORE_MATE - ply - 1));
    if (alpha >= beta)
        return alpha;

    // Quiescence search at leaf nodes
    if (depth <= 0)
    {
        return quiescence(board, alpha, beta, ply);
    }

    stats.nodesSearched++;
    bool inCheck = board.isCheck();

    // Transposition table probe
    TTEntry ttEntry;
    bool ttHit = tt.probe(board.getHash(), depth, alpha, beta, ttEntry);

    if (ttHit && !pvNode)
    {
        if (ttEntry.flag == TT_EXACT)
        {
            return scoreFromTT(ttEntry.score, ply);
        }
        else if (ttEntry.flag == TT_ALPHA && ttEntry.score <= alpha)
        {
            return alpha;
        }
        else if (ttEntry.flag == TT_BETA && ttEntry.score >= beta)
        {
            return beta;
        }
    }

    Move ttMove = ttHit ? ttEntry.bestMove : Move();

    // Null move pruning
    if (!pvNode && !inCheck && depth >= 3 && canNullMovePrune(board, depth, beta))
    {
        Score nullScore = nullMovePruning(board, depth, beta, ply);
        if (nullScore >= beta)
        {
            return beta;
        }
    }

    // Internal iterative deepening
    // (Skipped for simplicity)

    // Generate moves
    MoveList moves;
    MoveGenerator::generateLegalMoves(board, moves);

    if (moves.size() == 0)
    {
        return inCheck ? Score(-SCORE_MATE + ply) : SCORE_DRAW;
    }

    // Move ordering
    orderMoves(board, moves, ttMove, killerMoves[ply][0], killerMoves[ply][1], ply);

    // Search moves
    Score bestScore = -SCORE_INFINITE;
    Move bestMove;
    uint8_t ttFlag = TT_ALPHA;
    int moveCount = 0;

    for (const Move &move : moves)
    {
        moveCount++;

        // Futility pruning
        if (!pvNode && !inCheck && depth <= 3 && moveCount > 1)
        {
            if (canFutilityPrune(depth, alpha, Evaluator::evaluate(board)))
            {
                continue;
            }
        }

        // Make move
        board.makeMove(move);

        Score score;
        bool givesCheck = board.isCheck();

        // Late move reductions
        bool reduced = false;
        if (moveCount > 3 && depth >= 3 && !pvNode && !inCheck && !givesCheck)
        {
            if (canLateMoveReduce(move, depth, moveCount, pvNode))
            {
                int reduction = getReduction(depth, moveCount, pvNode);
                score = -alphaBeta(board, depth - 1 - reduction, -alpha - 1, -alpha, false, ply + 1);
                reduced = true;
            }
        }

        // Full search
        if (!reduced || score > alpha)
        {
            if (pvNode && moveCount == 1)
            {
                // PV node - full window
                score = -alphaBeta(board, depth - 1, -beta, -alpha, true, ply + 1);
            }
            else
            {
                // Zero window search
                score = -alphaBeta(board, depth - 1, -alpha - 1, -alpha, false, ply + 1);

                // Re-search if needed
                if (score > alpha && score < beta)
                {
                    score = -alphaBeta(board, depth - 1, -beta, -alpha, true, ply + 1);
                }
            }
        }

        // Unmake move
        board.unmakeMove(move);

        if (stopSearch)
            return 0;

        // Update best score
        if (score > bestScore)
        {
            bestScore = score;
            bestMove = move;

            if (score > alpha)
            {
                alpha = score;
                ttFlag = TT_EXACT;
                storePV(move, ply);

                // Beta cutoff
                if (score >= beta)
                {
                    stats.betaCutoffs++;
                    if (moveCount == 1)
                    {
                        stats.firstMoveCutoffs++;
                    }

                    ttFlag = TT_BETA;

                    // Update killers
                    if (!move.isCapture())
                    {
                        updateKillerMoves(move, ply);
                        updateHistory(board.getSideToMove(), move, depth);
                    }

                    break;
                }
            }
        }
    }

    // Store in transposition table
    tt.store(board.getHash(), bestMove, scoreToTT(bestScore, ply), depth, ttFlag);

    return bestScore;
}

// Quiescence search
Score SearchEngine::quiescence(Board &board, Score alpha, Score beta, int ply)
{
    stats.qNodesSearched++;

    // Stand pat
    Score standPat = Evaluator::evaluate(board);

    if (standPat >= beta)
    {
        return beta;
    }

    if (standPat > alpha)
    {
        alpha = standPat;
    }

    // Delta pruning
    constexpr Score QUEEN_VALUE = 900;
    if (standPat + QUEEN_VALUE + 200 < alpha)
    {
        return alpha;
    }

    // Generate captures
    MoveList moves;
    MoveGenerator::generateCaptures(board, moves);

    // Order captures by MVV-LVA
    // (Simplified - full implementation would sort)

    for (const Move &move : moves)
    {
        // SEE pruning
        if (SEE(board, move) < 0)
        {
            continue;
        }

        // Make move
        board.makeMove(move);
        Score score = -quiescence(board, -beta, -alpha, ply + 1);
        board.unmakeMove(move);

        if (score >= beta)
        {
            return beta;
        }

        if (score > alpha)
        {
            alpha = score;
        }
    }

    return alpha;
}

// Move ordering
void SearchEngine::orderMoves(Board &board, MoveList &moves, const Move &ttMove, const Move &killer1, const Move &killer2, int ply)
{
    if (moves.size() == 0)
        return;

    // Create score array
    int scores[MAX_MOVES];

    for (int i = 0; i < moves.size(); i++)
    {
        scores[i] = scoreMove(board, moves[i], ttMove, killer1, killer2);
    }

    // Simple selection sort (good enough for typical move counts)
    for (int i = 0; i < moves.size() - 1; i++)
    {
        int best = i;
        for (int j = i + 1; j < moves.size(); j++)
        {
            if (scores[j] > scores[best])
            {
                best = j;
            }
        }
        if (best != i)
        {
            std::swap(moves[i], moves[best]);
            std::swap(scores[i], scores[best]);
        }
    }
}

// Score move for ordering
int SearchEngine::scoreMove(const Board &board, const Move &move, const Move &ttMove,
                            const Move &killer1, const Move &killer2)
{
    // TT move
    if (move == ttMove)
    {
        return 1000000;
    }

    // Captures - MVV-LVA
    if (move.isCapture())
    {
        PieceType victim = board.pieceTypeAt(move.to());
        PieceType attacker = board.pieceTypeAt(move.from());
        return 100000 + PIECE_VALUES[victim] * 10 - PIECE_VALUES[attacker];
    }

    // Promotions
    if (move.isPromotion())
    {
        return 90000 + (move.flags() & 0x3) * 1000;
    }

    // Killers
    if (move == killer1)
        return 80000;
    if (move == killer2)
        return 79000;

    // History heuristic
    Color c = board.getSideToMove();
    return history[c][move.from()][move.to()];
}

// Static Exchange Evaluation
Score SearchEngine::SEE(const Board &board, const Move &move)
{
    // Simplified SEE - just check if it's a good capture
    if (!move.isCapture())
        return 0;

    PieceType victim = board.pieceTypeAt(move.to());
    PieceType attacker = board.pieceTypeAt(move.from());

    Score gain = PIECE_VALUES[victim] - PIECE_VALUES[attacker];

    // Simple heuristic: if we're trading up or equal, it's good
    return gain >= 0 ? 100 : gain;
}

// Null move pruning
bool SearchEngine::canNullMovePrune(const Board &board, int depth, Score beta)
{
    // Don't null move if:
    // - In check
    // - In endgame
    // - Previous move was null

    if (board.isCheck())
        return false;

    // Check if we have non-pawn material
    Color us = board.getSideToMove();
    int material = board.getMaterial(us);
    int pawns = popcount(board.getPieces(us, PAWN)) * PIECE_VALUES[PAWN];

    return (material - pawns) > 0;
}

Score SearchEngine::nullMovePruning(Board &board, int depth, Score beta, int ply)
{
    board.makeNullMove();

    // Reduced depth search
    int R = 2 + (depth > 6 ? 1 : 0);
    Score score = -alphaBeta(board, depth - 1 - R, -beta, -beta + 1, false, ply + 1);

    board.unmakeNullMove();

    return score;
}

// Futility pruning
bool SearchEngine::canFutilityPrune(int depth, Score alpha, Score eval)
{
    constexpr Score margins[4] = {0, 200, 300, 500};

    if (depth <= 0 || depth > 3)
        return false;

    return eval + margins[depth] <= alpha;
}

// Late move reductions
bool SearchEngine::canLateMoveReduce(const Move &move, int depth, int moveIndex, bool pvNode)
{
    if (pvNode)
        return false;
    if (move.isCapture())
        return false;
    if (move.isPromotion())
        return false;
    if (depth < 3)
        return false;
    if (moveIndex < 4)
        return false;

    return true;
}

int SearchEngine::getReduction(int depth, int moveIndex, bool pvNode)
{
    // Simple reduction formula
    int reduction = 1;

    if (depth >= 6 && moveIndex >= 8)
    {
        reduction = 2;
    }

    if (pvNode)
    {
        reduction = std::max(0, reduction - 1);
    }

    return reduction;
}

// Time management
bool SearchEngine::shouldStop()
{
    if (stopSearch)
        return true;

    if (limits.infinite)
        return false;

    if (limits.timeLimit > 0)
    {
        int elapsed = getElapsedTime();
        if (elapsed >= limits.timeLimit)
        {
            return true;
        }
    }

    if (limits.maxNodes > 0)
    {
        if (stats.nodesSearched >= limits.maxNodes)
        {
            return true;
        }
    }

    return false;
}

int SearchEngine::getElapsedTime() const
{
    auto now = std::chrono::steady_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(now - startTime);
    return duration.count();
}

// Update killer moves
void SearchEngine::updateKillerMoves(const Move &move, int ply)
{
    if (ply >= MAX_PLY)
        return;

    // Shift killers
    if (killerMoves[ply][0] != move)
    {
        killerMoves[ply][1] = killerMoves[ply][0];
        killerMoves[ply][0] = move;
    }
}

// Update history
void SearchEngine::updateHistory(Color c, const Move &move, int depth)
{
    // Bonus based on depth
    int bonus = depth * depth;

    history[c][move.from()][move.to()] += bonus;

    // Cap history values
    if (history[c][move.from()][move.to()] > 10000)
    {
        // Age all history values
        for (int f = 0; f < 64; f++)
        {
            for (int t = 0; t < 64; t++)
            {
                history[c][f][t] /= 2;
            }
        }
    }
}

// Clear killer moves
void SearchEngine::clearKillerMoves()
{
    for (int ply = 0; ply < MAX_PLY; ply++)
    {
        killerMoves[ply][0] = Move();
        killerMoves[ply][1] = Move();
    }
}

// Clear history
void SearchEngine::clearHistory()
{
    std::memset(history, 0, sizeof(history));
}

// Store PV
void SearchEngine::storePV(const Move &move, int ply)
{
    if (ply >= MAX_PLY)
        return;

    pvTable[ply][0] = move;

    for (int i = 0; i < pvLength[ply + 1]; i++)
    {
        pvTable[ply][i + 1] = pvTable[ply + 1][i];
    }

    pvLength[ply] = pvLength[ply + 1] + 1;
}

// Mate score conversion
Score SearchEngine::scoreToTT(Score score, int ply)
{
    if (score >= SCORE_MATE - MAX_PLY)
    {
        return score + ply;
    }
    else if (score <= -SCORE_MATE + MAX_PLY)
    {
        return score - ply;
    }
    return score;
}

Score SearchEngine::scoreFromTT(Score score, int ply)
{
    if (score >= SCORE_MATE - MAX_PLY)
    {
        return score - ply;
    }
    else if (score <= -SCORE_MATE + MAX_PLY)
    {
        return score + ply;
    }
    return score;
}
