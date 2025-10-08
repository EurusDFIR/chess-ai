#ifndef EVALUATION_H
#define EVALUATION_H

#include "types.h"
#include "board.h"

class Evaluator
{
public:
    // Debug: Evaluation breakdown
    struct EvalBreakdown
    {
        Score material;
        Score pst;
        Score pawnStructure;
        Score kingSafety;
        Score mobility;
        Score threats;
        Score openingPrinciples;
        Score endgame;
        Score rooksOnOpenFile;
        Score total;
    };

    // Main evaluation function
    static Score evaluate(const Board &board);

    // Debug: Detailed evaluation
    static EvalBreakdown evaluateDetailed(const Board &board);

private:
    // Component evaluations
    static Score evaluateMaterial(const Board &board);
    static Score evaluatePosition(const Board &board);
    static Score evaluatePawnStructure(const Board &board);
    static Score evaluateKingSafety(const Board &board);
    static Score evaluateMobility(const Board &board);
    static Score evaluateThreats(const Board &board);

    // NEW: Opening principles (from Python v2.3.0)
    static Score evaluateOpeningPrinciples(const Board &board);
    static Score evaluateCenterControl(const Board &board);
    static Score evaluateDevelopment(const Board &board);
    static Score evaluateCastlingRights(const Board &board);
    static Score evaluateEarlyQueen(const Board &board);

    // NEW: Endgame evaluation
    static Score evaluateEndgame(const Board &board);
    static Score evaluateRookOnOpenFile(const Board &board);

    // Game phase detection
    static int getGamePhase(const Board &board);
    static Score interpolateScore(Score mg, Score eg, int phase);

    // Piece-Square Tables (PST)
    // Indexed by [square] for white (flip vertically for black)

    // Pawn PST
    static constexpr Score PAWN_PST_MG[64] = {
        0, 0, 0, 0, 0, 0, 0, 0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5, 5, 10, 25, 25, 10, 5, 5,
        0, 0, 0, 20, 20, 0, 0, 0,
        5, -5, -10, 0, 0, -10, -5, 5,
        5, 10, 10, -20, -20, 10, 10, 5,
        0, 0, 0, 0, 0, 0, 0, 0};

    static constexpr Score PAWN_PST_EG[64] = {
        0, 0, 0, 0, 0, 0, 0, 0,
        80, 80, 80, 80, 80, 80, 80, 80,
        50, 50, 50, 50, 50, 50, 50, 50,
        30, 30, 30, 30, 30, 30, 30, 30,
        20, 20, 20, 20, 20, 20, 20, 20,
        10, 10, 10, 10, 10, 10, 10, 10,
        10, 10, 10, 10, 10, 10, 10, 10,
        0, 0, 0, 0, 0, 0, 0, 0};

    // Knight PST
    static constexpr Score KNIGHT_PST_MG[64] = {
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50};

    static constexpr Score KNIGHT_PST_EG[64] = {
        -50, -40, -30, -30, -30, -30, -40, -50,
        -40, -20, 0, 0, 0, 0, -20, -40,
        -30, 0, 10, 15, 15, 10, 0, -30,
        -30, 5, 15, 20, 20, 15, 5, -30,
        -30, 0, 15, 20, 20, 15, 0, -30,
        -30, 5, 10, 15, 15, 10, 5, -30,
        -40, -20, 0, 5, 5, 0, -20, -40,
        -50, -40, -30, -30, -30, -30, -40, -50};

    // Bishop PST
    static constexpr Score BISHOP_PST_MG[64] = {
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20};

    static constexpr Score BISHOP_PST_EG[64] = {
        -20, -10, -10, -10, -10, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 10, 10, 5, 0, -10,
        -10, 5, 5, 10, 10, 5, 5, -10,
        -10, 0, 10, 10, 10, 10, 0, -10,
        -10, 10, 10, 10, 10, 10, 10, -10,
        -10, 5, 0, 0, 0, 0, 5, -10,
        -20, -10, -10, -10, -10, -10, -10, -20};

    // Rook PST
    static constexpr Score ROOK_PST_MG[64] = {
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0};

    static constexpr Score ROOK_PST_EG[64] = {
        0, 0, 0, 0, 0, 0, 0, 0,
        5, 10, 10, 10, 10, 10, 10, 5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        -5, 0, 0, 0, 0, 0, 0, -5,
        0, 0, 0, 5, 5, 0, 0, 0};

    // Queen PST - FIXED: Penalty for early development (Python v2.3.0)
    static constexpr Score QUEEN_PST_MG[64] = {
        -20, -10, -10, -5, -5, -10, -10, -20,   // Rank 1: back rank OK
        -10, -20, -20, -20, -20, -20, -20, -10, // Rank 2: penalty -20
        -10, -20, -10, -10, -10, -10, -20, -10, // Rank 3: penalty -20/-10
        -5, -10, -5, 0, 0, -5, -10, -5,         // Rank 4: penalty -10/-5
        0, -5, 0, 5, 5, 0, -5, 0,               // Rank 5: slight bonus
        -10, -5, 0, 5, 5, 0, -5, -10,           // Rank 6: average
        -10, -10, -5, 0, 0, -5, -10, -10,       // Rank 7: penalty
        -20, -10, -10, -5, -5, -10, -10, -20};  // Rank 8: back rank OK

    static constexpr Score QUEEN_PST_EG[64] = {
        -20, -10, -10, -5, -5, -10, -10, -20,
        -10, 0, 0, 0, 0, 0, 0, -10,
        -10, 0, 5, 5, 5, 5, 0, -10,
        -5, 0, 5, 5, 5, 5, 0, -5,
        0, 0, 5, 5, 5, 5, 0, -5,
        -10, 5, 5, 5, 5, 5, 0, -10,
        -10, 0, 5, 0, 0, 0, 0, -10,
        -20, -10, -10, -5, -5, -10, -10, -20};

    // King PST
    static constexpr Score KING_PST_MG[64] = {
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
        20, 20, 0, 0, 0, 0, 20, 20,
        20, 30, 10, 0, 0, 10, 30, 20};

    static constexpr Score KING_PST_EG[64] = {
        -50, -40, -30, -20, -20, -30, -40, -50,
        -30, -20, -10, 0, 0, -10, -20, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 30, 40, 40, 30, -10, -30,
        -30, -10, 20, 30, 30, 20, -10, -30,
        -30, -30, 0, 0, 0, 0, -30, -30,
        -50, -30, -30, -30, -30, -30, -30, -50};

    // Helper: Get PST value for a piece
    static Score getPSTValue(PieceType pt, Square sq, Color c, int phase);
    static Square flipSquare(Square sq) { return Square(sq ^ 56); }
};

#endif // EVALUATION_H
