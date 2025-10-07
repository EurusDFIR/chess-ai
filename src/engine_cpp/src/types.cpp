#include "types.h"
#include <sstream>
#include <cctype>

// Move to UCI notation
std::string Move::toUCI() const
{
    if (isNull())
        return "0000";

    std::string uci;

    // From square
    int fromFile = fileOf(from());
    int fromRank = rankOf(from());
    uci += char('a' + fromFile);
    uci += char('1' + fromRank);

    // To square
    int toFile = fileOf(to());
    int toRank = rankOf(to());
    uci += char('a' + toFile);
    uci += char('1' + toRank);

    // Promotion
    if (isPromotion())
    {
        uint8_t f = flags();
        switch (f & 0x3)
        { // Get promotion piece type
        case 0:
            uci += 'n';
            break; // Knight
        case 1:
            uci += 'b';
            break; // Bishop
        case 2:
            uci += 'r';
            break; // Rook
        case 3:
            uci += 'q';
            break; // Queen
        }
    }

    return uci;
}

// Parse UCI notation to Move
Move Move::fromUCI(const std::string &uci)
{
    if (uci.length() < 4)
        return Move();

    // Parse from square
    int fromFile = uci[0] - 'a';
    int fromRank = uci[1] - '1';
    if (fromFile < 0 || fromFile > 7 || fromRank < 0 || fromRank > 7)
        return Move();
    Square from = makeSquare(fromFile, fromRank);

    // Parse to square
    int toFile = uci[2] - 'a';
    int toRank = uci[3] - '1';
    if (toFile < 0 || toFile > 7 || toRank < 0 || toRank > 7)
        return Move();
    Square to = makeSquare(toFile, toRank);

    // Parse promotion
    uint8_t flags = QUIET;
    if (uci.length() == 5)
    {
        char promo = std::tolower(uci[4]);
        switch (promo)
        {
        case 'n':
            flags = KNIGHT_PROMOTION;
            break;
        case 'b':
            flags = BISHOP_PROMOTION;
            break;
        case 'r':
            flags = ROOK_PROMOTION;
            break;
        case 'q':
            flags = QUEEN_PROMOTION;
            break;
        default:
            return Move();
        }
    }

    return Move(from, to, flags);
}
