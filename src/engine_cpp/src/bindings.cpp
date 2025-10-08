#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "board.h"
#include "types.h"
#include "movegen.h"
#include "search.h"
#include "evaluation.h"

namespace py = pybind11;

PYBIND11_MODULE(chess_engine, m)
{
     m.doc() = "Fast C++ Chess Engine with bitboards, magic move generation, and advanced search";

     // ========================================================================
     // ENUMS
     // ========================================================================

     py::enum_<PieceType>(m, "PieceType")
         .value("PAWN", PAWN)
         .value("KNIGHT", KNIGHT)
         .value("BISHOP", BISHOP)
         .value("ROOK", ROOK)
         .value("QUEEN", QUEEN)
         .value("KING", KING)
         .value("NO_PIECE_TYPE", NO_PIECE_TYPE)
         .export_values();

     py::enum_<Color>(m, "Color")
         .value("WHITE", WHITE)
         .value("BLACK", BLACK)
         .value("NO_COLOR", NO_COLOR)
         .export_values();

     // ========================================================================
     // MOVE CLASS
     // ========================================================================

     py::class_<Move>(m, "Move")
         .def(py::init<>(), "Create null move")
         .def(py::init<Square, Square>(),
              "Create move from squares",
              py::arg("from_square"),
              py::arg("to_square"))
         .def(py::init<Square, Square, uint8_t>(),
              "Create move with flags",
              py::arg("from_square"),
              py::arg("to_square"),
              py::arg("flags"))

         // Properties
         .def("from_square", &Move::from, "Get from square")
         .def("to_square", &Move::to, "Get to square")
         .def("flags", &Move::flags, "Get move flags")

         // Query methods
         .def("is_capture", &Move::isCapture, "Check if move is capture")
         .def("is_promotion", &Move::isPromotion, "Check if move is promotion")
         .def("is_castling", &Move::isCastling, "Check if move is castling")
         .def("is_en_passant", &Move::isEnPassant, "Check if move is en passant")
         .def("is_null", &Move::isNull, "Check if move is null")

         // UCI conversion
         .def("to_uci", &Move::toUCI, "Convert move to UCI notation")
         .def_static("from_uci", &Move::fromUCI,
                     "Parse UCI string to move",
                     py::arg("uci"))

         // Operators
         .def("__eq__", &Move::operator==)
         .def("__ne__", &Move::operator!=)
         .def("__repr__", [](const Move &m)
              { return "<Move " + m.toUCI() + ">"; });

     // ========================================================================
     // BOARD CLASS
     // ========================================================================

     py::class_<Board>(m, "Board")
         .def(py::init<>(), "Create empty board")

         // Initialization
         .def("init_start_position", &Board::initStartPosition,
              "Initialize to standard chess starting position")
         .def("from_fen", &Board::fromFEN,
              "Set position from FEN string",
              py::arg("fen"))
         .def("to_fen", &Board::toFEN,
              "Get current position as FEN string")

         // Move operations
         .def("make_move", &Board::makeMove,
              "Make a move on the board",
              py::arg("move"))
         .def("unmake_move", &Board::unmakeMove,
              "Unmake the last move",
              py::arg("move"))
         .def("make_null_move", &Board::makeNullMove,
              "Make a null move (pass)")
         .def("unmake_null_move", &Board::unmakeNullMove,
              "Unmake null move")

         // Board queries
         .def("get_side_to_move", &Board::getSideToMove,
              "Get color of side to move")
         .def("get_castling_rights", &Board::getCastlingRights,
              "Get castling rights bitfield")
         .def("get_en_passant_square", &Board::getEnPassantSquare,
              "Get en passant target square")
         .def("get_halfmove_clock", &Board::getHalfMoveClock,
              "Get halfmove clock for 50-move rule")
         .def("get_fullmove_number", &Board::getFullMoveNumber,
              "Get fullmove number")
         .def("get_hash", &Board::getHash,
              "Get Zobrist hash of position")

         // Piece queries
         .def("piece_type_at", &Board::pieceTypeAt,
              "Get piece type at square",
              py::arg("square"))
         .def("piece_color_at", &Board::pieceColorAt,
              "Get piece color at square",
              py::arg("square"))
         .def("is_empty", &Board::isEmpty,
              "Check if square is empty",
              py::arg("square"))
         .def("get_king_square", &Board::getKingSquare,
              "Get king square for color",
              py::arg("color"))

         // Game state checks
         .def("is_check", &Board::isCheck,
              "Check if side to move is in check")
         .def("is_checkmate", &Board::isCheckmate,
              "Check if position is checkmate")
         .def("is_stalemate", &Board::isStalemate,
              "Check if position is stalemate")
         .def("is_draw", &Board::isDraw,
              "Check if position is draw")
         .def("is_repetition", &Board::isRepetition,
              "Check if position is repetition")
         .def("is_insufficient_material", &Board::isInsufficientMaterial,
              "Check for insufficient mating material")

         // Attack queries
         .def("is_square_attacked", &Board::isSquareAttacked,
              "Check if square is attacked by color",
              py::arg("square"),
              py::arg("attacker_color"))

         // Utility
         .def("print", &Board::print,
              "Print board to console")
         .def("get_material", &Board::getMaterial,
              "Get total material value for color",
              py::arg("color"))

         .def("__repr__", [](const Board &b)
              { return "<Board FEN: " + b.toFEN() + ">"; });

     // ========================================================================
     // SEARCH ENGINE
     // ========================================================================

     py::class_<SearchStats>(m, "SearchStats")
         .def_readonly("nodes_searched", &SearchStats::nodesSearched,
                       "Total nodes searched")
         .def_readonly("q_nodes_searched", &SearchStats::qNodesSearched,
                       "Quiescence nodes searched")
         .def_readonly("tt_hits", &SearchStats::ttHits,
                       "Transposition table hits")
         .def_readonly("tt_misses", &SearchStats::ttMisses,
                       "Transposition table misses")
         .def_readonly("beta_cutoffs", &SearchStats::betaCutoffs,
                       "Number of beta cutoffs")
         .def_readonly("first_move_cutoffs", &SearchStats::firstMoveCutoffs,
                       "Beta cutoffs on first move")
         .def_readonly("max_depth_reached", &SearchStats::maxDepthReached,
                       "Maximum depth reached")
         .def_readonly("time_elapsed", &SearchStats::timeElapsed,
                       "Time elapsed in seconds")
         .def("get_nodes_per_second", &SearchStats::getNodesPerSecond,
              "Calculate nodes per second")
         .def("get_branching_factor", &SearchStats::getBranchingFactor,
              "Calculate effective branching factor")
         .def("__repr__", [](const SearchStats &s)
              { return "<SearchStats nodes=" + std::to_string(s.nodesSearched) +
                       " nps=" + std::to_string((int)s.getNodesPerSecond()) + ">"; });

     py::class_<SearchEngine>(m, "SearchEngine")
         .def(py::init<size_t>(),
              "Create search engine",
              py::arg("tt_size_mb") = 256)

         // Main search interface
         .def("get_best_move", &SearchEngine::getBestMove,
              "Search for best move",
              py::arg("board"),
              py::arg("max_depth") = 6,
              py::arg("time_limit") = 5000,
              "Search the position and return best move.\n"
              "Args:\n"
              "    board: Board to search\n"
              "    max_depth: Maximum search depth (default 6)\n"
              "    time_limit: Time limit in milliseconds (default 5000)\n"
              "Returns:\n"
              "    Best move found")

         // Stop search
         .def("stop", &SearchEngine::stop,
              "Stop search immediately")

         // Statistics
         .def("get_stats", &SearchEngine::getStats,
              "Get search statistics",
              py::return_value_policy::reference_internal)
         .def("get_nodes_searched", &SearchEngine::getNodesSearched,
              "Get total nodes searched")

         // TT management
         .def("clear_tt", &SearchEngine::clearTT,
              "Clear transposition table")
         .def("resize_tt", &SearchEngine::resizeTT,
              "Resize transposition table",
              py::arg("size_mb"))

         .def("__repr__", [](const SearchEngine &e)
              { return "<SearchEngine nodes=" +
                       std::to_string(e.getNodesSearched()) + ">"; });

     // ========================================================================
     // EVALUATION
     // ========================================================================

     py::class_<Evaluator::EvalBreakdown>(m, "EvalBreakdown")
         .def_readonly("material", &Evaluator::EvalBreakdown::material)
         .def_readonly("pst", &Evaluator::EvalBreakdown::pst)
         .def_readonly("pawn_structure", &Evaluator::EvalBreakdown::pawnStructure)
         .def_readonly("king_safety", &Evaluator::EvalBreakdown::kingSafety)
         .def_readonly("mobility", &Evaluator::EvalBreakdown::mobility)
         .def_readonly("threats", &Evaluator::EvalBreakdown::threats)
         .def_readonly("opening_principles", &Evaluator::EvalBreakdown::openingPrinciples)
         .def_readonly("endgame", &Evaluator::EvalBreakdown::endgame)
         .def_readonly("rooks_on_open_file", &Evaluator::EvalBreakdown::rooksOnOpenFile)
         .def_readonly("total", &Evaluator::EvalBreakdown::total)
         .def("__repr__", [](const Evaluator::EvalBreakdown &e)
              { return "<EvalBreakdown total=" + std::to_string(e.total) + "cp>"; });

     py::class_<Evaluator>(m, "Evaluator")
         .def_static("evaluate", &Evaluator::evaluate,
                     "Evaluate position from side to move perspective",
                     py::arg("board"),
                     "Returns evaluation score in centipawns")
         .def_static("evaluate_detailed", &Evaluator::evaluateDetailed,
                     "Get detailed evaluation breakdown",
                     py::arg("board"),
                     "Returns EvalBreakdown with component scores");

     // ========================================================================
     // MOVE GENERATION
     // ========================================================================

     py::class_<MoveList>(m, "MoveList")
         .def(py::init<>())
         .def("size", &MoveList::size, "Get number of moves")
         .def("__len__", &MoveList::size)
         .def("__getitem__", [](const MoveList &ml, int i)
              {
            if (i < 0 || i >= ml.size()) {
                throw py::index_error("Move list index out of range");
            }
            return ml[i]; })
         .def("__iter__", [](const MoveList &ml)
              { return py::make_iterator(ml.begin(), ml.end()); }, py::keep_alive<0, 1>())
         .def("__repr__", [](const MoveList &ml)
              { return "<MoveList size=" + std::to_string(ml.size()) + ">"; });

     py::class_<MoveGenerator>(m, "MoveGenerator")
         .def_static("generate_legal_moves", &MoveGenerator::generateLegalMoves,
                     "Generate all legal moves",
                     py::arg("board"),
                     py::arg("moves"))
         .def_static("generate_captures", &MoveGenerator::generateCaptures,
                     "Generate capture moves only",
                     py::arg("board"),
                     py::arg("moves"))
         .def_static("is_legal", &MoveGenerator::isLegal,
                     "Check if move is legal",
                     py::arg("board"),
                     py::arg("move"));

     // ========================================================================
     // CONSTANTS
     // ========================================================================

     m.attr("SCORE_INFINITE") = SCORE_INFINITE;
     m.attr("SCORE_MATE") = SCORE_MATE;
     m.attr("SCORE_DRAW") = SCORE_DRAW;

     // Piece values
     m.attr("PAWN_VALUE") = PIECE_VALUES[PAWN];
     m.attr("KNIGHT_VALUE") = PIECE_VALUES[KNIGHT];
     m.attr("BISHOP_VALUE") = PIECE_VALUES[BISHOP];
     m.attr("ROOK_VALUE") = PIECE_VALUES[ROOK];
     m.attr("QUEEN_VALUE") = PIECE_VALUES[QUEEN];
     m.attr("KING_VALUE") = PIECE_VALUES[KING];

     // ========================================================================
     // HELPER FUNCTIONS
     // ========================================================================

     m.def("init_tables", []()
           {
        AttackTables::init();
        Zobrist::init(); }, "Initialize attack tables and zobrist keys");

     m.def("square_to_string", [](Square sq) -> std::string
           {
        if (sq == NO_SQUARE) return "-";
        char file = 'a' + fileOf(sq);
        char rank = '1' + rankOf(sq);
        return std::string(1, file) + std::string(1, rank); }, "Convert square to algebraic notation", py::arg("square"));

     m.def("string_to_square", [](const std::string &str) -> Square
           {
        if (str == "-" || str.length() < 2) return NO_SQUARE;
        int file = str[0] - 'a';
        int rank = str[1] - '1';
        if (file < 0 || file > 7 || rank < 0 || rank > 7) return NO_SQUARE;
        return makeSquare(file, rank); }, "Convert algebraic notation to square", py::arg("notation"));

     // Version info
     m.attr("__version__") = "2.0.0";
     m.attr("__author__") = "Chess AI Team";
}
