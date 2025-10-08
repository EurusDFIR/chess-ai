#ifndef SEARCH_H
#define SEARCH_H

#include "types.h"
#include "board.h"
#include "transposition.h"
#include <chrono>
#include <atomic>

// Search statistics
struct SearchStats
{
    uint64_t nodesSearched;
    uint64_t qNodesSearched;
    uint64_t ttHits;
    uint64_t ttMisses;
    uint64_t betaCutoffs;
    uint64_t firstMoveCutoffs;
    int maxDepthReached;
    double timeElapsed;

    SearchStats() : nodesSearched(0), qNodesSearched(0), ttHits(0), ttMisses(0),
                    betaCutoffs(0), firstMoveCutoffs(0), maxDepthReached(0), timeElapsed(0.0) {}

    void clear()
    {
        nodesSearched = 0;
        qNodesSearched = 0;
        ttHits = 0;
        ttMisses = 0;
        betaCutoffs = 0;
        firstMoveCutoffs = 0;
        maxDepthReached = 0;
        timeElapsed = 0.0;
    }

    double getNodesPerSecond() const
    {
        return timeElapsed > 0 ? (double)nodesSearched / timeElapsed : 0.0;
    }

    double getBranchingFactor() const
    {
        return betaCutoffs > 0 ? (double)firstMoveCutoffs / betaCutoffs : 0.0;
    }
};

// Search limits
struct SearchLimits
{
    int maxDepth;
    int timeLimit; // milliseconds
    uint64_t maxNodes;
    bool infinite;

    SearchLimits() : maxDepth(MAX_PLY), timeLimit(0), maxNodes(0), infinite(false) {}
};

class SearchEngine
{
private:
    TranspositionTable tt;
    SearchStats stats;
    SearchLimits limits;

    std::chrono::steady_clock::time_point startTime;
    std::atomic<bool> stopSearch;

    // Killer moves (2 per ply)
    Move killerMoves[MAX_PLY][2];

    // History heuristic
    int history[2][64][64]; // [color][from][to]

    // PV (Principal Variation)
    Move pvTable[MAX_PLY][MAX_PLY];
    int pvLength[MAX_PLY];

public:
    SearchEngine(size_t ttSizeMB = 256);
    ~SearchEngine() = default;

    // Main search interface
    Move getBestMove(Board &board, int maxDepth = 6, int timeLimit = 5000);

    // Stop search
    void stop() { stopSearch = true; }

    // Get statistics
    const SearchStats &getStats() const { return stats; }
    uint64_t getNodesSearched() const { return stats.nodesSearched; }

    // Clear transposition table
    void clearTT() { tt.clear(); }
    void resizeTT(size_t sizeMB) { tt.resize(sizeMB); }

private:
    // Iterative deepening
    Score iterativeDeepening(Board &board, int maxDepth);

    // Alpha-beta search
    Score alphaBeta(Board &board, int depth, Score alpha, Score beta, bool pvNode, int ply);

    // Quiescence search
    Score quiescence(Board &board, Score alpha, Score beta, int ply);

    // Move ordering
    void orderMoves(Board &board, MoveList &moves, const Move &ttMove, const Move &killer1, const Move &killer2, int ply);
    int scoreMove(const Board &board, const Move &move, const Move &ttMove,
                  const Move &killer1, const Move &killer2);

    // Static Exchange Evaluation
    Score SEE(const Board &board, const Move &move);

    // Pruning techniques
    bool canNullMovePrune(const Board &board, int depth, Score beta);
    Score nullMovePruning(Board &board, int depth, Score beta, int ply);
    bool canFutilityPrune(int depth, Score alpha, Score eval);
    bool canLateMoveReduce(const Move &move, int depth, int moveIndex, bool pvNode);
    int getReduction(int depth, int moveIndex, bool pvNode);

    // NEW: Advanced search techniques (Python v2.4.0)
    bool isSingularMove(Board &board, const Move &ttMove, Score ttScore, int depth, int ply, Score beta);
    bool tryMultiCut(Board &board, int depth, Score beta, int ply);
    Move doInternalIterativeDeepening(Board &board, int depth, Score alpha, Score beta, int ply);
    bool tryProbCut(Board &board, int depth, Score beta, int ply, Score &probcutScore);

    // Time management
    bool shouldStop();
    int getElapsedTime() const;

    // Helper functions
    void updateKillerMoves(const Move &move, int ply);
    void updateHistory(Color c, const Move &move, int depth);
    void clearKillerMoves();
    void clearHistory();
    void storePV(const Move &move, int ply);

    // Mate score adjustment
    Score scoreToTT(Score score, int ply);
    Score scoreFromTT(Score score, int ply);
    bool isMateScore(Score score) { return abs(score) >= SCORE_MATE - MAX_PLY; }
};

#endif // SEARCH_H
