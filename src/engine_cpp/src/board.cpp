#include "board.h"
#include "movegen.h"
#include <random>
#include <sstream>
#include <iostream>

// Zobrist keys initialization
uint64_t Zobrist::psq[2][7][64];
uint64_t Zobrist::enpassant[8];
uint64_t Zobrist::castling[16];
uint64_t Zobrist::sideToMove;

void Zobrist::init()
{
    std::mt19937_64 rng(0x1234567890ABCDEFULL);

    // Initialize piece-square keys
    for (int c = 0; c < 2; c++)
    {
        for (int pt = 0; pt < 7; pt++)
        {
            for (int sq = 0; sq < 64; sq++)
            {
                psq[c][pt][sq] = rng();
            }
        }
    }

    // En passant keys
    for (int f = 0; f < 8; f++)
    {
        enpassant[f] = rng();
    }

    // Castling keys
    for (int cr = 0; cr < 16; cr++)
    {
        castling[cr] = rng();
    }

    // Side to move
    sideToMove = rng();
}

// Board constructor
Board::Board()
{
    // Initialize Zobrist keys if not done
    static bool zobristInit = false;
    if (!zobristInit)
    {
        Zobrist::init();
        AttackTables::init();
        zobristInit = true;
    }

    // Clear board
    for (int c = 0; c < 3; c++)
        occupied[c] = 0;
    for (int c = 0; c < 2; c++)
    {
        for (int pt = 0; pt < 7; pt++)
        {
            pieces[c][pt] = 0;
        }
    }
    for (int sq = 0; sq < 64; sq++)
    {
        pieceTypes[sq] = NO_PIECE_TYPE;
        pieceColors[sq] = NO_COLOR;
    }

    sideToMove = WHITE;
    castlingRights = NO_CASTLING;
    enPassantSquare = NO_SQUARE;
    halfMoveClock = 0;
    fullMoveNumber = 1;
    hash = 0;
}

// Initialize starting position
void Board::initStartPosition()
{
    fromFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
}

// Parse FEN string
bool Board::fromFEN(const std::string &fen)
{
    // Clear board first
    for (int c = 0; c < 3; c++)
        occupied[c] = 0;
    for (int c = 0; c < 2; c++)
    {
        for (int pt = 0; pt < 7; pt++)
        {
            pieces[c][pt] = 0;
        }
    }
    for (int sq = 0; sq < 64; sq++)
    {
        pieceTypes[sq] = NO_PIECE_TYPE;
        pieceColors[sq] = NO_COLOR;
    }
    history.clear();

    std::istringstream ss(fen);
    std::string token;

    // Parse piece placement
    ss >> token;
    int sq = A8;
    for (char c : token)
    {
        if (c == '/')
        {
            sq -= 16; // Move to next rank
        }
        else if (c >= '1' && c <= '8')
        {
            sq += (c - '0'); // Empty squares
        }
        else
        {
            // Place piece
            Color color = std::isupper(c) ? WHITE : BLACK;
            PieceType pt;

            switch (std::tolower(c))
            {
            case 'p':
                pt = PAWN;
                break;
            case 'n':
                pt = KNIGHT;
                break;
            case 'b':
                pt = BISHOP;
                break;
            case 'r':
                pt = ROOK;
                break;
            case 'q':
                pt = QUEEN;
                break;
            case 'k':
                pt = KING;
                break;
            default:
                return false;
            }

            putPiece(color, pt, Square(sq));
            sq++;
        }
    }

    // Parse side to move
    ss >> token;
    sideToMove = (token == "w") ? WHITE : BLACK;

    // Parse castling rights
    ss >> token;
    castlingRights = NO_CASTLING;
    if (token.find('K') != std::string::npos)
        castlingRights |= WHITE_OO;
    if (token.find('Q') != std::string::npos)
        castlingRights |= WHITE_OOO;
    if (token.find('k') != std::string::npos)
        castlingRights |= BLACK_OO;
    if (token.find('q') != std::string::npos)
        castlingRights |= BLACK_OOO;

    // Parse en passant
    ss >> token;
    if (token != "-")
    {
        int file = token[0] - 'a';
        int rank = token[1] - '1';
        enPassantSquare = makeSquare(file, rank);
    }
    else
    {
        enPassantSquare = NO_SQUARE;
    }

    // Parse halfmove clock
    if (ss >> token)
        halfMoveClock = std::stoi(token);
    else
        halfMoveClock = 0;

    // Parse fullmove number
    if (ss >> token)
        fullMoveNumber = std::stoi(token);
    else
        fullMoveNumber = 1;

    // Calculate hash
    hash = 0;
    for (int sq = 0; sq < 64; sq++)
    {
        if (pieceTypes[sq] != NO_PIECE_TYPE)
        {
            hash ^= Zobrist::psq[pieceColors[sq]][pieceTypes[sq]][sq];
        }
    }
    hash ^= Zobrist::castling[castlingRights];
    if (enPassantSquare != NO_SQUARE)
    {
        hash ^= Zobrist::enpassant[fileOf(enPassantSquare)];
    }
    if (sideToMove == BLACK)
    {
        hash ^= Zobrist::sideToMove;
    }

    return true;
}

// Convert to FEN
std::string Board::toFEN() const
{
    std::ostringstream fen;

    // Piece placement
    for (int rank = 7; rank >= 0; rank--)
    {
        int empty = 0;
        for (int file = 0; file < 8; file++)
        {
            Square sq = makeSquare(file, rank);

            if (isEmpty(sq))
            {
                empty++;
            }
            else
            {
                if (empty > 0)
                {
                    fen << empty;
                    empty = 0;
                }

                Color c = pieceColorAt(sq);
                PieceType pt = pieceTypeAt(sq);

                char piece;
                switch (pt)
                {
                case PAWN:
                    piece = 'p';
                    break;
                case KNIGHT:
                    piece = 'n';
                    break;
                case BISHOP:
                    piece = 'b';
                    break;
                case ROOK:
                    piece = 'r';
                    break;
                case QUEEN:
                    piece = 'q';
                    break;
                case KING:
                    piece = 'k';
                    break;
                default:
                    piece = '?';
                    break;
                }

                if (c == WHITE)
                    piece = std::toupper(piece);
                fen << piece;
            }
        }

        if (empty > 0)
            fen << empty;
        if (rank > 0)
            fen << '/';
    }

    // Side to move
    fen << (sideToMove == WHITE ? " w " : " b ");

    // Castling rights
    if (castlingRights == NO_CASTLING)
    {
        fen << '-';
    }
    else
    {
        if (castlingRights & WHITE_OO)
            fen << 'K';
        if (castlingRights & WHITE_OOO)
            fen << 'Q';
        if (castlingRights & BLACK_OO)
            fen << 'k';
        if (castlingRights & BLACK_OOO)
            fen << 'q';
    }
    fen << ' ';

    // En passant
    if (enPassantSquare == NO_SQUARE)
    {
        fen << '-';
    }
    else
    {
        fen << char('a' + fileOf(enPassantSquare));
        fen << char('1' + rankOf(enPassantSquare));
    }
    fen << ' ';

    // Halfmove and fullmove
    fen << halfMoveClock << ' ' << fullMoveNumber;

    return fen.str();
}

// Helper: put piece on square
void Board::putPiece(Color c, PieceType pt, Square sq)
{
    pieces[c][pt] |= bit(sq);
    occupied[c] |= bit(sq);
    pieceTypes[sq] = pt;
    pieceColors[sq] = c;
}

// Helper: clear square
void Board::clearSquare(Square sq)
{
    if (!isEmpty(sq))
    {
        Color c = pieceColors[sq];
        PieceType pt = pieceTypes[sq];

        pieces[c][pt] &= ~bit(sq);
        occupied[c] &= ~bit(sq);
        pieceTypes[sq] = NO_PIECE_TYPE;
        pieceColors[sq] = NO_COLOR;
    }
}

// Helper: move piece
void Board::movePiece(Color c, PieceType pt, Square from, Square to)
{
    pieces[c][pt] &= ~bit(from);
    pieces[c][pt] |= bit(to);
    occupied[c] &= ~bit(from);
    occupied[c] |= bit(to);

    pieceTypes[from] = NO_PIECE_TYPE;
    pieceColors[from] = NO_COLOR;
    pieceTypes[to] = pt;
    pieceColors[to] = c;
}

// Make move (template - needs full implementation)
void Board::makeMove(const Move &move)
{
    // Save state for unmake
    BoardState state;
    state.castlingRights = castlingRights;
    state.enPassantSquare = enPassantSquare;
    state.halfMoveClock = halfMoveClock;
    state.hash = hash;
    state.capturedPiece = NO_PIECE_TYPE;
    history.push_back(state);

    Square from = move.from();
    Square to = move.to();
    PieceType pt = pieceTypeAt(from);
    Color us = sideToMove;

    // Update hash
    hash ^= Zobrist::psq[us][pt][from];
    hash ^= Zobrist::castling[castlingRights];
    if (enPassantSquare != NO_SQUARE)
    {
        hash ^= Zobrist::enpassant[fileOf(enPassantSquare)];
    }

    // Handle capture
    if (!isEmpty(to))
    {
        PieceType captured = pieceTypeAt(to);
        state.capturedPiece = captured;
        clearSquare(to);
        hash ^= Zobrist::psq[~us][captured][to];
        halfMoveClock = 0;
    }
    else
    {
        halfMoveClock++;
    }

    // Move piece
    movePiece(us, pt, from, to);
    hash ^= Zobrist::psq[us][pt][to];

    // Reset en passant
    enPassantSquare = NO_SQUARE;

    // Handle special moves (castling, en passant, promotion)
    // TODO: Implement special move handling

    // Update castling rights
    // TODO: Update based on piece movements

    // Switch side
    sideToMove = ~sideToMove;
    hash ^= Zobrist::sideToMove;
    hash ^= Zobrist::castling[castlingRights];

    if (us == BLACK)
        fullMoveNumber++;
}

// Unmake move
void Board::unmakeMove(const Move &move)
{
    if (history.empty())
        return;

    // Restore state
    BoardState state = history.back();
    history.pop_back();

    castlingRights = state.castlingRights;
    enPassantSquare = state.enPassantSquare;
    halfMoveClock = state.halfMoveClock;
    hash = state.hash;

    // Switch side back
    sideToMove = ~sideToMove;

    Square from = move.from();
    Square to = move.to();
    PieceType pt = pieceTypeAt(to);

    // Move piece back
    movePiece(sideToMove, pt, to, from);

    // Restore captured piece
    if (state.capturedPiece != NO_PIECE_TYPE)
    {
        putPiece(~sideToMove, state.capturedPiece, to);
    }

    // TODO: Handle special moves unmake
}

// Get king square
Square Board::getKingSquare(Color c) const
{
    Bitboard kings = pieces[c][KING];
    return kings ? lsb(kings) : NO_SQUARE;
}

// Check if in check
bool Board::isCheck() const
{
    Square kingSq = getKingSquare(sideToMove);
    return kingSq != NO_SQUARE && isSquareAttacked(kingSq, ~sideToMove);
}

// Check if square is attacked
bool Board::isSquareAttacked(Square sq, Color attackerColor) const
{
    return getAttackers(sq, attackerColor) != 0;
}

// Get attackers of a square
Bitboard Board::getAttackers(Square sq, Color attackerColor) const
{
    Bitboard attackers = 0;
    Bitboard occupied = getAllOccupied();

    // Pawn attacks
    attackers |= AttackTables::getPawnAttacks(~attackerColor, sq) & pieces[attackerColor][PAWN];

    // Knight attacks
    attackers |= AttackTables::getKnightAttacks(sq) & pieces[attackerColor][KNIGHT];

    // King attacks
    attackers |= AttackTables::getKingAttacks(sq) & pieces[attackerColor][KING];

    // Bishop/Queen diagonal attacks
    Bitboard bishops = pieces[attackerColor][BISHOP] | pieces[attackerColor][QUEEN];
    if (bishops)
    {
        Bitboard attacks = AttackTables::getBishopAttacks(sq, occupied);
        attackers |= attacks & bishops;
    }

    // Rook/Queen orthogonal attacks
    Bitboard rooks = pieces[attackerColor][ROOK] | pieces[attackerColor][QUEEN];
    if (rooks)
    {
        Bitboard attacks = AttackTables::getRookAttacks(sq, occupied);
        attackers |= attacks & rooks;
    }

    return attackers;
}

// Print board
void Board::print() const
{
    std::cout << "\n  +---+---+---+---+---+---+---+---+\n";
    for (int rank = 7; rank >= 0; rank--)
    {
        std::cout << (rank + 1) << " |";
        for (int file = 0; file < 8; file++)
        {
            Square sq = makeSquare(file, rank);

            if (isEmpty(sq))
            {
                std::cout << "   |";
            }
            else
            {
                Color c = pieceColorAt(sq);
                PieceType pt = pieceTypeAt(sq);

                char piece;
                switch (pt)
                {
                case PAWN:
                    piece = 'P';
                    break;
                case KNIGHT:
                    piece = 'N';
                    break;
                case BISHOP:
                    piece = 'B';
                    break;
                case ROOK:
                    piece = 'R';
                    break;
                case QUEEN:
                    piece = 'Q';
                    break;
                case KING:
                    piece = 'K';
                    break;
                default:
                    piece = '?';
                    break;
                }

                if (c == BLACK)
                    piece = std::tolower(piece);
                std::cout << ' ' << piece << " |";
            }
        }
        std::cout << "\n  +---+---+---+---+---+---+---+---+\n";
    }
    std::cout << "    a   b   c   d   e   f   g   h\n\n";
    std::cout << "FEN: " << toFEN() << "\n";
}

// Get material count for a color
int Board::getMaterial(Color c) const
{
    int material = 0;
    material += popcount(pieces[c][PAWN]) * 100;
    material += popcount(pieces[c][KNIGHT]) * 320;
    material += popcount(pieces[c][BISHOP]) * 330;
    material += popcount(pieces[c][ROOK]) * 500;
    material += popcount(pieces[c][QUEEN]) * 900;
    return material;
}

// Check for threefold repetition
bool Board::isRepetition() const
{
    if (history.size() < 4)
        return false;

    int count = 1;
    for (int i = (int)history.size() - 2; i >= 0 && i >= (int)history.size() - halfMoveClock - 1; i--)
    {
        if (history[i].hash == hash)
        {
            count++;
            if (count >= 3)
                return true;
        }
    }
    return false;
}

// Check for draw
bool Board::isDraw() const
{
    return halfMoveClock >= 100 || isRepetition() || isInsufficientMaterial();
}

// Make null move
void Board::makeNullMove()
{
    BoardState state;
    state.hash = hash;
    state.castlingRights = castlingRights;
    state.enPassantSquare = enPassantSquare;
    state.halfMoveClock = halfMoveClock;
    history.push_back(state);

    sideToMove = Color(1 - sideToMove);

    if (enPassantSquare != NO_SQUARE)
    {
        enPassantSquare = NO_SQUARE;
    }

    halfMoveClock++;
}

// Unmake null move
void Board::unmakeNullMove()
{
    if (history.empty())
        return;

    const BoardState &state = history.back();
    hash = state.hash;
    castlingRights = state.castlingRights;
    enPassantSquare = state.enPassantSquare;
    halfMoveClock = state.halfMoveClock;

    sideToMove = Color(1 - sideToMove);
    history.pop_back();
}

// Check for checkmate
bool Board::isCheckmate() const
{
    if (!isCheck())
        return false;

    MoveList moves;
    MoveGenerator::generateLegalMoves(*this, moves);
    return moves.size() == 0;
}

// Check for stalemate
bool Board::isStalemate() const
{
    if (isCheck())
        return false;

    MoveList moves;
    MoveGenerator::generateLegalMoves(*this, moves);
    return moves.size() == 0;
}

// Check for insufficient material
bool Board::isInsufficientMaterial() const
{
    // King vs King
    if (popcount(getAllOccupied()) == 2)
        return true;

    // King + minor vs King
    if (popcount(getAllOccupied()) == 3)
    {
        if (pieces[WHITE][KNIGHT] || pieces[BLACK][KNIGHT] ||
            pieces[WHITE][BISHOP] || pieces[BLACK][BISHOP])
        {
            return true;
        }
    }

    // King + Bishop vs King + Bishop (same color bishops)
    if (popcount(getAllOccupied()) == 4 &&
        popcount(pieces[WHITE][BISHOP]) == 1 &&
        popcount(pieces[BLACK][BISHOP]) == 1)
    {
        Bitboard lightSquares = 0x55AA55AA55AA55AAULL;
        bool whiteBishopOnLight = pieces[WHITE][BISHOP] & lightSquares;
        bool blackBishopOnLight = pieces[BLACK][BISHOP] & lightSquares;
        return whiteBishopOnLight == blackBishopOnLight;
    }

    return false;
}
